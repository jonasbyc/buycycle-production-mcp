#!/usr/bin/env python3
"""
Buycycle Listing MCP Server - FastMCP Version
Simplified version following Composio's recommended approach.
"""
from mcp.server.fastmcp import FastMCP
import json
import asyncio
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Buycycle Listing Server")

# Load data at module level for simplicity
DATA_DIR = Path(__file__).parent / "data"
bike_data = {}

def load_bike_data():
    """Load all bike data into memory."""
    global bike_data
    logger.info("Loading bike data...")

    try:
        # Load bike types
        with open(DATA_DIR / "bike_types.json", 'r') as f:
            bike_data["bike_types"] = json.load(f)

        # Load brands
        with open(DATA_DIR / "brands.json", 'r') as f:
            bike_data["brands"] = json.load(f)

        # Load models by brand
        with open(DATA_DIR / "models_by_brand.json", 'r') as f:
            bike_data["models_by_brand"] = json.load(f)

        # Load countries
        with open(DATA_DIR / "countries.json", 'r') as f:
            bike_data["countries"] = json.load(f)

        # Load step 2 details
        with open(DATA_DIR / "step2_details.json", 'r') as f:
            bike_data["step2_details"] = json.load(f)

        logger.info(f"Loaded data: {len(bike_data['brands'])} brands, {len(bike_data['countries'])} countries")

    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise

# Data will be loaded lazily when first tool is called
_data_loaded = False

def ensure_data_loaded():
    """Ensure data is loaded before accessing it."""
    global _data_loaded
    if not _data_loaded:
        load_bike_data()
        _data_loaded = True

# STEP 1 TOOLS: Bike Type, Brand, and Model Selection

@mcp.tool()
def list_bike_types() -> dict:
    """Get all available bike types with descriptions."""
    ensure_data_loaded()
    bike_types = []
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
    ensure_data_loaded()
    brands = []
    for brand_id, brand_info in list(bike_data["brands"].items())[:limit]:
        brands.append({
            "id": brand_id,
            "name": brand_info["name"],
            "country": brand_info.get("country"),
            "specialty": brand_info.get("specialty", [])
        })

    return {
        "success": True,
        "data": {
            "brands": brands,
            "showing_count": len(brands),
            "total_available": len(bike_data["brands"])
        }
    }

@mcp.tool()
def search_brands(query: str, limit: int = 10) -> dict:
    """Search for bike brands by name."""
    matching_brands = []
    query_lower = query.lower()

    for brand_id, brand_info in bike_data["brands"].items():
        if query_lower in brand_info["name"].lower():
            matching_brands.append({
                "id": brand_id,
                "name": brand_info["name"],
                "country": brand_info.get("country"),
                "specialty": brand_info.get("specialty", [])
            })

        if len(matching_brands) >= limit:
            break

    return {
        "success": True,
        "data": {
            "brands": matching_brands,
            "query": query,
            "total_matches": len(matching_brands)
        }
    }

@mcp.tool()
def get_models_for_brand(brand_id: str, bike_type_id: str) -> dict:
    """Get models for a specific brand and bike type."""
    if brand_id not in bike_data["brands"]:
        return {
            "success": False,
            "error": {
                "code": "INVALID_BRAND",
                "message": f"Brand '{brand_id}' not found",
                "available_brands": list(bike_data["brands"].keys())[:10]
            }
        }

    if bike_type_id not in bike_data["bike_types"]:
        return {
            "success": False,
            "error": {
                "code": "INVALID_BIKE_TYPE",
                "message": f"Bike type '{bike_type_id}' not found",
                "available_types": list(bike_data["bike_types"].keys())
            }
        }

    models = bike_data["models_by_brand"].get(brand_id, {}).get(bike_type_id, [])

    return {
        "success": True,
        "data": {
            "models": models,
            "brand_id": brand_id,
            "bike_type_id": bike_type_id,
            "total_count": len(models)
        }
    }

# STEP 2 TOOLS: Bike Details

@mcp.tool()
def get_frame_materials() -> dict:
    """Get all available frame materials."""
    frame_materials = bike_data["step2_details"].get("frame_materials", {})

    return {
        "success": True,
        "data": {
            "frame_materials": frame_materials,
            "count": len(frame_materials)
        }
    }

