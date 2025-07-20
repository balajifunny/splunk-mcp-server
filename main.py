# server.py
import httpx
import asyncio
import json
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Create an async MCP server
mcp = FastMCP("SplunkServer")

# Splunk configuration
SPLUNK_HOST = "127.0.0.1"
SPLUNK_PORT = "8089"
SPLUNK_USERNAME = "<your_splunk_username>"
SPLUNK_PASSWORD = "<your_splunk_password>"
SPLUNK_SCHEME = "https"

def get_splunk_base_url() -> str:
    return f"{SPLUNK_SCHEME}://{SPLUNK_HOST}:{SPLUNK_PORT}"

def get_auth() -> tuple:
    return (SPLUNK_USERNAME, SPLUNK_PASSWORD)

def get_httpx_options() -> Dict[str, Any]:
    return {
        "verify": False,  # Change to True in production with valid SSL
        "timeout": 30
    }

# Define supported types
SUPPORTED_TYPES = {
    "saved_searches": "saved/searches",
    "alerts": "saved/searches?search=alert_type=*",
    "field_extractions": "data/props/extractions",
    "field_aliases": "data/props/fieldaliases",
    "calculated_fields": "data/props/fieldtransformations",
    "lookups": "data/lookup-table-files",
    "automatic_lookups": "data/transforms/automatic_lookups",
    "lookup_transforms": "data/transforms/lookups",
    "macros": "data/macros",
    "tags": "data/tags",
    "data_models": "datamodel/model",
    "workflow_actions": "data/ui/workflow-actions",
    "views": "data/ui/views",
    "panels": "data/ui/panels",
    "apps": "apps/local"
}

@mcp.tool("get_knowledge_objects")
async def get_knowledge_objects(type: str, count: int = 100) -> dict:
    """
    Get knowledge objects from Splunk.
    Supported types include saved_searches, lookups, macros, etc.
    """
    try:
        if type not in SUPPORTED_TYPES:
            return {"success": False, "error": f"Unsupported type: {type}"}

        async with httpx.AsyncClient(
            auth=get_auth(),
            base_url=get_splunk_base_url(),
            **get_httpx_options()
        ) as client:
            response = await client.get(
                f"/services/{SUPPORTED_TYPES[type]}",
                params={"output_mode": "json", "count": count}
            )
            response.raise_for_status()
            data = response.json()
            objects = [
                {
                    "name": entry.get("name"),
                    "title": entry["content"].get("label", entry.get("name")),
                    "disabled": entry["content"].get("disabled", False),
                    "app": entry["acl"].get("app"),
                    "owner": entry["acl"].get("owner"),
                }
                for entry in data.get("entry", [])
            ]

            return {
                "success": True,
                "type": type,
                "count": len(objects),
                "objects": objects,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
async def search_splunk(query: str, earliest_time: str = "-1h", latest_time: str = "now", max_count: int = 100) -> Dict[str, Any]:
    """Search Splunk logs with the given query."""
    try:
        async with httpx.AsyncClient(auth=get_auth(), base_url=get_splunk_base_url(), **get_httpx_options()) as client:
            # Step 1: Start a search job
            search_data = {
                'search': f"search {query}",
                'earliest_time': earliest_time,
                'latest_time': latest_time,
                'output_mode': 'json'
            }

            response = await client.post("/services/search/jobs", data=search_data)
            response.raise_for_status()

            job_response = response.json()
            job_id = job_response.get("sid")

            if not job_id:
                return {
                    'success': False,
                    'error': 'Failed to extract job SID',
                    'query': query
                }

            # Step 2: Poll for results
            results_url = f"/services/search/jobs/{job_id}/results"
            results_params = {
                'output_mode': 'json',
                'count': max_count
            }

            for _ in range(30):  # Retry for ~30 seconds
                results_response = await client.get(results_url, params=results_params)
                if results_response.status_code == 200:
                    results = results_response.json()
                    if "results" in results:
                        return {
                            'success': True,
                            'results': results.get('results', []),
                            'query': query,
                            'count': len(results.get('results', []))
                        }
                await asyncio.sleep(1)

            return {
                'success': False,
                'error': 'Search job timeout or no results returned',
                'query': query
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'query': query
        }

@mcp.tool()
async def get_splunk_indexes() -> List[str]:
    """Get list of available Splunk indexes."""
    try:
        async with httpx.AsyncClient(auth=get_auth(), base_url=get_splunk_base_url(), **get_httpx_options()) as client:
            response = await client.get("/services/data/indexes", params={'output_mode': 'json'})
            response.raise_for_status()

            data = response.json()
            indexes = [entry['name'] for entry in data.get('entry', [])]
            return indexes

    except Exception as e:
        return [f"Error retrieving indexes: {str(e)}"]

@mcp.tool()
async def get_log_stats(index: str, time_range: str = "-1h") -> Dict[str, Any]:
    """Get log statistics for a specific index."""
    try:
        query = f"index={index} | stats count by sourcetype"
        return await search_splunk(query, earliest_time=time_range)

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'index': index
        }
    
@mcp.tool("get_all_users")
async def get_all_users() -> str:
    """Fetch all Splunk users."""
    try:
        async with httpx.AsyncClient(auth=get_auth(), base_url=get_splunk_base_url(), **get_httpx_options()) as client:
            response = await client.get("/services/authentication/users?output_mode=json")
            response.raise_for_status()
            users = response.json().get("entry", [])
            usernames = [user["name"] for user in users]
            return json.dumps({"usernames": usernames}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    

@mcp.tool("get_user_info")
async def get_user_info(username: str) -> str:
    """Get detailed information about a specific Splunk user."""
    try:
        async with httpx.AsyncClient(auth=get_auth(), base_url=get_splunk_base_url(), **get_httpx_options()) as client:
            url = f"/services/authentication/users/{username}?output_mode=json"
            response = await client.get(url)
            response.raise_for_status()
            user_info = response.json().get("entry", [{}])[0]
            return json.dumps(user_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)



@mcp.tool()
async def search_errors(index: str = "*", time_range: str = "-1h", max_count: int = 50) -> Dict[str, Any]:
    """Search for error logs across indexes."""
    query = f"index={index} (error OR ERROR OR exception OR Exception OR failed OR FAILED)"
    return await search_splunk(query, earliest_time=time_range, max_count=max_count)

@mcp.resource("splunk://search/{query}")
async def get_search_resource(query: str) -> str:
    """Get Splunk search results as a resource."""
    result = await search_splunk(query)
    return json.dumps(result, indent=2)

@mcp.resource("splunk://indexes")
async def get_indexes_resource() -> str:
    """Get available Splunk indexes as a resource."""
    indexes = await get_splunk_indexes()
    return json.dumps({"indexes": indexes}, indent=2)
