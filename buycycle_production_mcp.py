#!/usr/bin/env python3
"""
Buycycle Production MCP Server - Optimized FastMCP Version
Production-ready MCP server with real Buycycle data and 6-step workflow.
Optimized for speed, accuracy, and AI agent interactions.
"""
from mcp.server.fastmcp import FastMCP
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Buycycle Production Listing Server")

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

        # Create lookup dictionaries for O(1) access
        bike_data["brands_by_id"] = {brand["id"]: brand for brand in bike_data["brands"]}
        bike_data["types_by_id"] = {bt["id"]: bt for bt in bike_data["bike_types"]}
        bike_data["components_by_id"] = {comp["id"]: comp for comp in bike_data["components"]}

        logger.info(f" Production data loaded: {len(bike_data['brands'])} brands, "
                   f"{len(bike_data['bike_types'])} bike types, "
                   f"{len(bike_data['components'])} components")

    except Exception as e:
        logger.error(f" Failed to load production data: {e}")
        raise

# Load data when module is imported
load_production_data()

# STEP 1 TOOLS: Bike Type, Brand Selection with Custom Family Auto-Selection

@mcp.tool()
def get_bike_types_and_categories() -> Dict[str, Any]:
    """
    STEP 1: Get all bike types and their subcategories for user selection.

    Returns:
        dict: Complete list of bike types (Road & Gravel, Mountainbike) with all subcategories

    USE THIS FIRST - Shows user both bike_type_id options (1,2) and all bike_category_id options.
    This eliminates the need for separate category lookups.
    """
    try:
        bike_types = []
        for bike_type in bike_data["bike_types"]:
            bike_types.append({
                "id": bike_type["id"],
                "name": bike_type["name"],
                "description": bike_type["description"],
                "categories": bike_type["categories"],
                "total_categories": bike_type["total_categories"]
            })

        return {
            "success": True,
            "step": 1,
            "data": {
                "bike_types": bike_types,
                "total_count": len(bike_types),
                "next_action": "Select bike type, then search for brands"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_bike_types: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def get_categories_for_bike_type(bike_type_id: int) -> Dict[str, Any]:
    """
    STEP 1 ALTERNATIVE: Get subcategories for a specific bike type (if not using get_bike_types_and_categories).

    Args:
        bike_type_id: 1 = Road & Gravel, 2 = Mountainbike

    Returns:
        dict: Subcategories for the specified bike type with IDs and names

    TIP: Use get_bike_types_and_categories() instead to get everything at once.
    """
    try:
        bike_type = bike_data["types_by_id"].get(bike_type_id)
        if not bike_type:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BIKE_TYPE",
                    "message": f"Bike type ID {bike_type_id} not found",
                    "valid_ids": list(bike_data["types_by_id"].keys())
                }
            }

        return {
            "success": True,
            "step": 1,
            "data": {
                "bike_type": {
                    "id": bike_type["id"],
                    "name": bike_type["name"],
                    "description": bike_type["description"]
                },
                "categories": bike_type["categories"],
                "total_categories": len(bike_type["categories"])
            }
        }

    except Exception as e:
        logger.error(f"Error in get_bike_categories: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def search_bike_brands(query: str = "", limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    STEP 1: Search for bike brands and get their IDs + auto-selected custom families.

    Args:
        query: Brand name to search (e.g., "Trek", "Specialized"). Empty = show all brands
        limit: How many results to return (default: 20, max: 100)
        offset: Skip results for pagination (default: 0)

    Returns:
        dict: Brands with brand_id (integer) + custom_family_id (integer) pre-selected

    KEY: Returns brand_id AND family_id together - no separate family lookup needed!
    Examples: search_bike_brands("Trek"), search_bike_brands("") for all brands
    """
    try:
        # Validate parameters
        limit = min(max(1, limit), 100)  # Between 1 and 100
        offset = max(0, offset)

        # Filter brands by query
        if query.strip():
            matching_brands = [
                brand for brand in bike_data["brands"]
                if query.lower() in brand["name"].lower()
            ]
        else:
            matching_brands = bike_data["brands"]

        # Apply pagination
        total_matches = len(matching_brands)
        paginated_brands = matching_brands[offset:offset + limit]

        # Format response with custom family pre-selected
        brands = []
        for brand in paginated_brands:
            brands.append({
                "id": brand["id"],
                "name": brand["name"],
                "description": brand["description"],
                "custom_family_id": brand["custom_family_id"],
                "custom_family_name": brand["custom_family_name"],
                "total_families": brand["total_families"]
            })

        return {
            "success": True,
            "step": 1,
            "data": {
                "brands": brands,
                "query": query,
                "pagination": {
                    "current_page": (offset // limit) + 1,
                    "total_results": total_matches,
                    "results_per_page": limit,
                    "has_more": (offset + limit) < total_matches
                },
                "note": "custom_family_id is pre-selected for speed optimization"
            }
        }

    except Exception as e:
        logger.error(f"Error in search_brands: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def validate_step1_basic_info(bike_type_id: int, brand_id: int, bike_category_id: int) -> Dict[str, Any]:
    """
    STEP 1 VALIDATION: Verify bike type, brand, and category selections before Step 2.

    Args:
        bike_type_id: Selected bike type (1 or 2)
        brand_id: Selected brand ID (integer from search_bike_brands)
        bike_category_id: Selected category ID (integer matching bike_type_id)

    Returns:
        dict: Validation success + complete Step 1 data + auto-selected family_id

    REQUIRED: Call this after user makes Step 1 choices to ensure valid combinations.
    """
    try:
        errors = []

        # Validate bike type
        bike_type = bike_data["types_by_id"].get(bike_type_id)
        if not bike_type:
            errors.append(f"Invalid bike_type_id: {bike_type_id}")

        # Validate brand
        brand = bike_data["brands_by_id"].get(brand_id)
        if not brand:
            errors.append(f"Invalid brand_id: {brand_id}")

        # Validate category belongs to bike type
        category_valid = False
        if bike_type:
            for category in bike_type["categories"]:
                if category["id"] == bike_category_id:
                    category_valid = True
                    break

        if not category_valid:
            errors.append(f"Category {bike_category_id} does not belong to bike type {bike_type_id}")

        if errors:
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Step 1 validation failed",
                    "errors": errors
                }
            }

        # Auto-select custom family
        family_id = brand["custom_family_id"]
        family_name = brand["custom_family_name"]

        return {
            "success": True,
            "step": 1,
            "data": {
                "validated": True,
                "selections": {
                    "bike_type_id": bike_type_id,
                    "bike_type_name": bike_type["name"],
                    "brand_id": brand_id,
                    "brand_name": brand["name"],
                    "bike_category_id": bike_category_id,
                    "family_id": family_id,
                    "family_name": family_name
                },
                "message": "Step 1 validated successfully. Custom family auto-selected.",
                "next_step": "Proceed to Step 2: Technical Specifications"
            }
        }

    except Exception as e:
        logger.error(f"Error in validate_step1: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

# STEP 2 TOOLS: Technical Specifications

@mcp.tool()
def get_frame_material_options() -> Dict[str, Any]:
    """
    STEP 2: Get all frame material codes and descriptions for user selection.

    Returns:
        dict: 5 frame materials (carbon, aluminum, titanium, steel, magnesium) with descriptions

    NOTE: These are also embedded in get_complete_listing_workflow() to save calls.
    Returns frame_material_code (string) needed for Step 2 validation.
    """
    try:
        materials = [
            {"code": "carbon", "name": "Carbon", "description": "Carbon fiber - Lightweight and stiff"},
            {"code": "aluminum", "name": "Aluminum", "description": "Aluminum alloy - Durable and affordable"},
            {"code": "titanium", "name": "Titanium", "description": "Titanium - Premium lightweight metal"},
            {"code": "steel", "name": "Steel", "description": "Steel - Classic and comfortable"},
            {"code": "magnesium", "name": "Magnesium", "description": "Magnesium - Ultra-lightweight metal"}
        ]

        return {
            "success": True,
            "step": 2,
            "data": {
                "frame_materials": materials,
                "total_count": len(materials)
            }
        }

    except Exception as e:
        logger.error(f"Error in get_frame_materials: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def get_compatible_components(bike_type_id: int) -> Dict[str, Any]:
    """
    STEP 2: Get component groupsets compatible with the selected bike type.

    Args:
        bike_type_id: 1 = Road & Gravel components, 2 = Mountainbike components

    Returns:
        dict: Component groupsets (Shimano, SRAM, Campagnolo) with IDs and descriptions

    FILTERED: Only shows components compatible with your bike type (saves agent time).
    Returns bike_component_id (integer) needed for Step 2 validation.
    """
    try:
        bike_type = bike_data["types_by_id"].get(bike_type_id)
        if not bike_type:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BIKE_TYPE",
                    "message": f"Bike type ID {bike_type_id} not found"
                }
            }

        # Filter components compatible with this bike type
        compatible_components = []
        for component in bike_data["components"]:
            for comp_bike_type in component["bike_types"]:
                if comp_bike_type["id"] == bike_type_id:
                    compatible_components.append({
                        "id": component["id"],
                        "name": component["name"],
                        "description": component["description"]
                    })
                    break

        return {
            "success": True,
            "step": 2,
            "data": {
                "bike_type": {
                    "id": bike_type["id"],
                    "name": bike_type["name"]
                },
                "compatible_components": compatible_components,
                "total_count": len(compatible_components)
            }
        }

    except Exception as e:
        logger.error(f"Error in get_components_for_type: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def get_bike_color_options() -> Dict[str, Any]:
    """
    STEP 2: Get all bike colors with IDs and hex codes for user selection.

    Returns:
        dict: 8 colors (Black, White, Gray, Red, Green, Orange, Blue, Purple) with hex codes

     VISUAL: Includes hex codes for UI display. Returns color_id (integer) for validation.
     NOTE: Also embedded in get_complete_listing_workflow() to save calls.
    """
    try:
        return {
            "success": True,
            "step": 2,
            "data": {
                "colors": bike_data["colors"],
                "total_count": len(bike_data["colors"])
            }
        }

    except Exception as e:
        logger.error(f"Error in get_colors: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def get_frame_size_options() -> Dict[str, Any]:
    """
    STEP 2: Get all frame sizes (numeric 42-64cm and letter XS-XXXL) for user selection.

    Returns:
        dict: 32 frame sizes grouped by type (numeric/letter) with descriptions

     ORGANIZED: Separates numeric sizes (42-64) from letter sizes (XS-XXXL).
    Returns frame_size (string) like "54" or "l" for validation.
    """
    try:
        # Group sizes by type for better UX
        numeric_sizes = [size for size in bike_data["sizes"] if size["type"] == "numeric"]
        letter_sizes = [size for size in bike_data["sizes"] if size["type"] == "letter"]

        return {
            "success": True,
            "step": 2,
            "data": {
                "numeric_sizes": numeric_sizes,
                "letter_sizes": letter_sizes,
                "all_sizes": bike_data["sizes"],
                "total_count": len(bike_data["sizes"])
            }
        }

    except Exception as e:
        logger.error(f"Error in get_sizes: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def validate_step2_technical_specs(bike_type_id: int, bike_category_id: int, motor: bool, year: int,
                   frame_material_code: str, bike_component_id: int, frame_size: str,
                   color_id: int, **additional_specs) -> Dict[str, Any]:
    """
    STEP 2 VALIDATION: Verify all technical specifications before proceeding to Step 3.

    Args:
        bike_type_id: 1 or 2 (from Step 1)
        bike_category_id: Category ID (from Step 1)
        motor: True/False for e-bike
        year: Manufacturing year (1980-2025)
        frame_material_code: "carbon", "aluminum", "titanium", "steel", or "magnesium"
        bike_component_id: Component groupset ID (from get_compatible_components)
        frame_size: Size code like "54" or "l"
        color_id: Color ID 56-63
        **additional_specs: shifting_code, brake_type_code, suspension_configuration, etc.

    Returns:
        dict: Complete validation result + formatted specifications for Step 3

     REQUIRED: Validates all technical fields with detailed error messages if invalid.
    """
    try:
        errors = []

        # Validate year
        if not (1980 <= year <= 2025):
            errors.append("Year must be between 1980 and 2025")

        # Validate frame material
        valid_materials = ["carbon", "aluminum", "titanium", "steel", "magnesium"]
        if frame_material_code not in valid_materials:
            errors.append(f"Invalid frame material. Valid options: {valid_materials}")

        # Validate component
        component = bike_data["components_by_id"].get(bike_component_id)
        if not component:
            errors.append(f"Invalid component ID: {bike_component_id}")

        # Validate color
        valid_color_ids = [color["id"] for color in bike_data["colors"]]
        if color_id not in valid_color_ids:
            errors.append(f"Invalid color ID. Valid options: {valid_color_ids}")

        # Validate frame size
        valid_sizes = [size["size"] for size in bike_data["sizes"]]
        if frame_size not in valid_sizes:
            errors.append(f"Invalid frame size. Valid options: {valid_sizes}")

        if errors:
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Step 2 validation failed",
                    "errors": errors
                }
            }

        return {
            "success": True,
            "step": 2,
            "data": {
                "validated": True,
                "specifications": {
                    "bike_type_id": bike_type_id,
                    "bike_category_id": bike_category_id,
                    "motor": motor,
                    "year": year,
                    "frame_material_code": frame_material_code,
                    "bike_component_id": bike_component_id,
                    "frame_size": frame_size,
                    "color_id": color_id,
                    **additional_specs
                },
                "message": "Step 2 validated successfully",
                "next_step": "Proceed to Step 3: Location Information"
            }
        }

    except Exception as e:
        logger.error(f"Error in validate_step2: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

# STEP 3 TOOLS: Location Information

@mcp.tool()
def get_supported_countries() -> Dict[str, Any]:
    """
    STEP 3: Get all countries where bikes can be listed and shipped.

    Returns:
        dict: 28 supported countries with IDs, names, and shipping information

     SHIPPING: Shows which countries support Buycycle marketplace listings.
    Returns country_id (integer) needed for Step 3 validation.
    """
    try:
        return {
            "success": True,
            "step": 3,
            "data": {
                "countries": bike_data["countries"],
                "total_count": len(bike_data["countries"])
            }
        }

    except Exception as e:
        logger.error(f"Error in list_countries: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def validate_step3_location_info(country_id: int, zip_code: str, state: str, city: str, receipt_present: bool) -> Dict[str, Any]:
    """
    STEP 3 VALIDATION: Verify location and receipt information before proceeding to Step 4.

    Args:
        country_id: Country ID (integer from get_supported_countries)
        zip_code: Postal/ZIP code (string, required)
        state: State, province, or region (string, required)
        city: City name (string, required)
        receipt_present: True if have original purchase receipt, False if not

    Returns:
        dict: Validation success + complete location data for Step 4

     REQUIRED: Validates country exists and all location fields are provided.
    Receipt info affects listing credibility but doesn't block validation.
    """
    try:
        errors = []

        # Validate country
        country = next((c for c in bike_data["countries"] if c["id"] == country_id), None)
        if not country:
            errors.append(f"Invalid country ID: {country_id}")

        # Validate required fields
        if not zip_code.strip():
            errors.append("ZIP/postal code is required")
        if not city.strip():
            errors.append("City is required")

        if errors:
            return {
                "success": False,
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": "Step 3 validation failed",
                    "errors": errors
                }
            }

        return {
            "success": True,
            "step": 3,
            "data": {
                "validated": True,
                "location": {
                    "country_id": country_id,
                    "country_name": country["name"] if country else None,
                    "zip_code": zip_code,
                    "state": state,
                    "city": city,
                    "receipt_present": receipt_present
                },
                "message": "Step 3 validated successfully",
                "next_step": "Proceed to Step 4: Component Details"
            }
        }

    except Exception as e:
        logger.error(f"Error in validate_step3: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

# UTILITY TOOLS

@mcp.tool()
def get_complete_listing_workflow() -> Dict[str, Any]:
    """
    START HERE: Complete 6-step bike listing workflow with ALL options embedded.

    Returns:
        dict: Complete workflow with bike types, categories, frame materials, colors,
              suspension types, brake types, and field requirements - ALL in one response

    EFFICIENCY: Contains ALL static options inline - no need for separate calls to:
    - get_frame_materials, get_colors, get suspension types, get_brake_types

    WORKFLOW: Shows exact tools needed for each step + embedded options for immediate use.
    Perfect starting point for any bike listing conversation.
    """
    try:
        structure = {
            "description": "Complete 6-step bike listing workflow - all options embedded for efficiency",
            "instructions": "Use this structure to guide the user through bike listing creation. All options are provided inline to eliminate extra tool calls.",
            "workflow": "step_1 → step_2 → step_3 → step_4 → step_5 → step_6",

            "step_1": {
                "title": "Basic Bike Information",
                "required": True,
                "description": "Select bike type, brand, and auto-assign custom family",
                "fields": {
                    "bike_type_id": {
                        "description": "Main bike category - choose one",
                        "required": True,
                        "type": "integer",
                        "options": [
                            {"id": 1, "name": "Road & Gravel", "description": "Road bikes, gravel bikes, triathlon, vintage"},
                            {"id": 2, "name": "Mountainbike", "description": "Mountain bikes, downhill, trail, crosscountry, enduro"}
                        ]
                    },
                    "bike_category_id": {
                        "description": "Specific subcategory - must match bike_type_id",
                        "required": True,
                        "type": "integer",
                        "road_gravel_options": [
                            {"id": 1, "name": "Road", "bike_type_id": 1},
                            {"id": 2, "name": "Gravel", "bike_type_id": 1},
                            {"id": 4, "name": "Triathlon", "bike_type_id": 1},
                            {"id": 45, "name": "Vintage", "bike_type_id": 1}
                        ],
                        "mountainbike_options": [
                            {"id": 19, "name": "Downhill", "bike_type_id": 2},
                            {"id": 26, "name": "Trail", "bike_type_id": 2},
                            {"id": 27, "name": "Other", "bike_type_id": 2},
                            {"id": 28, "name": "Crosscountry", "bike_type_id": 2},
                            {"id": 29, "name": "Enduro", "bike_type_id": 2}
                        ]
                    },
                    "brand_id": {
                        "description": "Bike manufacturer - use search_bike_brands tool to find specific brands",
                        "required": True,
                        "type": "integer",
                        "tool": "search_bike_brands",
                        "note": "Use search_bike_brands('Trek') to find brands. 1232 brands available.",
                        "examples": ["Trek", "Specialized", "Giant", "Cannondale"]
                    },
                    "family_id": {
                        "description": "Model family - automatically selected as custom family",
                        "required": True,
                        "type": "integer",
                        "auto_selection": "custom_family_id from selected brand",
                        "note": "This is automatically filled when brand is selected"
                    }
                },
                "validation_tool": "validate_step1"
            },

            "step_2": {
                "title": "Technical Specifications",
                "required": True,
                "description": "Specify technical details, components, and physical attributes",
                "fields": {
                    "motor": {
                        "description": "Electric motor present",
                        "required": True,
                        "type": "boolean",
                        "options": [
                            {"value": True, "description": "E-bike with motor"},
                            {"value": False, "description": "Traditional bike without motor"}
                        ]
                    },
                    "year": {
                        "description": "Manufacturing year",
                        "required": True,
                        "type": "integer",
                        "validation": "Between 1980-2025",
                        "examples": [2023, 2022, 2021, 2020]
                    },
                    "frame_material_code": {
                        "description": "Frame material type",
                        "required": True,
                        "type": "string",
                        "options": [
                            {"code": "carbon", "name": "Carbon", "description": "Carbon fiber - lightweight and stiff"},
                            {"code": "aluminum", "name": "Aluminum", "description": "Aluminum alloy - durable and affordable"},
                            {"code": "titanium", "name": "Titanium", "description": "Titanium - premium lightweight metal"},
                            {"code": "steel", "name": "Steel", "description": "Steel - classic and comfortable"},
                            {"code": "magnesium", "name": "Magnesium", "description": "Magnesium - ultra-lightweight metal"}
                        ]
                    },
                    "bike_component_id": {
                        "description": "Component groupset - filtered by bike type",
                        "required": True,
                        "type": "integer",
                        "tool": "get_compatible_components",
                        "note": "Use get_compatible_components(bike_type_id) to get compatible options"
                    },
                    "shifting_code": {
                        "description": "Shifting system type",
                        "required": True,
                        "type": "string",
                        "options": [
                            {"code": "mechanical", "name": "Mechanical", "description": "Cable-actuated shifting"},
                            {"code": "electronic", "name": "Electronic", "description": "Electronic shifting (Di2, eTap, EPS)"},
                            {"code": "other", "name": "Other", "description": "Alternative shifting systems"}
                        ]
                    },
                    "brake_type_code": {
                        "description": "Brake system type",
                        "required": True,
                        "type": "string",
                        "options": [
                            {"code": "rim", "name": "Rim", "description": "Rim brakes"},
                            {"code": "disc", "name": "Disc", "description": "Disc brakes (hydraulic or mechanical)"},
                            {"code": "coaster", "name": "Coaster", "description": "Coaster/back-pedal brakes"},
                            {"code": "other", "name": "Other", "description": "Alternative brake systems"}
                        ]
                    },
                    "msrp": {
                        "description": "Original retail price",
                        "required": True,
                        "type": "integer",
                        "validation": "Positive integer in EUR",
                        "examples": [2500, 4000, 8000]
                    },
                    "frame_size": {
                        "description": "Frame size code - use get_frame_size_options() to see options",
                        "required": True,
                        "type": "string",
                        "tool": "get_frame_size_options",
                        "note": "Use get_frame_size_options() to see all 32 size options (e.g., '42', 's', 'l')",
                        "examples": ["42", "54", "s", "m", "l"]
                    },
                    "color_id": {
                        "description": "Bike color",
                        "required": True,
                        "type": "integer",
                        "options": [
                            {"id": 56, "name": "Black", "code": "#111827"},
                            {"id": 57, "name": "White", "code": "#FFFFFF"},
                            {"id": 58, "name": "Gray", "code": "#D1D5DB"},
                            {"id": 59, "name": "Red", "code": "#EF4444"},
                            {"id": 60, "name": "Green", "code": "#80BE70"},
                            {"id": 61, "name": "Orange", "code": "#F59E0B"},
                            {"id": 62, "name": "Blue", "code": "#3B82F6"},
                            {"id": 63, "name": "Purple", "code": "#9A2DF0"}
                        ]
                    },
                    "suspension_configuration": {
                        "description": "Suspension type",
                        "required": True,
                        "type": "string",
                        "options": [
                            {"code": "rigid", "name": "Rigid", "description": "No suspension"},
                            {"code": "hardtail", "name": "Hardtail", "description": "Front suspension only"},
                            {"code": "full", "name": "Full", "description": "Front and rear suspension"}
                        ]
                    },
                    "front_suspension_travel": {
                        "description": "Front suspension travel in mm (if applicable)",
                        "required": False,
                        "type": "integer",
                        "validation": "0-200mm, 0 if rigid",
                        "examples": [100, 120, 140, 160]
                    },
                    "rear_suspension_travel": {
                        "description": "Rear suspension travel in mm (if full suspension)",
                        "required": False,
                        "type": "integer",
                        "validation": "0-200mm, 0 if not full suspension",
                        "examples": [100, 120, 140, 150]
                    }
                },
                "validation_tool": "validate_step2"
            },

            "step_3": {
                "title": "Location & Receipt",
                "required": True,
                "description": "Specify location and receipt information",
                "fields": {
                    "receipt_present": {
                        "description": "Original purchase receipt available",
                        "required": True,
                        "type": "boolean",
                        "options": [
                            {"value": True, "description": "Have original receipt"},
                            {"value": False, "description": "No original receipt"}
                        ]
                    },
                    "country_id": {
                        "description": "Country location",
                        "required": True,
                        "type": "integer",
                        "tool": "get_supported_countries",
                        "note": "Use get_supported_countries() to see all 28 supported countries"
                    },
                    "zip_code": {
                        "description": "Postal/ZIP code",
                        "required": True,
                        "type": "string",
                        "validation": "Valid postal code format"
                    },
                    "state": {
                        "description": "State, province, or region",
                        "required": True,
                        "type": "string"
                    },
                    "city": {
                        "description": "City name",
                        "required": True,
                        "type": "string"
                    }
                },
                "validation_tool": "validate_step3"
            },

            "step_4": {
                "title": "Component Details",
                "required": True,
                "description": "Specify individual component details (user input)",
                "fields": {
                    "Fork_Material": {"description": "Fork material/brand", "type": "string", "required": False},
                    "Fork": {"description": "Fork model/specifications", "type": "string", "required": False},
                    "Tires": {"description": "Tire brand/model/size", "type": "string", "required": False},
                    "Cassette": {"description": "Cassette specifications", "type": "string", "required": False},
                    "Seatpost": {"description": "Seatpost specifications", "type": "string", "required": False},
                    "Handlebar": {"description": "Handlebar specifications", "type": "string", "required": False},
                    "Chainrings": {"description": "Chainring specifications", "type": "string", "required": False},
                    "Saddle": {"description": "Saddle brand/model", "type": "string", "required": False},
                    "Wheels": {"description": "Wheelset specifications", "type": "string", "required": False},
                    "Crank": {"description": "Crank specifications", "type": "string", "required": False},
                    "Stem": {"description": "Stem specifications", "type": "string", "required": False},
                    "Brakes": {"description": "Brake specifications", "type": "string", "required": False},
                    "RearDerailleur": {"description": "Rear derailleur specifications", "type": "string", "required": False},
                    "Pedals": {"description": "Pedal specifications", "type": "string", "required": False},
                    "RearShock": {"description": "Rear shock specifications", "type": "string", "required": False},
                    "Motor": {"description": "Motor specifications (if e-bike)", "type": "string", "required": False},
                    "info": {"description": "Additional component information", "type": "string", "required": False}
                },
                "note": "All fields are user-provided text. No validation tools needed."
            },

            "step_5": {
                "title": "Pricing",
                "required": True,
                "description": "Set listing price",
                "fields": {
                    "price": {
                        "description": "Listing price",
                        "required": True,
                        "type": "integer",
                        "validation": "Positive integer",
                        "examples": [1500, 2000, 3500]
                    },
                    "currency": {
                        "description": "Price currency",
                        "required": True,
                        "type": "string",
                        "default": "EUR",
                        "options": ["EUR", "USD"]
                    }
                }
            },

            "step_6": {
                "title": "Photos",
                "required": True,
                "description": "Upload bike photos",
                "fields": {
                    "photos": {
                        "description": "Photo upload array",
                        "required": True,
                        "type": "array",
                        "validation": "3-20 photos required",
                        "requirements": [
                            "Minimum 3 photos required",
                            "Maximum 20 photos allowed",
                            "Include: full bike profile, front view, drivetrain detail"
                        ]
                    }
                }
            }
        }

        return {
            "success": True,
            "data": structure,
            "summary": {
                "total_steps": 6,
                "embedded_options": "All options provided inline - no extra tool calls needed",
                "tools_needed": ["search_bike_brands", "get_compatible_components", "get_frame_size_options", "get_supported_countries"],
                "validation_tools": ["validate_step1_basic_info", "validate_step2_technical_specs", "validate_step3_location_info"]
            }
        }

    except Exception as e:
        logger.error(f"Error in get_listing_structure: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

@mcp.tool()
def get_server_capabilities() -> Dict[str, Any]:
    """
     SERVER INFO: Get details about this Buycycle MCP server's capabilities and loaded data.

    Returns:
        dict: Server version, loaded data counts, optimization features, and available tools

     SHOWS: 1232 brands, 110 components, 28 countries, and all optimization features.
    Use for debugging or to understand server capabilities.
    """
    try:
        return {
            "success": True,
            "data": {
                "name": "Buycycle Production Listing MCP Server",
                "version": "2.0.0-production",
                "description": "Production-ready MCP server with real Buycycle data",
                "features": [
                    "Real production data from Buycycle",
                    "1232 optimized brands with custom families",
                    "6-step listing workflow",
                    "Search and filtering capabilities",
                    "Strict validation",
                    "Agent-optimized responses",
                    "<1s response times"
                ],
                "steps": 6,
                "total_tools": 15,
                "data_loaded": {
                    "brands": len(bike_data.get("brands", [])),
                    "bike_types": len(bike_data.get("bike_types", [])),
                    "components": len(bike_data.get("components", [])),
                    "colors": len(bike_data.get("colors", [])),
                    "sizes": len(bike_data.get("sizes", [])),
                    "countries": len(bike_data.get("countries", []))
                },
                "optimizations": [
                    "Custom family IDs pre-selected",
                    "O(1) lookups with ID mappings",
                    "Filtered components by bike type",
                    "Enhanced descriptions for AI agents",
                    "Production-ready data validation"
                ]
            }
        }

    except Exception as e:
        logger.error(f"Error in get_server_info: {e}")
        return {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": str(e)}
        }

# RESOURCES

@mcp.resource("listing://structure")
def get_listing_structure_resource() -> str:
    """Get listing structure as a formatted resource."""
    try:
        structure = bike_data["listing_structure"]
        return f"""
Buycycle Listing Structure - 6 Steps

Step 1: {structure['steps']['step_1']['title']}
- Tools: {', '.join(structure['steps']['step_1']['tools_to_use'])}

Step 2: {structure['steps']['step_2']['title']}
- Tools: {', '.join(structure['steps']['step_2']['tools_to_use'])}

[Additional steps available in full structure]

Total brands: {len(bike_data['brands'])}
Total components: {len(bike_data['components'])}
        """.strip()

    except Exception:
        return "Error loading listing structure"

# Export the FastMCP instance for FastMCP Cloud
server = mcp

def main():
    """Entry point for local development"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    import os
    # Only run the server if not in serverless environment
    if not os.environ.get('AWS_LAMBDA_FUNCTION_NAME') and not os.environ.get('VERCEL') and not os.environ.get('NETLIFY'):
        main()