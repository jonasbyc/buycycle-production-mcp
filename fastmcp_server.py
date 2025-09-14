#!/usr/bin/env python3
"""
Entry point for running the Buycycle Listing MCP Server on FastMCP.
This file adapts the server for a serverless ASGI environment.
"""
import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
# This allows for absolute imports from the 'server' module
sys.path.insert(0, str(Path(__file__).parent))

from server.main import server as app
from server.data_loader import data_loader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for a specific environment variable to confirm it's a serverless environment
# This helps prevent accidental direct execution of this file in a local environment
if os.getenv("IS_SERVERLESS") == "true":
    logger.info("Serverless environment detected - FastMCP will handle execution")

@app.on_event("startup")
async def startup_event():
    """
    Asynchronous event handler that loads all necessary data when the server starts.
    This is the serverless-compatible way to perform initialization tasks.
    """
    try:
        logger.info("Loading optimized production data...")
        await data_loader.load_all_optimized()
        # Log the counts of loaded data to confirm successful loading
        brand_count = len(data_loader.get_brands())
        bike_type_count = len(data_loader.get_bike_types())
        component_count = len(data_loader.get_components())
        logger.info(f"Production data loaded: {brand_count} brands, {bike_type_count} bike types, {component_count} components")
    except Exception as e:
        logger.error(f"Fatal error during data loading: {e}", exc_info=True)
        # In a serverless environment, raising an exception on startup is often the best way
        # to signal a critical failure.
        raise

# The 'app' object is now the ASGI application that FastMCP will run.
# There is no need for `if __name__ == "__main__":` or `asyncio.run()` here.