@mcp.tool()
def get_bike_conditions() -> dict:
    """Get all available bike conditions."""
    conditions = bike_data["step2_details"].get("conditions", {})

    return {
        "success": True,
        "data": {
            "conditions": conditions,
            "count": len(conditions)
        }
    }

@mcp.tool()
def validate_bike_selection(bike_type_id: str, brand_id: str, model_id: str) -> dict:
    """Validate a complete bike selection."""
    errors = []

    # Check bike type
    if bike_type_id not in bike_data["bike_types"]:
        errors.append(f"Invalid bike type: {bike_type_id}")

    # Check brand
    if brand_id not in bike_data["brands"]:
        errors.append(f"Invalid brand: {brand_id}")

    # Check model exists for brand and type
    models = bike_data["models_by_brand"].get(brand_id, {}).get(bike_type_id, [])
    if not any(m["id"] == model_id for m in models):
        errors.append(f"Model '{model_id}' not found for brand '{brand_id}' and type '{bike_type_id}'")

    if errors:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_FAILED",
                "message": "Selection validation failed",
                "errors": errors
            }
        }

    return {
        "success": True,
        "data": {
            "valid": True,
            "message": "Selection is valid",
            "next_step": "Specify bike details"
        }
    }

# STEP 3 TOOLS: Location

@mcp.tool()
def list_countries() -> dict:
    """Get all supported countries."""
    countries = []
    for country in bike_data["countries"]:
        countries.append({
            "code": country["code"],
            "name": country["name"],
            "currencies": country.get("currencies", [])
        })

    return {
        "success": True,
        "data": {
            "countries": countries,
            "total_count": len(countries)
        }
    }

@mcp.tool()
def get_cities_for_country(country_code: str, limit: int = 10) -> dict:
    """Get major cities for a country."""
    country = None
    for c in bike_data["countries"]:
        if c["code"] == country_code.upper():
            country = c
            break

    if not country:
        return {
            "success": False,
            "error": {
                "code": "INVALID_COUNTRY",
                "message": f"Country code '{country_code}' not supported"
            }
        }

    cities = country.get("major_cities", [])[:limit]

    return {
        "success": True,
        "data": {
            "cities": cities,
            "country": country["name"],
            "country_code": country_code.upper(),
            "showing_count": len(cities)
        }
    }

# UTILITY TOOLS

@mcp.tool()
def get_server_info() -> dict:
    """Get information about this MCP server."""
    return {
        "success": True,
        "data": {
            "name": "Buycycle Listing MCP Server",
            "version": "1.0.0",
            "description": "Helps create bike listings for the Buycycle marketplace",
            "steps": 6,
            "total_tools": 12,
            "data_loaded": {
                "brands": len(bike_data.get("brands", {})),
                "bike_types": len(bike_data.get("bike_types", {})),
                "countries": len(bike_data.get("countries", []))
            }
        }
    }

@mcp.tool()
def calculate_listing_progress(completed_steps: list) -> dict:
    """Calculate how much of the listing process is complete."""
    total_steps = 6
    completed = len(completed_steps)

    return {
        "success": True,
        "data": {
            "completed_steps": completed,
            "total_steps": total_steps,
            "progress_percentage": round((completed / total_steps) * 100, 1),
            "remaining_steps": total_steps - completed,
            "is_complete": completed == total_steps
        }
    }

# RESOURCES

@mcp.resource("listing://progress/{steps}")
def get_listing_progress(steps: str) -> str:
    """Get listing progress as a formatted resource."""
    completed_steps = steps.split(",") if steps else []
    result = calculate_listing_progress(completed_steps)

    if result["success"]:
        data = result["data"]
        return f"""
Buycycle Listing Progress: {data['progress_percentage']}%
Completed: {data['completed_steps']}/{data['total_steps']} steps
Remaining: {data['remaining_steps']} steps
Status: {'Complete' if data['is_complete'] else 'In Progress'}
        """.strip()

    return "Error calculating progress"

# Create HTTP app for AWS Lambda Web Adapter (FastMCP Cloud)
app = mcp.streamable_http_app()

if __name__ == "__main__":
    # For local testing only
    mcp.run(transport="stdio")