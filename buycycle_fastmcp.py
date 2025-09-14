#!/usr/bin/env python3
"""
Lambda-compatible MCP Server for Buycycle
Simple HTTP server that handles MCP protocol over HTTP
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global data containers - will load lazily
bike_data = {}
_data_loaded = False

def load_bike_data():
    """Load all bike data into memory."""
    global bike_data, _data_loaded
    if _data_loaded:
        return

    logger.info("Loading bike data...")
    try:
        # Data directory
        data_dir = Path(__file__).parent / "data"

        # Load bike types
        with open(data_dir / "bike_types.json", 'r') as f:
            bike_data["bike_types"] = json.load(f)

        # Load brands
        with open(data_dir / "brands.json", 'r') as f:
            bike_data["brands"] = json.load(f)

        # Load models by brand
        with open(data_dir / "models_by_brand.json", 'r') as f:
            bike_data["models_by_brand"] = json.load(f)

        # Load countries
        with open(data_dir / "countries.json", 'r') as f:
            bike_data["countries"] = json.load(f)

        logger.info(f"Loaded data: {len(bike_data['brands'])} brands, {len(bike_data['countries'])} countries")
        _data_loaded = True

    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise

# Create FastAPI app
app = FastAPI(title="Buycycle MCP Server", version="1.0.0")

@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint for Lambda Web Adapter"""
    return {"status": "ok", "service": "buycycle-mcp-server"}

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """Handle MCP protocol requests"""
    load_bike_data()  # Load data on first request

    try:
        # Get the request data
        data = await request.json()

        # Handle MCP protocol
        if data.get("method") == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "list_bike_types",
                            "description": "Get all available bike types",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "list_brands",
                            "description": "Get available bike brands",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "limit": {"type": "integer", "default": 20}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "list_countries",
                            "description": "Get supported countries",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            })

        elif data.get("method") == "tools/call":
            tool_name = data.get("params", {}).get("name")
            arguments = data.get("params", {}).get("arguments", {})

            if tool_name == "list_bike_types":
                bike_types = []
                for type_id, type_info in bike_data["bike_types"].items():
                    bike_types.append({
                        "id": type_id,
                        "name": type_info["name"],
                        "description": type_info["description"],
                        "category": type_info["category"]
                    })

                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "success": True,
                                "data": {
                                    "bike_types": bike_types,
                                    "total_count": len(bike_types)
                                }
                            })
                        }]
                    }
                })

            elif tool_name == "list_brands":
                limit = arguments.get("limit", 20)
                brands = []
                for brand_id, brand_info in list(bike_data["brands"].items())[:limit]:
                    brands.append({
                        "id": brand_id,
                        "name": brand_info["name"]
                    })

                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "success": True,
                                "data": {
                                    "brands": brands,
                                    "total_count": len(brands)
                                }
                            })
                        }]
                    }
                })

            elif tool_name == "list_countries":
                countries = []
                for country_code, country_info in bike_data["countries"].items():
                    countries.append({
                        "code": country_code,
                        "name": country_info["name"]
                    })

                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps({
                                "success": True,
                                "data": {
                                    "countries": countries,
                                    "total_count": len(countries)
                                }
                            })
                        }]
                    }
                })

            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                })

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {data.get('method')}"
                }
            })

    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": data.get("id") if "data" in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })