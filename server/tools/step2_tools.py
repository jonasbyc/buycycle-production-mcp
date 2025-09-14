"""Step 2 MCP Tools: Bike Details and Specifications."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
import logging

logger = logging.getLogger(__name__)


async def get_step2_detail_options(bike_type_id: str) -> Dict[str, Any]:
    """
    Get all available detail options for Step 2 based on bike type.

    Args:
        bike_type_id: The bike type to get options for

    Returns all available options for bike details (frame materials, conditions, etc.).
    Use this to see what options are available for the bike type.
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

        # Get all step 2 options
        step2_options = data_loader.get_step2_details()
        conditional_fields = data_loader.get_conditional_fields()
        bike_type_rules = conditional_fields.get("bike_types", {}).get(bike_type_id, {})

        # Filter options based on bike type
        filtered_options = {}

        # Always include basic options
        basic_fields = ["frame_materials", "conditions", "years", "common_colors", "frame_sizes", "brake_types"]
        for field in basic_fields:
            if field in step2_options:
                if field == "frame_sizes":
                    filtered_options[field] = step2_options[field].get(bike_type_id, step2_options[field].get("road", []))
                else:
                    filtered_options[field] = step2_options[field]

        # Add conditional fields based on bike type
        required_fields = bike_type_rules.get("required_fields", [])
        excluded_fields = bike_type_rules.get("excluded_fields", [])

        # E-bike specific options
        if bike_type_id == "e_bike" or "motor" in required_fields:
            filtered_options.update({
                "motor_brands": step2_options.get("motor_brands", {}),
                "motor_positions": step2_options.get("motor_positions", {}),
                "battery_capacities": step2_options.get("battery_capacities", [])
            })

        # Mountain bike specific options
        if bike_type_id == "mountain" or "suspension" in str(required_fields):
            filtered_options["suspension_types"] = step2_options.get("suspension_types", {})

        # Drivetrain options (not for BMX typically)
        if bike_type_id != "bmx":
            filtered_options.update({
                "shifter_brands": step2_options.get("shifter_brands", {}),
                "brake_brands": step2_options.get("brake_brands", {})
            })

        return {
            "success": True,
            "data": {
                "options": filtered_options,
                "bike_type_id": bike_type_id,
                "field_rules": {
                    "required_fields": required_fields,
                    "excluded_fields": excluded_fields,
                    "conditional_fields": bike_type_rules.get("conditional_fields", {})
                }
            },
            "metadata": {
                "step": 2,
                "next_suggested_tools": ["validate_bike_details"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_step2_detail_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_frame_materials() -> Dict[str, Any]:
    """
    Get all available frame materials with details.

    Returns comprehensive information about frame material options.
    Use to understand frame material choices and their characteristics.
    """
    try:
        step2_options = data_loader.get_step2_details()
        frame_materials = step2_options.get("frame_materials", {})

        return {
            "success": True,
            "data": {
                "frame_materials": frame_materials,
                "total_count": len(frame_materials)
            },
            "metadata": {
                "step": 2,
                "field": "frame_material_code",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_frame_materials: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_motor_options() -> Dict[str, Any]:
    """
    Get all e-bike motor options (brands, positions, battery capacities).

    Returns motor-related options for e-bikes.
    Use only for e-bike listings to get motor specifications.
    """
    try:
        step2_options = data_loader.get_step2_details()

        motor_data = {
            "motor_brands": step2_options.get("motor_brands", {}),
            "motor_positions": step2_options.get("motor_positions", {}),
            "battery_capacities": step2_options.get("battery_capacities", [])
        }

        return {
            "success": True,
            "data": motor_data,
            "metadata": {
                "step": 2,
                "bike_type_requirement": "e_bike",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_motor_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_suspension_options() -> Dict[str, Any]:
    """
    Get suspension type options and travel ranges.

    Returns suspension-related options for mountain bikes.
    Use for mountain bikes to understand suspension options.
    """
    try:
        step2_options = data_loader.get_step2_details()
        suspension_types = step2_options.get("suspension_types", {})

        # Add typical travel ranges
        travel_info = {
            "front_suspension_travel_ranges": {
                "xc": "80-120mm",
                "trail": "120-150mm",
                "enduro": "150-170mm",
                "downhill": "170-200mm+"
            },
            "rear_suspension_travel_ranges": {
                "trail": "110-140mm",
                "enduro": "140-170mm",
                "downhill": "170-200mm+"
            }
        }

        return {
            "success": True,
            "data": {
                "suspension_types": suspension_types,
                "travel_info": travel_info
            },
            "metadata": {
                "step": 2,
                "bike_type_requirement": "mountain",
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_suspension_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_drivetrain_options() -> Dict[str, Any]:
    """
    Get drivetrain component options (shifters, brakes).

    Returns drivetrain-related component options.
    Use to understand shifter and brake options.
    """
    try:
        step2_options = data_loader.get_step2_details()

        drivetrain_data = {
            "shifter_brands": step2_options.get("shifter_brands", {}),
            "brake_types": step2_options.get("brake_types", {}),
            "brake_brands": step2_options.get("brake_brands", {}),
            "typical_speeds": {
                "road": [8, 9, 10, 11, 12],
                "mountain": [7, 8, 9, 10, 11, 12],
                "city": [1, 3, 7, 8, 9],
                "e_bike": [1, 5, 7, 8, 9, 10, 11]
            }
        }

        return {
            "success": True,
            "data": drivetrain_data,
            "metadata": {
                "step": 2,
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_drivetrain_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_bike_details(bike_type_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate bike details for Step 2.

    Args:
        bike_type_id: The bike type these details are for
        details: Dictionary of bike details to validate

    Validates all bike specifications against bike type requirements.
    Use this to check if all details are valid before proceeding to Step 3.
    """
    try:
        # Run validation
        result = await validator.validate_step2(bike_type_id, details)

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "bike_type_id": bike_type_id,
                "validated_details": details
            },
            "metadata": {
                "step": 2,
                "next_suggested_tools": ["list_countries"],
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
        logger.error(f"Error in validate_bike_details: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def check_field_requirements(bike_type_id: str) -> Dict[str, Any]:
    """
    Get field requirements for a specific bike type.

    Args:
        bike_type_id: The bike type to check requirements for

    Returns detailed information about which fields are required, optional, or excluded.
    Use this to understand what information is needed for the bike type.
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

        conditional_fields = data_loader.get_conditional_fields()
        bike_type_rules = conditional_fields.get("bike_types", {}).get(bike_type_id, {})
        validation_rules = conditional_fields.get("validation_rules", {})

        return {
            "success": True,
            "data": {
                "bike_type_id": bike_type_id,
                "required_fields": bike_type_rules.get("required_fields", []),
                "optional_fields": bike_type_rules.get("optional_fields", []),
                "excluded_fields": bike_type_rules.get("excluded_fields", []),
                "conditional_fields": bike_type_rules.get("conditional_fields", {}),
                "validation_rules": validation_rules
            },
            "metadata": {
                "step": 2,
                "validation_status": "informational"
            }
        }

    except Exception as e:
        logger.error(f"Error in check_field_requirements: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }