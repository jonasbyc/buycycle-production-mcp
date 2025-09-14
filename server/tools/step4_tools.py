"""Step 4 MCP Tools: Components and Upgrades."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
import logging

logger = logging.getLogger(__name__)


async def list_component_categories() -> Dict[str, Any]:
    """
    Get all component categories available for bike listings.

    Returns categories of components that can be specified.
    Use this to understand what component information is needed.
    """
    try:
        components = data_loader.get_components()
        categories = list(components.keys())

        # Add descriptions for categories
        category_info = {
            "wheels": {
                "name": "Wheels",
                "description": "Wheelsets including rims and hubs",
                "required": True
            },
            "tires": {
                "name": "Tires",
                "description": "Tire brand, model, and specifications",
                "required": True
            },
            "saddles": {
                "name": "Saddle",
                "description": "Seat specifications and brand",
                "required": True
            },
            "handlebars": {
                "name": "Handlebars",
                "description": "Handlebar type, width, and material",
                "required": True
            },
            "pedals": {
                "name": "Pedals",
                "description": "Pedal type and system",
                "required": True
            },
            "upgrade_categories": {
                "name": "Upgrades",
                "description": "Components that have been upgraded from stock",
                "required": False
            }
        }

        formatted_categories = []
        for category in categories:
            info = category_info.get(category, {
                "name": category.title(),
                "description": f"{category.title()} components",
                "required": False
            })
            formatted_categories.append({
                "id": category,
                **info
            })

        return {
            "success": True,
            "data": {
                "categories": formatted_categories,
                "total_count": len(formatted_categories)
            },
            "metadata": {
                "step": 4,
                "next_suggested_tools": ["get_components_for_bike_type"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_component_categories: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_components_for_bike_type(bike_type_id: str, category: str = None) -> Dict[str, Any]:
    """
    Get components appropriate for a specific bike type.

    Args:
        bike_type_id: The bike type to get components for
        category: Optional specific category to filter by

    Returns component options filtered by bike type and optionally by category.
    Use to see what components are appropriate for the bike type.
    """
    try:
        if not data_loader.validate_bike_type_exists(bike_type_id):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BIKE_TYPE",
                    "message": f"Bike type '{bike_type_id}' does not exist"
                }
            }

        # Get components filtered by bike type
        components = data_loader.get_components_for_bike_type(bike_type_id)

        if category:
            if category not in components:
                return {
                    "success": False,
                    "error": {
                        "code": "INVALID_CATEGORY",
                        "message": f"Category '{category}' not available for bike type '{bike_type_id}'",
                        "available_categories": list(components.keys())
                    }
                }
            components = {category: components[category]}

        return {
            "success": True,
            "data": {
                "components": components,
                "bike_type_id": bike_type_id,
                "filtered_category": category
            },
            "metadata": {
                "step": 4,
                "next_suggested_tools": ["validate_components"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_components_for_bike_type: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_wheel_options(bike_type_id: str) -> Dict[str, Any]:
    """
    Get wheel options for a specific bike type.

    Args:
        bike_type_id: The bike type to get wheel options for

    Returns wheel specifications appropriate for the bike type.
    Use to understand wheel options for the bike type.
    """
    try:
        components = data_loader.get_components_for_bike_type(bike_type_id)
        wheels = components.get("wheels", [])

        if not wheels:
            # Fallback to road wheels if no specific ones found
            all_components = data_loader.get_components()
            wheels = all_components.get("wheels", {}).get("road", [])

        return {
            "success": True,
            "data": {
                "wheels": wheels,
                "bike_type_id": bike_type_id,
                "wheel_info": {
                    "weight_importance": "Lower weight improves performance",
                    "material_types": ["alloy", "carbon"],
                    "typical_weights": {
                        "road_alloy": "1500-1800g",
                        "road_carbon": "1200-1500g",
                        "mountain_alloy": "1800-2200g",
                        "mountain_carbon": "1500-1900g"
                    }
                }
            },
            "metadata": {
                "step": 4,
                "category": "wheels",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_wheel_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_tire_options(bike_type_id: str) -> Dict[str, Any]:
    """
    Get tire options for a specific bike type.

    Args:
        bike_type_id: The bike type to get tire options for

    Returns tire specifications appropriate for the bike type.
    Use to understand tire options and sizing for the bike type.
    """
    try:
        components = data_loader.get_components_for_bike_type(bike_type_id)
        tires = components.get("tires", [])

        if not tires:
            # Fallback based on bike type
            all_components = data_loader.get_components()
            tire_mapping = {
                "road": "road",
                "gravel": "gravel",
                "mountain": "mountain",
                "city": "road",  # Use road as fallback
                "hybrid": "road",
                "e_bike": "road",
                "touring": "road",
                "bmx": "road"  # Generic fallback
            }
            tire_type = tire_mapping.get(bike_type_id, "road")
            tires = all_components.get("tires", {}).get(tire_type, [])

        return {
            "success": True,
            "data": {
                "tires": tires,
                "bike_type_id": bike_type_id,
                "tire_info": {
                    "width_guide": {
                        "road": "23-32mm",
                        "gravel": "35-45mm",
                        "mountain": "2.0-2.6 inches",
                        "city": "28-42mm"
                    },
                    "types": ["clincher", "tubeless", "tubular"]
                }
            },
            "metadata": {
                "step": 4,
                "category": "tires",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_tire_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_saddle_options() -> Dict[str, Any]:
    """
    Get saddle options for bike listings.

    Returns saddle brands, models, and specifications.
    Use to understand saddle options and sizing.
    """
    try:
        components = data_loader.get_components()
        saddles = components.get("saddles", [])

        return {
            "success": True,
            "data": {
                "saddles": saddles,
                "saddle_info": {
                    "width_guide": {
                        "narrow": "130-143mm",
                        "medium": "143-155mm",
                        "wide": "155mm+"
                    },
                    "materials": ["leather", "synthetic", "carbon"],
                    "considerations": [
                        "Width should match sit bone measurement",
                        "Padding preference varies by rider",
                        "Material affects durability and comfort"
                    ]
                }
            },
            "metadata": {
                "step": 4,
                "category": "saddles",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_saddle_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_handlebar_options(bike_type_id: str) -> Dict[str, Any]:
    """
    Get handlebar options for a specific bike type.

    Args:
        bike_type_id: The bike type to get handlebar options for

    Returns handlebar specifications appropriate for the bike type.
    Use to understand handlebar options for the bike type.
    """
    try:
        components = data_loader.get_components_for_bike_type(bike_type_id)
        handlebars = components.get("handlebars", {})

        # If no specific handlebars found, get appropriate type
        if not handlebars:
            all_handlebars = data_loader.get_components().get("handlebars", {})
            if bike_type_id in ["road", "gravel", "touring"]:
                handlebars = all_handlebars.get("road", [])
            elif bike_type_id in ["mountain"]:
                handlebars = all_handlebars.get("mountain", [])
            else:
                handlebars = all_handlebars.get("city", [])

        return {
            "success": True,
            "data": {
                "handlebars": handlebars,
                "bike_type_id": bike_type_id,
                "handlebar_info": {
                    "types": {
                        "drop": "Curved bars for road/gravel bikes",
                        "flat": "Straight bars for mountain/city bikes",
                        "riser": "Upward-angled flat bars"
                    },
                    "width_guide": {
                        "road": "38-44cm (shoulder width)",
                        "mountain": "720-800mm (wider for control)",
                        "city": "600-680mm (comfortable width)"
                    }
                }
            },
            "metadata": {
                "step": 4,
                "category": "handlebars",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_handlebar_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_pedal_options() -> Dict[str, Any]:
    """
    Get pedal options for bike listings.

    Returns pedal types, systems, and brands.
    Use to understand pedal options and compatibility.
    """
    try:
        components = data_loader.get_components()
        pedals = components.get("pedals", [])

        return {
            "success": True,
            "data": {
                "pedals": pedals,
                "pedal_info": {
                    "systems": {
                        "SPD-SL": "Road clipless (3-bolt)",
                        "SPD": "Mountain clipless (2-bolt)",
                        "Keo": "Look road system",
                        "Eggbeater": "Crankbrothers system",
                        "flat": "Platform pedals (no clips)"
                    },
                    "considerations": [
                        "Clipless pedals require compatible shoes",
                        "Platform pedals work with any shoes",
                        "Road systems typically have larger platforms",
                        "Mountain systems easier to walk in"
                    ]
                }
            },
            "metadata": {
                "step": 4,
                "category": "pedals",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_pedal_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_upgrade_categories() -> Dict[str, Any]:
    """
    Get available upgrade categories for bike components.

    Returns categories of components that can be marked as upgrades.
    Use to understand what upgrades can be specified.
    """
    try:
        components = data_loader.get_components()
        upgrade_categories = components.get("upgrade_categories", [])

        # Add descriptions for upgrade categories
        category_descriptions = {
            "wheels": "Upgraded wheelsets from stock",
            "tires": "Premium or different tires from original",
            "drivetrain": "Upgraded shifters, derailleurs, or cassette",
            "brakes": "Upgraded brake systems or components",
            "suspension": "Upgraded fork or shock components",
            "cockpit": "Upgraded handlebars, stem, or grips",
            "seatpost": "Upgraded seatpost (carbon, dropper, etc.)",
            "saddle": "Premium or custom saddle upgrade",
            "pedals": "Upgraded pedal systems",
            "accessories": "Added accessories not originally included",
            "electronics": "Added electronic components or systems"
        }

        formatted_categories = []
        for category in upgrade_categories:
            formatted_categories.append({
                "id": category,
                "name": category.title(),
                "description": category_descriptions.get(category, f"Upgraded {category} components")
            })

        return {
            "success": True,
            "data": {
                "upgrade_categories": formatted_categories,
                "total_count": len(formatted_categories)
            },
            "metadata": {
                "step": 4,
                "category": "upgrades",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_upgrade_categories: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_components(bike_type_id: str, components: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate Step 4 component specifications.

    Args:
        bike_type_id: The bike type these components are for
        components: Dictionary of component specifications

    Validates all component information for completeness and compatibility.
    Use this to verify components before proceeding to Step 5.
    """
    try:
        # Run validation
        result = await validator.validate_step4(bike_type_id, components)

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "bike_type_id": bike_type_id,
                "validated_components": components
            },
            "metadata": {
                "step": 4,
                "next_suggested_tools": ["list_currencies"],
                "validation_status": "valid",
                "ready_for_next_step": True
            }
        }

    except ValidationError as e:
        return {
            "success": False,
            "error": {
                "code": e.code,
                "message": e.message,
                "details": e.details
            }
        }

    except Exception as e:
        logger.error(f"Error in validate_components: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }