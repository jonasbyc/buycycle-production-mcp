"""Step 3 MCP Tools: Location and Shipping."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
import logging

logger = logging.getLogger(__name__)


async def list_countries() -> Dict[str, Any]:
    """
    Get all supported countries for bike listings.

    Returns countries where bikes can be listed and sold.
    Use this to show available countries for the listing location.
    """
    try:
        countries = data_loader.get_countries()

        # Format for consumption
        formatted_countries = []
        for country in countries:
            formatted_countries.append({
                "code": country["code"],
                "name": country["name"],
                "currencies": country.get("currencies", []),
                "shipping_options": {
                    "domestic": country.get("shipping_domestic", False),
                    "eu": country.get("shipping_eu", False),
                    "international": country.get("shipping_international", False)
                }
            })

        return {
            "success": True,
            "data": {
                "countries": formatted_countries,
                "total_count": len(formatted_countries)
            },
            "metadata": {
                "step": 3,
                "next_suggested_tools": ["get_cities_for_country", "get_shipping_options"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_countries: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_country_details(country_code: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific country.

    Args:
        country_code: ISO country code (e.g., 'DE', 'US', 'GB')

    Returns detailed information about the country including cities and shipping options.
    Use after country selection to get specific details.
    """
    try:
        country = data_loader.get_country_by_code(country_code.upper())

        if not country:
            available_codes = [c["code"] for c in data_loader.get_countries()]
            return {
                "success": False,
                "error": {
                    "code": "INVALID_COUNTRY",
                    "message": f"Country code '{country_code}' not supported",
                    "valid_values": available_codes
                }
            }

        return {
            "success": True,
            "data": {
                "country": country,
                "major_cities": country.get("major_cities", []),
                "shipping_capabilities": {
                    "domestic": country.get("shipping_domestic", False),
                    "eu": country.get("shipping_eu", False),
                    "international": country.get("shipping_international", False)
                },
                "supported_currencies": country.get("currencies", [])
            },
            "metadata": {
                "step": 3,
                "next_suggested_tools": ["get_shipping_options", "validate_location"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_country_details: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_cities_for_country(country_code: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get major cities for a specific country.

    Args:
        country_code: ISO country code
        limit: Maximum number of cities to return (default: 20)

    Returns major cities that can be used for listings in the country.
    Use to help users select appropriate cities.
    """
    try:
        country = data_loader.get_country_by_code(country_code.upper())

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
                "country_code": country_code.upper(),
                "country_name": country["name"],
                "showing_count": len(cities)
            },
            "metadata": {
                "step": 3,
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_cities_for_country: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_shipping_options(country_code: str) -> Dict[str, Any]:
    """
    Get available shipping options for a country.

    Args:
        country_code: ISO country code

    Returns shipping methods and capabilities for the country.
    Use to understand what shipping options are available.
    """
    try:
        country = data_loader.get_country_by_code(country_code.upper())

        if not country:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_COUNTRY",
                    "message": f"Country code '{country_code}' not supported"
                }
            }

        # Define shipping options based on country capabilities
        shipping_options = []

        if country.get("shipping_domestic", False):
            shipping_options.extend([
                {
                    "id": "pickup",
                    "name": "Pickup by Buyer",
                    "description": "Buyer collects bike in person",
                    "cost": "Free",
                    "available": True
                },
                {
                    "id": "domestic_shipping",
                    "name": "Domestic Shipping",
                    "description": f"Shipping within {country['name']}",
                    "cost": "Varies",
                    "available": True
                }
            ])

        if country.get("shipping_eu", False):
            shipping_options.append({
                "id": "eu_shipping",
                "name": "EU Shipping",
                "description": "Shipping within European Union",
                "cost": "Varies",
                "available": True
            })

        if country.get("shipping_international", False):
            shipping_options.append({
                "id": "international_shipping",
                "name": "International Shipping",
                "description": "Worldwide shipping",
                "cost": "Varies",
                "available": True
            })

        return {
            "success": True,
            "data": {
                "shipping_options": shipping_options,
                "country_code": country_code.upper(),
                "country_name": country["name"]
            },
            "metadata": {
                "step": 3,
                "next_suggested_tools": ["validate_location"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_shipping_options: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_location(country_code: str, city: str, postal_code: str, shipping_options: List[str]) -> Dict[str, Any]:
    """
    Validate Step 3 location and shipping information.

    Args:
        country_code: Selected country code
        city: Selected city
        postal_code: Postal/ZIP code
        shipping_options: List of selected shipping method IDs

    Validates location information and shipping selections.
    Use this to verify location data before proceeding to Step 4.
    """
    try:
        # Run validation
        result = await validator.validate_step3(country_code, city, postal_code, shipping_options)

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "location": {
                    "country_code": country_code,
                    "city": city,
                    "postal_code": postal_code,
                    "shipping_options": shipping_options
                }
            },
            "metadata": {
                "step": 3,
                "next_suggested_tools": ["list_component_categories"],
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
        logger.error(f"Error in validate_location: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def search_cities(country_code: str, query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for cities within a country.

    Args:
        country_code: ISO country code
        query: City name or partial name to search for
        limit: Maximum results to return (default: 10)

    Returns cities matching the search query.
    Use when users want to find specific cities.
    """
    try:
        country = data_loader.get_country_by_code(country_code.upper())

        if not country:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_COUNTRY",
                    "message": f"Country code '{country_code}' not supported"
                }
            }

        cities = country.get("major_cities", [])
        query_lower = query.lower()

        # Search cities
        matching_cities = [
            city for city in cities
            if query_lower in city.lower()
        ][:limit]

        return {
            "success": True,
            "data": {
                "cities": matching_cities,
                "query": query,
                "country_code": country_code.upper(),
                "country_name": country["name"],
                "total_matches": len(matching_cities)
            },
            "metadata": {
                "step": 3,
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in search_cities: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }