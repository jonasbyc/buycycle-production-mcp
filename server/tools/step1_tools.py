"""Step 1 MCP Tools: Bike Type, Brand, and Model Selection."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
from ..models import MCPResponse, MCPError
import logging

logger = logging.getLogger(__name__)


async def list_bike_types() -> Dict[str, Any]:
    """
    Get all available bike types with descriptions.

    Returns a list of bike types that can be listed on Buycycle.
    Use this as the first step to understand what type of bike is being listed.
    """
    try:
        bike_types = data_loader.get_bike_types()

        # Format for easy consumption
        formatted_types = []
        for type_id, type_info in bike_types.items():
            formatted_types.append({
                "id": type_id,
                "name": type_info["name"],
                "description": type_info["description"],
                "category": type_info["category"]
            })

        return {
            "success": True,
            "data": {
                "bike_types": formatted_types,
                "total_count": len(formatted_types)
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["list_brands"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_bike_types: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def list_brands(limit: int = 50) -> Dict[str, Any]:
    """
    Get all available bike brands.

    Args:
        limit: Maximum number of brands to return (default: 50)

    Returns brands that can be selected for bike listings.
    Use after selecting bike type to see available brands.
    """
    try:
        brands = data_loader.get_brands()

        # Format and limit results
        formatted_brands = []
        for brand_id, brand_info in list(brands.items())[:limit]:
            formatted_brands.append({
                "id": brand_id,
                "name": brand_info["name"],
                "country": brand_info.get("country"),
                "specialty": brand_info.get("specialty", [])
            })

        return {
            "success": True,
            "data": {
                "brands": formatted_brands,
                "total_count": len(brands),
                "showing_count": len(formatted_brands)
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["list_models_for_brand"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_brands: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def search_brands(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for bike brands by name.

    Args:
        query: Search term (brand name or partial name)
        limit: Maximum results to return (default: 20)

    Returns brands matching the search query.
    Use this when you know part of the brand name.
    """
    try:
        brands = data_loader.get_brands()
        query_lower = query.lower()

        # Search brands
        matching_brands = []
        for brand_id, brand_info in brands.items():
            if query_lower in brand_info["name"].lower():
                matching_brands.append({
                    "id": brand_id,
                    "name": brand_info["name"],
                    "country": brand_info.get("country"),
                    "specialty": brand_info.get("specialty", [])
                })

        # Limit results
        matching_brands = matching_brands[:limit]

        return {
            "success": True,
            "data": {
                "brands": matching_brands,
                "query": query,
                "total_matches": len(matching_brands)
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["list_models_for_brand"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in search_brands: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def list_models_for_brand(brand_id: str, bike_type_id: str) -> Dict[str, Any]:
    """
    Get all models for a specific brand and bike type.

    Args:
        brand_id: The brand identifier (from list_brands)
        bike_type_id: The bike type identifier (from list_bike_types)

    Returns models available for the specified brand and bike type.
    Use after selecting brand to see available models.
    """
    try:
        # Validate inputs
        if not data_loader.validate_brand_exists(brand_id):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BRAND",
                    "message": f"Brand '{brand_id}' does not exist",
                    "valid_values": list(data_loader.get_brands().keys())
                }
            }

        if not data_loader.validate_bike_type_exists(bike_type_id):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_BIKE_TYPE",
                    "message": f"Bike type '{bike_type_id}' does not exist",
                    "valid_values": list(data_loader.get_bike_types().keys())
                }
            }

        # Get models
        models = data_loader.get_brand_models_by_type(brand_id, bike_type_id)

        if not models:
            return {
                "success": True,
                "data": {
                    "models": [],
                    "brand_id": brand_id,
                    "bike_type_id": bike_type_id,
                    "message": f"No {bike_type_id} models found for brand {brand_id}"
                },
                "metadata": {
                    "step": 1,
                    "next_suggested_tools": ["list_brands"],
                    "validation_status": "pending"
                }
            }

        return {
            "success": True,
            "data": {
                "models": models,
                "brand_id": brand_id,
                "bike_type_id": bike_type_id,
                "total_count": len(models)
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["get_model_details", "validate_step1_selection"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_models_for_brand: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_model_details(brand_id: str, model_id: str, bike_type_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific bike model.

    Args:
        brand_id: The brand identifier
        model_id: The model identifier
        bike_type_id: The bike type identifier

    Returns detailed specifications for the model.
    Use to get comprehensive information about a selected model.
    """
    try:
        # Validate model exists
        if not data_loader.validate_model_exists(brand_id, model_id, bike_type_id):
            return {
                "success": False,
                "error": {
                    "code": "INVALID_MODEL",
                    "message": f"Model '{model_id}' not found for brand '{brand_id}' and bike type '{bike_type_id}'"
                }
            }

        # Get model details
        models = data_loader.get_brand_models_by_type(brand_id, bike_type_id)
        model = next((m for m in models if m["id"] == model_id), None)

        if not model:
            return {
                "success": False,
                "error": {
                    "code": "MODEL_NOT_FOUND",
                    "message": f"Model details not found"
                }
            }

        # Get brand info
        brand = data_loader.get_brands()[brand_id]
        bike_type = data_loader.get_bike_types()[bike_type_id]

        return {
            "success": True,
            "data": {
                "model": model,
                "brand": {
                    "id": brand_id,
                    "name": brand["name"],
                    "country": brand.get("country")
                },
                "bike_type": {
                    "id": bike_type_id,
                    "name": bike_type["name"],
                    "category": bike_type["category"]
                }
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["validate_step1_selection"],
                "validation_status": "ready_for_validation"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_model_details: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_step1_selection(bike_type_id: str, brand_id: str, model_id: str) -> Dict[str, Any]:
    """
    Validate Step 1 selections (bike type, brand, and model).

    Args:
        bike_type_id: Selected bike type
        brand_id: Selected brand
        model_id: Selected model

    Validates that the combination is valid and compatible.
    Use this before proceeding to Step 2.
    """
    try:
        # Run validation
        result = await validator.validate_step1(bike_type_id, brand_id, model_id)

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "selections": {
                    "bike_type_id": bike_type_id,
                    "brand_id": brand_id,
                    "model_id": model_id
                }
            },
            "metadata": {
                "step": 1,
                "next_suggested_tools": ["get_step2_detail_options"],
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
        logger.error(f"Error in validate_step1_selection: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }