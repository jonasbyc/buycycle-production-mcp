#!/usr/bin/env python3
"""
Buycycle Production MCP Server - Serverless Compatible
Conditional FastMCP import to avoid asyncio conflicts in Lambda environments
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global data containers
bike_data = {}

def load_production_data():
    """Load all optimized production data into memory for <1s response times."""
    global bike_data
    logger.info(" Loading optimized production data...")

    try:
        # Data directory
        data_dir = Path(__file__).parent / "data"

        # Load all optimized files
        with open(data_dir / "optimized_brands.json", 'r') as f:
            bike_data["brands"] = json.load(f)

        with open(data_dir / "enhanced_bike_types.json", 'r') as f:
            bike_data["bike_types"] = json.load(f)

        with open(data_dir / "enhanced_components.json", 'r') as f:
            bike_data["components"] = json.load(f)

        with open(data_dir / "enhanced_colors.json", 'r') as f:
            bike_data["colors"] = json.load(f)

        with open(data_dir / "enhanced_sizes.json", 'r') as f:
            bike_data["sizes"] = json.load(f)

        with open(data_dir / "enhanced_countries.json", 'r') as f:
            bike_data["countries"] = json.load(f)

        with open(data_dir / "agent_listing_structure.json", 'r') as f:
            bike_data["listing_structure"] = json.load(f)

        logger.info(f" Production data loaded: {len(bike_data['brands'])} brands, {len(bike_data['bike_types'])} bike types, {len(bike_data['components'])} components")

    except Exception as e:
        logger.error(f"Failed to load production data: {e}")
        raise

# Load data immediately on import
load_production_data()

# Always use FastMCP for consistent interface
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Buycycle Production Listing Server")

# Export server for FastMCP Cloud (required naming)
server = mcp

# Check if we're in a serverless environment for execution control
IS_SERVERLESS = bool(
    os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or
    os.environ.get('VERCEL') or
    os.environ.get('NETLIFY')
)

if IS_SERVERLESS:
    logger.info("Serverless environment detected - FastMCP will handle execution")

# Tool implementations (same as before)
@mcp.tool()
def get_complete_listing_workflow() -> str:
    """
    START HERE: Complete 6-step bike listing workflow with ALL options embedded.
    Returns the complete workflow structure with all available options for bike listing creation.
    Use this tool first to understand the full listing process and available options.
    """
    try:
        structure = bike_data["listing_structure"]

        workflow_summary = f"""
BUYCYCLE BIKE LISTING WORKFLOW - 6 STEPS

STEP 1: Basic Information
- Bike Type: {len(bike_data['bike_types'])} types available
- Brands: {len(bike_data['brands'])} brands with auto-selected custom families
- Use: search_bike_brands(query="brand name") to find specific brands

STEP 2: Technical Specifications
- Components: {len(bike_data['components'])} component options
- Colors: {len(bike_data['colors'])} colors with hex codes
- Sizes: {len(bike_data['sizes'])} frame sizes (numeric + letter)
- Materials: Carbon, Aluminum, Titanium, Steel, Magnesium
- Use: search_bike_components(query="component name") for specific parts

STEP 3: Location & Shipping
- Countries: {len(bike_data['countries'])} supported countries
- Shipping and location details required

STEP 4: Component Details
- Detailed component specifications
- Upgrade information and conditions

STEP 5: Pricing
- Price in EUR currency
- Market-based pricing recommendations

STEP 6: Photos
- Image upload and organization

NEXT STEPS:
1. Use search_bike_brands() to find your bike brand
2. Use get_bike_types_and_categories() to see available bike types
3. Use search_bike_components() to find compatible components
4. Use validate_bike_listing() to check your complete listing

Total options: {len(bike_data['brands'])} brands, {len(bike_data['components'])} components, {len(bike_data['colors'])} colors
"""
        return workflow_summary.strip()
    except Exception:
        return "Error loading workflow structure"

@mcp.tool()
def search_bike_brands(query: str = "", limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    STEP 1: Search for bike brands and get their IDs + auto-selected custom families.
    Returns brands with embedded custom family IDs to save additional tool calls.

    Args:
        query: Brand name to search for (e.g., "trek", "specialized")
        limit: Maximum number of brands to return (default: 20)
        offset: Pagination offset for large result sets (default: 0)

    Returns:
        Dictionary with brands list, pagination info, and search query
    """
    try:
        brands = bike_data["brands"]

        # Filter brands based on query
        if query:
            filtered_brands = [
                brand for brand in brands
                if query.lower() in brand["name"].lower()
            ]
        else:
            filtered_brands = brands

        # Apply pagination
        paginated_brands = filtered_brands[offset:offset + limit]

        return {
            "brands": paginated_brands,
            "pagination": {
                "total": len(filtered_brands),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(filtered_brands)
            },
            "query": query,
            "message": f"Found {len(filtered_brands)} brands. Each brand includes auto-selected custom_family_id."
        }

    except Exception as e:
        return {"error": f"Failed to search brands: {str(e)}"}

@mcp.tool()
def search_bike_components(query: str = "", bike_type_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    STEP 2: Search bike components (groupsets) with bike type filtering.
    Components are automatically filtered by bike type compatibility.

    Args:
        query: Component name to search for (e.g., "shimano", "sram")
        bike_type_id: Filter by bike type ID (1=Road, 2=Mountain, etc.)
        limit: Maximum number of components to return (default: 20)
        offset: Pagination offset for large result sets (default: 0)

    Returns:
        Dictionary with components list, pagination info, and compatibility data
    """
    try:
        components = bike_data["components"]

        # Filter by bike type if specified
        if bike_type_id is not None:
            components = [
                comp for comp in components
                if bike_type_id in comp.get("compatible_bike_types", [])
            ]

        # Filter by query
        if query:
            components = [
                comp for comp in components
                if query.lower() in comp["name"].lower()
            ]

        # Apply pagination
        paginated_components = components[offset:offset + limit]

        return {
            "components": paginated_components,
            "pagination": {
                "total": len(components),
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < len(components)
            },
            "query": query,
            "bike_type_filter": bike_type_id,
            "message": f"Found {len(components)} compatible components"
        }

    except Exception as e:
        return {"error": f"Failed to search components: {str(e)}"}

@mcp.tool()
def get_bike_types_and_categories() -> Dict[str, Any]:
    """
    Get all available bike types with their categories and IDs.
    Essential for STEP 1 bike type selection and component compatibility.

    Returns:
        Dictionary with bike types, categories, and usage information
    """
    try:
        return {
            "bike_types": bike_data["bike_types"],
            "total": len(bike_data["bike_types"]),
            "message": "Use bike_type_id for component filtering and validation"
        }
    except Exception as e:
        return {"error": f"Failed to get bike types: {str(e)}"}

@mcp.tool()
def get_frame_colors() -> Dict[str, Any]:
    """
    STEP 2: Get all available frame colors with hex codes and descriptions.
    Use these exact color names in your bike listing.

    Returns:
        Dictionary with colors, hex codes, and total count
    """
    try:
        return {
            "colors": bike_data["colors"],
            "total": len(bike_data["colors"]),
            "message": "Use exact color name from this list in bike listing"
        }
    except Exception as e:
        return {"error": f"Failed to get colors: {str(e)}"}

@mcp.tool()
def get_frame_sizes() -> Dict[str, Any]:
    """
    STEP 2: Get all available frame sizes (numeric and letter sizing).
    Includes both numeric sizes (42-64cm) and letter sizes (XS-XXXL).

    Returns:
        Dictionary with sizes, types, and descriptions
    """
    try:
        return {
            "sizes": bike_data["sizes"],
            "total": len(bike_data["sizes"]),
            "numeric_sizes": [s for s in bike_data["sizes"] if s["type"] == "numeric"],
            "letter_sizes": [s for s in bike_data["sizes"] if s["type"] == "letter"],
            "message": "Use exact size value from this list in bike listing"
        }
    except Exception as e:
        return {"error": f"Failed to get sizes: {str(e)}"}

@mcp.tool()
def get_supported_countries() -> Dict[str, Any]:
    """
    STEP 3: Get all supported countries for bike listings with shipping information.
    Use for location selection and shipping configuration.

    Returns:
        Dictionary with countries, shipping data, and total count
    """
    try:
        return {
            "countries": bike_data["countries"],
            "total": len(bike_data["countries"]),
            "message": "Use country_id for location in bike listing"
        }
    except Exception as e:
        return {"error": f"Failed to get countries: {str(e)}"}

@mcp.tool()
def validate_bike_listing(listing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    FINAL STEP: Validate a complete bike listing against the 6-step structure.
    Performs comprehensive validation of all required fields and data consistency.

    Args:
        listing_data: Complete bike listing following the 6-step structure

    Returns:
        Dictionary with validation result, errors, and suggestions
    """
    try:
        errors = []
        warnings = []

        # Basic structure validation
        required_steps = ["step_1", "step_2", "step_3", "step_5"]
        for step in required_steps:
            if step not in listing_data:
                errors.append(f"Missing required step: {step}")

        # Step 1 validation
        if "step_1" in listing_data:
            step1 = listing_data["step_1"]
            if "brand_id" not in step1:
                errors.append("step_1: brand_id is required")
            elif not any(b["id"] == step1["brand_id"] for b in bike_data["brands"]):
                errors.append(f"step_1: Invalid brand_id {step1['brand_id']}")

        # Step 2 validation
        if "step_2" in listing_data:
            step2 = listing_data["step_2"]
            required_fields = ["bike_category_id", "year", "frame_material_code", "frame_size", "color"]
            for field in required_fields:
                if field not in step2:
                    errors.append(f"step_2: {field} is required")

        # Step 5 validation
        if "step_5" in listing_data:
            step5 = listing_data["step_5"]
            if "price" not in step5:
                errors.append("step_5: price is required")
            elif not isinstance(step5.get("price"), (int, float)) or step5["price"] <= 0:
                errors.append("step_5: price must be a positive number")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "message": "Validation passed" if len(errors) == 0 else f"Found {len(errors)} errors",
            "listing_data": listing_data
        }

    except Exception as e:
        return {"error": f"Validation failed: {str(e)}", "valid": False}

def main():
    """Entry point for local development"""
    if not IS_SERVERLESS:
        mcp.run(transport="stdio")
    else:
        logger.info("Server loaded in serverless mode")

if __name__ == "__main__":
    main()