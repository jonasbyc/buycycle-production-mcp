"""Step 6 MCP Tools: Photos and Media."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
import logging

logger = logging.getLogger(__name__)


async def get_photo_requirements() -> Dict[str, Any]:
    """
    Get photo requirements and guidelines for bike listings.

    Returns specifications for photo uploads and best practices.
    Use this to understand photo requirements before upload.
    """
    try:
        requirements = {
            "quantity": {
                "minimum": 3,
                "maximum": 20,
                "recommended": 8
            },
            "technical_specs": {
                "min_resolution": "800x600",
                "recommended_resolution": "1920x1080",
                "max_file_size": "10MB",
                "supported_formats": ["JPEG", "JPG", "PNG", "WEBP"],
                "aspect_ratio": "4:3 or 16:9 recommended"
            },
            "required_shots": [
                {
                    "type": "main_photo",
                    "description": "Full bike profile shot from drive side",
                    "required": True,
                    "tips": ["Clean background", "Good lighting", "Show full bike"]
                },
                {
                    "type": "full_bike_front",
                    "description": "Front view of complete bike",
                    "required": True,
                    "tips": ["Center the bike", "Show handlebar and front wheel clearly"]
                },
                {
                    "type": "full_bike_rear",
                    "description": "Rear view showing drivetrain",
                    "required": True,
                    "tips": ["Show cassette and derailleur", "Include rear brake"]
                }
            ],
            "recommended_shots": [
                {
                    "type": "drivetrain_closeup",
                    "description": "Close-up of shifters, derailleurs, and cassette",
                    "tips": ["Show component brands clearly", "Include chain condition"]
                },
                {
                    "type": "cockpit",
                    "description": "Handlebars, stem, and controls",
                    "tips": ["Show brake levers", "Include computer mount if present"]
                },
                {
                    "type": "saddle_seatpost",
                    "description": "Saddle and seatpost area",
                    "tips": ["Show saddle condition", "Include seatpost clamp"]
                },
                {
                    "type": "wheels_tires",
                    "description": "Close-up of wheels and tires",
                    "tips": ["Show tire tread", "Include wheel brands if visible"]
                },
                {
                    "type": "frame_details",
                    "description": "Frame joints and material details",
                    "tips": ["Show any damage or wear", "Include frame size if marked"]
                }
            ]
        }

        return {
            "success": True,
            "data": {
                "photo_requirements": requirements,
                "photography_tips": [
                    "Clean the bike before photographing",
                    "Use natural lighting when possible",
                    "Avoid cluttered backgrounds",
                    "Take photos from slightly above bike level",
                    "Include close-ups of any damage or wear",
                    "Show serial numbers if visible",
                    "Photograph any upgrades or special features"
                ]
            },
            "metadata": {
                "step": 6,
                "next_suggested_tools": ["validate_photo_order", "get_photo_tips"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_photo_requirements: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_photo_tips(bike_type_id: str) -> Dict[str, Any]:
    """
    Get photography tips specific to a bike type.

    Args:
        bike_type_id: The bike type to get photography tips for

    Returns bike-type-specific photography guidance.
    Use to get targeted photography advice for the bike type.
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

        # Bike-type specific tips
        type_specific_tips = {
            "road": {
                "key_features": ["Aerodynamic frame shape", "Drop handlebars", "Narrow tires", "Lightweight components"],
                "photography_focus": [
                    "Show aerodynamic tube shapes",
                    "Capture handlebar tape condition",
                    "Highlight lightweight components",
                    "Show tire width and condition"
                ],
                "common_upgrades": ["Carbon wheels", "Electronic shifting", "Power meter", "Aerobars"]
            },
            "mountain": {
                "key_features": ["Suspension system", "Wide tires", "Sturdy frame", "Off-road components"],
                "photography_focus": [
                    "Show suspension travel and condition",
                    "Capture tire tread pattern",
                    "Highlight any frame protection",
                    "Show drivetrain protection (chain guide, etc.)"
                ],
                "common_upgrades": ["Dropper seatpost", "Tubeless setup", "Upgraded suspension", "Protective gear"]
            },
            "e_bike": {
                "key_features": ["Motor system", "Battery", "Display unit", "Electric components"],
                "photography_focus": [
                    "Show motor location and brand",
                    "Capture battery and mounting system",
                    "Display unit and controls",
                    "Any charging port or cables"
                ],
                "common_upgrades": ["Larger battery", "Premium display", "Upgraded motor", "Smart connectivity"]
            },
            "gravel": {
                "key_features": ["Versatile geometry", "Wide tire clearance", "Adventure-ready features", "Multiple mounting points"],
                "photography_focus": [
                    "Show tire clearance and frame spacing",
                    "Capture mounting points for accessories",
                    "Highlight any adventure features",
                    "Show disc brakes and wide handlebars"
                ],
                "common_upgrades": ["Bikepacking bags", "Tubeless setup", "Adventure accessories", "Wider tires"]
            }
        }

        tips = type_specific_tips.get(bike_type_id, {
            "key_features": ["Frame design", "Component quality", "Overall condition"],
            "photography_focus": ["Show frame clearly", "Capture component details", "Document condition"],
            "common_upgrades": ["Component upgrades", "Accessory additions"]
        })

        return {
            "success": True,
            "data": {
                "bike_type_id": bike_type_id,
                "specific_tips": tips,
                "general_advice": [
                    "Take photos in good natural lighting",
                    "Clean the bike thoroughly before shooting",
                    "Use a neutral background",
                    "Include detail shots of key components",
                    "Show any wear or damage honestly",
                    "Highlight unique or upgraded features"
                ]
            },
            "metadata": {
                "step": 6,
                "validation_status": "informational"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_photo_tips: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_photo_order(photos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate photo order and selection for Step 6.

    Args:
        photos: List of photo objects with order, description, and main photo flag

    Validates photo sequence and ensures main photo is properly set.
    Use this to verify photo organization before listing completion.
    """
    try:
        # Run validation
        result = await validator.validate_step6(photos)

        # Additional checks for photo quality
        suggestions = []

        if len(photos) < 5:
            suggestions.append("Consider adding more photos - 5-8 photos typically get better buyer interest")

        main_photos = [p for p in photos if p.get("is_main", False)]
        if main_photos:
            main_photo = main_photos[0]
            if "profile" not in main_photo.get("description", "").lower() and "side" not in main_photo.get("description", "").lower():
                suggestions.append("Main photo should ideally be a profile (side) view of the complete bike")

        # Check for recommended photo types
        descriptions = [p.get("description", "").lower() for p in photos]
        recommended_checks = {
            "drivetrain": any("drivetrain" in desc or "shifter" in desc or "derailleur" in desc for desc in descriptions),
            "wheels": any("wheel" in desc or "tire" in desc for desc in descriptions),
            "cockpit": any("handlebar" in desc or "cockpit" in desc or "stem" in desc for desc in descriptions)
        }

        for feature, present in recommended_checks.items():
            if not present:
                suggestions.append(f"Consider adding a {feature} detail photo to showcase components")

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "photo_count": len(photos),
                "main_photo_set": len(main_photos) == 1,
                "suggestions": suggestions,
                "validated_photos": photos
            },
            "metadata": {
                "step": 6,
                "next_suggested_tools": ["create_complete_listing"],
                "validation_status": "valid",
                "ready_for_completion": True
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
        logger.error(f"Error in validate_photo_order: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def suggest_photo_descriptions(bike_type_id: str, photo_count: int) -> Dict[str, Any]:
    """
    Suggest photo descriptions and order for optimal listing presentation.

    Args:
        bike_type_id: The bike type for targeted suggestions
        photo_count: Number of photos planned for the listing

    Returns suggested photo sequence and descriptions.
    Use to plan photo organization for maximum impact.
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

        # Base photo suggestions that apply to all bike types
        base_suggestions = [
            {
                "order": 1,
                "description": "Full bike profile view (drive side)",
                "is_main": True,
                "priority": "required",
                "tips": "Clean bike, good lighting, drive side visible"
            },
            {
                "order": 2,
                "description": "Full bike front view",
                "is_main": False,
                "priority": "required",
                "tips": "Center frame, show handlebars clearly"
            },
            {
                "order": 3,
                "description": "Drivetrain and rear derailleur detail",
                "is_main": False,
                "priority": "high",
                "tips": "Show component brands, chain condition"
            }
        ]

        # Type-specific additions
        type_specific = {
            "e_bike": [
                {
                    "order": 4,
                    "description": "Motor and battery system",
                    "priority": "required",
                    "tips": "Show motor brand and battery mounting"
                },
                {
                    "order": 5,
                    "description": "Display unit and controls",
                    "priority": "high",
                    "tips": "Show screen and control buttons clearly"
                }
            ],
            "mountain": [
                {
                    "order": 4,
                    "description": "Front suspension detail",
                    "priority": "high",
                    "tips": "Show fork brand and travel setting"
                },
                {
                    "order": 5,
                    "description": "Rear suspension (if full-suspension)",
                    "priority": "conditional",
                    "tips": "Show shock and linkage system"
                }
            ],
            "road": [
                {
                    "order": 4,
                    "description": "Cockpit and shifter detail",
                    "priority": "high",
                    "tips": "Show shifter brand and handlebar tape"
                }
            ]
        }

        # Common additional photos for any remaining slots
        additional_suggestions = [
            {
                "description": "Saddle and seatpost",
                "priority": "medium",
                "tips": "Show saddle condition and seatpost type"
            },
            {
                "description": "Wheels and tires close-up",
                "priority": "medium",
                "tips": "Show tire tread and wheel condition"
            },
            {
                "description": "Frame size marking or geometry",
                "priority": "low",
                "tips": "Include frame size sticker if visible"
            },
            {
                "description": "Any damage or wear areas",
                "priority": "conditional",
                "tips": "Document any issues honestly"
            },
            {
                "description": "Serial number (if comfortable sharing)",
                "priority": "low",
                "tips": "For authenticity verification"
            }
        ]

        # Build suggestion list based on photo count
        suggestions = base_suggestions.copy()

        # Add type-specific photos
        if bike_type_id in type_specific:
            for photo in type_specific[bike_type_id]:
                if len(suggestions) < photo_count:
                    photo["order"] = len(suggestions) + 1
                    suggestions.append(photo)

        # Fill remaining slots with additional suggestions
        for photo in additional_suggestions:
            if len(suggestions) < photo_count:
                photo["order"] = len(suggestions) + 1
                photo["is_main"] = False
                suggestions.append(photo)

        return {
            "success": True,
            "data": {
                "suggested_photos": suggestions[:photo_count],
                "bike_type_id": bike_type_id,
                "photo_count": photo_count,
                "optimization_tips": [
                    "First 3 photos are most critical for buyer interest",
                    "Main photo should show the complete bike clearly",
                    "Include detail shots of expensive components",
                    "Document any wear or damage honestly",
                    "Good lighting makes a huge difference in photo quality"
                ]
            },
            "metadata": {
                "step": 6,
                "validation_status": "informational"
            }
        }

    except Exception as e:
        logger.error(f"Error in suggest_photo_descriptions: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }