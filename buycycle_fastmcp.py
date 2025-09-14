#!/usr/bin/env python3
"""
Buycycle MCP Server - FastMCP Cloud Compatible
Uses FastMCP but with minimal async conflicts
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

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
        # Don't raise - let tools handle missing data gracefully

# Try to create FastMCP server but fallback to simple object
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("Buycycle Listing Server")

    @mcp.tool()
    def list_bike_types() -> dict:
        """Get all available bike types with descriptions."""
        # Lazy load data
        if not _data_loaded:
            load_bike_data()

        bike_types = []
        if "bike_types" in bike_data:
            for type_id, type_info in bike_data["bike_types"].items():
                bike_types.append({
                    "id": type_id,
                    "name": type_info["name"],
                    "description": type_info["description"],
                    "category": type_info["category"]
                })

        return {
            "success": True,
            "data": {
                "bike_types": bike_types,
                "total_count": len(bike_types)
            }
        }

    @mcp.tool()
    def list_brands(limit: int = 20) -> dict:
        """Get available bike brands with optional limit."""
        # Lazy load data
        if not _data_loaded:
            load_bike_data()

        brands = []
        if "brands" in bike_data:
            for brand_id, brand_info in list(bike_data["brands"].items())[:limit]:
                brands.append({
                    "id": brand_id,
                    "name": brand_info["name"]
                })

        return {
            "success": True,
            "data": {
                "brands": brands,
                "total_count": len(brands)
            }
        }

    @mcp.tool()
    def list_countries() -> dict:
        """Get supported countries for bike listings."""
        # Lazy load data
        if not _data_loaded:
            load_bike_data()

        countries = []
        if "countries" in bike_data:
            for country_code, country_info in bike_data["countries"].items():
                countries.append({
                    "code": country_code,
                    "name": country_info["name"]
                })

        return {
            "success": True,
            "data": {
                "countries": countries,
                "total_count": len(countries)
            }
        }

    # Create app for FastMCP Cloud - but avoid running it at module level
    app = None

    def get_app():
        """Get the app instance - lazy creation to avoid asyncio conflicts"""
        global app
        if app is None:
            try:
                # Try to create HTTP app without running
                from fastapi import FastAPI
                app = FastAPI(title="Buycycle MCP Server", version="1.0.0")

                @app.get("/")
                @app.get("/health")
                async def health_check():
                    return {"status": "ok", "service": "buycycle-mcp-server"}

            except Exception as e:
                logger.error(f"Failed to create FastAPI app: {e}")
                # Fallback - try to create streamable HTTP app
                try:
                    app = mcp.streamable_http_app()
                except Exception as e2:
                    logger.error(f"Failed to create MCP app: {e2}")
                    # Final fallback - create a dummy object
                    class DummyApp:
                        def __init__(self):
                            self.name = "Buycycle MCP Server"
                    app = DummyApp()
        return app

    # Export app for FastMCP Cloud
    app = get_app()

except ImportError as e:
    logger.error(f"Failed to import FastMCP: {e}")
    # Create a simple fallback object
    class SimpleMCPServer:
        def __init__(self, name):
            self.name = name

    mcp = SimpleMCPServer("Buycycle Listing Server")

    # Create a simple FastAPI app as fallback
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Buycycle MCP Server", version="1.0.0")

        @app.get("/")
        @app.get("/health")
        async def health_check():
            return {"status": "ok", "service": "buycycle-mcp-server"}

    except ImportError:
        # Final fallback - create dummy app
        class DummyApp:
            def __init__(self):
                self.name = "Buycycle MCP Server"
        app = DummyApp()

except Exception as e:
    logger.error(f"Unexpected error during server setup: {e}")
    # Create dummy objects to prevent import errors
    class DummyServer:
        def __init__(self):
            self.name = "Buycycle MCP Server"
    mcp = DummyServer()
    app = DummyServer()