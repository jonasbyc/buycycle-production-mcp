#!/usr/bin/env python3
"""
Simple entry point for MCP Inspector testing.
This file runs our Buycycle MCP server with absolute imports.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import our modules with absolute imports
from server.data_loader import data_loader
from server.validators import validator
from server.tools import step1_tools, step2_tools, step3_tools, step4_tools, step5_tools, step6_tools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the main MCP server
server = Server("buycycle-listing-mcp")

@server.list_tools()
async def handle_list_tools():
    """List all available tools for the Buycycle listing process."""
    return [
        # Step 1 Tools
        {
            "name": "list_bike_types",
            "description": "Get all available bike types with descriptions",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "list_brands",
            "description": "Get all available bike brands",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of brands to return", "default": 50}
                },
                "required": []
            }
        },
        {
            "name": "validate_step1_selection",
            "description": "Validate Step 1 selections (bike type, brand, and model)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Selected bike type"},
                    "brand_id": {"type": "string", "description": "Selected brand"},
                    "model_id": {"type": "string", "description": "Selected model"}
                },
                "required": ["bike_type_id", "brand_id", "model_id"]
            }
        },
        # Step 2 Tools
        {
            "name": "get_step2_detail_options",
            "description": "Get all available detail options for Step 2 based on bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get options for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "validate_bike_details",
            "description": "Validate bike details for Step 2",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type these details are for"},
                    "details": {
                        "type": "object",
                        "description": "Dictionary of bike details to validate",
                        "additionalProperties": True
                    }
                },
                "required": ["bike_type_id", "details"]
            }
        },
        # Step 3 Tools
        {
            "name": "list_countries",
            "description": "Get all supported countries for bike listings",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "validate_location",
            "description": "Validate Step 3 location and shipping information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "Selected country code"},
                    "city": {"type": "string", "description": "Selected city"},
                    "postal_code": {"type": "string", "description": "Postal/ZIP code"},
                    "shipping_options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Selected shipping method IDs"
                    }
                },
                "required": ["country_code", "city", "postal_code", "shipping_options"]
            }
        }
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool calls by routing to appropriate tool functions."""
    try:
        # Step 1 tools
        if name == "list_bike_types":
            return await step1_tools.list_bike_types()
        elif name == "list_brands":
            limit = arguments.get("limit", 50)
            return await step1_tools.list_brands(limit)
        elif name == "validate_step1_selection":
            return await step1_tools.validate_step1_selection(
                arguments["bike_type_id"], arguments["brand_id"], arguments["model_id"]
            )
        # Step 2 tools
        elif name == "get_step2_detail_options":
            return await step2_tools.get_step2_detail_options(arguments["bike_type_id"])
        elif name == "validate_bike_details":
            return await step2_tools.validate_bike_details(
                arguments["bike_type_id"], arguments["details"]
            )
        # Step 3 tools
        elif name == "list_countries":
            return await step3_tools.list_countries()
        elif name == "validate_location":
            return await step3_tools.validate_location(
                arguments["country_code"], arguments["city"],
                arguments["postal_code"], arguments["shipping_options"]
            )
        else:
            return {
                "success": False,
                "error": {"code": "UNKNOWN_TOOL", "message": f"Tool '{name}' not found"}
            }

    except Exception as e:
        logger.error(f"Error handling tool call '{name}': {e}")
        return {
            "success": False,
            "error": {"code": "TOOL_EXECUTION_ERROR", "message": str(e)}
        }

async def main():
    """Main entry point for the MCP server."""
    try:
        # Load all data at startup
        logger.info("Starting Buycycle Listing MCP Server...")
        await data_loader.load_all()
        logger.info("Data loading complete. Server ready.")

        # Run the server
        await stdio_server(server)

    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())