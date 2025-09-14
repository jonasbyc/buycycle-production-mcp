#!/usr/bin/env python3
"""
ASGI HTTP server wrapper for the Buycycle Listing MCP Server.
This file makes the stdio-based MCP server compatible with HTTP environments like FastMCP.
"""
import logging
from fastapi import FastAPI, Request, Response
from server.main import server as mcp_server
from server.data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a FastAPI app to wrap the MCP server
app = FastAPI(
    title="Buycycle Listing MCP Server",
    description="An HTTP wrapper for the Buycycle MCP server.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Load all necessary data when the server starts."""
    try:
        logger.info("Loading optimized production data for HTTP server...")
        await data_loader.load_all_optimized()
        brand_count = len(data_loader.get_brands())
        bike_type_count = len(data_loader.get_bike_types())
        component_count = len(data_loader.get_components())
        logger.info(f"Production data loaded: {brand_count} brands, {bike_type_count} bike types, {component_count} components")
    except Exception as e:
        logger.error(f"Fatal error during data loading: {e}", exc_info=True)
        raise

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """
    Handle raw MCP protocol requests over HTTP POST.
    This endpoint simulates the stdio transport over HTTP.
    """
    try:
        # Get raw body as bytes
        request_data = await request.body()
        
        # Process the request using the MCP server's raw protocol handler
        response_data = await mcp_server.handle_request(request_data)
        
        # Return the response
        if response_data:
            return Response(content=response_data, media_type="application/octet-stream")
        else:
            # If there's no response, return a 204 No Content
            return Response(status_code=204)
            
    except Exception as e:
        logger.error(f"Error processing MCP request: {e}", exc_info=True)
        return Response(status_code=500, content=f"Internal Server Error: {e}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

# The 'app' object is the ASGI application for FastMCP.
