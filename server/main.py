#!/usr/bin/env python3
"""
Buycycle Listing MCP Server

This is the main entry point for the Buycycle bike listing MCP server.
It provides structured tools for AI agents to guide users through
the 6-step bike listing process on the Buycycle marketplace.
"""
import asyncio
import logging
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import our tools and data loader
from .data_loader import data_loader
from .validators import validator
from . import tools
from .tools import step1_tools, step2_tools, step3_tools, step4_tools, step5_tools, step6_tools

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Create the main MCP server
server = Server("buycycle-listing-mcp")


@server.list_tools()
async def handle_list_tools():
    """
    List all available tools for the Buycycle listing process.

    Tools are organized by the 6-step listing process:
    - Step 1: Bike type, brand, and model selection
    - Step 2: Bike details and specifications
    - Step 3: Location and shipping
    - Step 4: Components and upgrades
    - Step 5: Pricing and financial details
    - Step 6: Photos and media
    """
    tools = [
        # Step 1: Bike Type, Brand, and Model Selection
        {
            "name": "list_bike_types",
            "description": "Get all available bike types with descriptions",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "list_brands",
            "description": "Get all available bike brands",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of brands to return",
                        "default": 50
                    }
                },
                "required": []
            }
        },
        {
            "name": "search_brands",
            "description": "Search for bike brands by name",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for brand name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "list_models_for_brand",
            "description": "Get all models for a specific brand and bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "brand_id": {
                        "type": "string",
                        "description": "Brand identifier"
                    },
                    "bike_type_id": {
                        "type": "string",
                        "description": "Bike type identifier"
                    }
                },
                "required": ["brand_id", "bike_type_id"]
            }
        },
        {
            "name": "get_model_details",
            "description": "Get detailed information about a specific bike model",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "brand_id": {"type": "string", "description": "Brand identifier"},
                    "model_id": {"type": "string", "description": "Model identifier"},
                    "bike_type_id": {"type": "string", "description": "Bike type identifier"}
                },
                "required": ["brand_id", "model_id", "bike_type_id"]
            }
        },
        {
            "name": "validate_step1_selection",
            "description": "Validate Step 1 selections (bike type, brand, and model)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Selected bike type"},
                    "brand_id": {"type": "string", "description": "Selected brand"},
                    "model_id": {"type": "string", "description": "Selected model"}
                },
                "required": ["bike_type_id", "brand_id", "model_id"]
            }
        },

        # Step 2: Bike Details and Specifications
        {
            "name": "get_step2_detail_options",
            "description": "Get all available detail options for Step 2 based on bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get options for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "get_frame_materials",
            "description": "Get all available frame materials with details",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_motor_options",
            "description": "Get all e-bike motor options (brands, positions, battery capacities)",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_suspension_options",
            "description": "Get suspension type options and travel ranges",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_drivetrain_options",
            "description": "Get drivetrain component options (shifters, brakes)",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "check_field_requirements",
            "description": "Get field requirements for a specific bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to check requirements for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "validate_bike_details",
            "description": "Validate bike details for Step 2",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type these details are for"},
                    "details": {
                        "type": "object",
                        "description": "Dictionary of bike details to validate",
                        "additionalProperties": True
                    }
                },
                "required": ["bike_type_id", "details"]
            }
        },

        # Step 3: Location and Shipping
        {
            "name": "list_countries",
            "description": "Get all supported countries for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_country_details",
            "description": "Get detailed information about a specific country",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "ISO country code"}
                },
                "required": ["country_code"]
            }
        },
        {
            "name": "get_cities_for_country",
            "description": "Get major cities for a specific country",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "ISO country code"},
                    "limit": {"type": "integer", "description": "Maximum cities to return", "default": 20}
                },
                "required": ["country_code"]
            }
        },
        {
            "name": "search_cities",
            "description": "Search for cities within a country",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "ISO country code"},
                    "query": {"type": "string", "description": "City name or partial name"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": ["country_code", "query"]
            }
        },
        {
            "name": "get_shipping_options",
            "description": "Get available shipping options for a country",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "ISO country code"}
                },
                "required": ["country_code"]
            }
        },
        {
            "name": "validate_location",
            "description": "Validate Step 3 location and shipping information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string", "description": "Selected country code"},
                    "city": {"type": "string", "description": "Selected city"},
                    "postal_code": {"type": "string", "description": "Postal/ZIP code"},
                    "shipping_options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Selected shipping method IDs"
                    }
                },
                "required": ["country_code", "city", "postal_code", "shipping_options"]
            }
        },

        # Step 4: Components and Upgrades
        {
            "name": "list_component_categories",
            "description": "Get all component categories available for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_components_for_bike_type",
            "description": "Get components appropriate for a specific bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get components for"},
                    "category": {"type": "string", "description": "Optional specific category to filter by"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "get_wheel_options",
            "description": "Get wheel options for a specific bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get wheel options for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "get_tire_options",
            "description": "Get tire options for a specific bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get tire options for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "get_saddle_options",
            "description": "Get saddle options for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_handlebar_options",
            "description": "Get handlebar options for a specific bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get handlebar options for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "get_pedal_options",
            "description": "Get pedal options for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_upgrade_categories",
            "description": "Get available upgrade categories for bike components",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "validate_components",
            "description": "Validate Step 4 component specifications",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type these components are for"},
                    "components": {
                        "type": "object",
                        "description": "Dictionary of component specifications",
                        "additionalProperties": True
                    }
                },
                "required": ["bike_type_id", "components"]
            }
        },

        # Step 5: Pricing and Financial Details
        {
            "name": "list_currencies",
            "description": "Get all supported currencies for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_currency_details",
            "description": "Get detailed information about a specific currency",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "currency_code": {"type": "string", "description": "ISO currency code"}
                },
                "required": ["currency_code"]
            }
        },
        {
            "name": "get_payment_methods",
            "description": "Get available payment methods for a specific currency",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "currency_code": {"type": "string", "description": "ISO currency code"}
                },
                "required": ["currency_code"]
            }
        },
        {
            "name": "get_price_suggestions",
            "description": "Get AI-powered price suggestions based on bike details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type"},
                    "brand_id": {"type": "string", "description": "Bike brand"},
                    "model_id": {"type": "string", "description": "Bike model"},
                    "year": {"type": "integer", "description": "Manufacturing year"},
                    "condition": {"type": "string", "description": "Bike condition"}
                },
                "required": ["bike_type_id", "brand_id", "model_id", "year", "condition"]
            }
        },
        {
            "name": "calculate_fees",
            "description": "Calculate estimated platform and payment processing fees",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "asking_price": {"type": "number", "description": "Listing price"},
                    "currency_code": {"type": "string", "description": "Currency code", "default": "EUR"}
                },
                "required": ["asking_price"]
            }
        },
        {
            "name": "validate_pricing",
            "description": "Validate Step 5 pricing and financial details",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "currency_code": {"type": "string", "description": "Selected currency code"},
                    "asking_price": {"type": "number", "description": "Listing price"},
                    "payment_methods": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Accepted payment method IDs"
                    },
                    "original_price": {"type": "number", "description": "Optional original MSRP"},
                    "negotiable": {"type": "boolean", "description": "Whether price is negotiable", "default": False}
                },
                "required": ["currency_code", "asking_price", "payment_methods"]
            }
        },

        # Step 6: Photos and Media
        {
            "name": "get_photo_requirements",
            "description": "Get photo requirements and guidelines for bike listings",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_photo_tips",
            "description": "Get photography tips specific to a bike type",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type to get photography tips for"}
                },
                "required": ["bike_type_id"]
            }
        },
        {
            "name": "suggest_photo_descriptions",
            "description": "Suggest photo descriptions and order for optimal listing presentation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bike_type_id": {"type": "string", "description": "Bike type for targeted suggestions"},
                    "photo_count": {"type": "integer", "description": "Number of photos planned"}
                },
                "required": ["bike_type_id", "photo_count"]
            }
        },
        {
            "name": "validate_photo_order",
            "description": "Validate photo order and selection for Step 6",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "photos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "description": {"type": "string"},
                                "order": {"type": "integer"},
                                "is_main": {"type": "boolean"}
                            },
                            "required": ["description", "order", "is_main"]
                        },
                        "description": "List of photo objects with order and descriptions"
                    }
                },
                "required": ["photos"]
            }
        }
    ]

    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    Handle tool calls by routing to appropriate tool functions.
    """
    try:
        # Step 1 tools
        if name == "list_bike_types":
            return await step1_tools.list_bike_types()
        elif name == "list_brands":
            limit = arguments.get("limit", 50)
            return await step1_tools.list_brands(limit)
        elif name == "search_brands":
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            return await step1_tools.search_brands(query, limit)
        elif name == "list_models_for_brand":
            brand_id = arguments["brand_id"]
            bike_type_id = arguments["bike_type_id"]
            return await step1_tools.list_models_for_brand(brand_id, bike_type_id)
        elif name == "get_model_details":
            brand_id = arguments["brand_id"]
            model_id = arguments["model_id"]
            bike_type_id = arguments["bike_type_id"]
            return await step1_tools.get_model_details(brand_id, model_id, bike_type_id)
        elif name == "validate_step1_selection":
            bike_type_id = arguments["bike_type_id"]
            brand_id = arguments["brand_id"]
            model_id = arguments["model_id"]
            return await step1_tools.validate_step1_selection(bike_type_id, brand_id, model_id)

        # Step 2 tools
        elif name == "get_step2_detail_options":
            bike_type_id = arguments["bike_type_id"]
            return await step2_tools.get_step2_detail_options(bike_type_id)
        elif name == "get_frame_materials":
            return await step2_tools.get_frame_materials()
        elif name == "get_motor_options":
            return await step2_tools.get_motor_options()
        elif name == "get_suspension_options":
            return await step2_tools.get_suspension_options()
        elif name == "get_drivetrain_options":
            return await step2_tools.get_drivetrain_options()
        elif name == "check_field_requirements":
            bike_type_id = arguments["bike_type_id"]
            return await step2_tools.check_field_requirements(bike_type_id)
        elif name == "validate_bike_details":
            bike_type_id = arguments["bike_type_id"]
            details = arguments["details"]
            return await step2_tools.validate_bike_details(bike_type_id, details)

        # Step 3 tools
        elif name == "list_countries":
            return await step3_tools.list_countries()
        elif name == "get_country_details":
            country_code = arguments["country_code"]
            return await step3_tools.get_country_details(country_code)
        elif name == "get_cities_for_country":
            country_code = arguments["country_code"]
            limit = arguments.get("limit", 20)
            return await step3_tools.get_cities_for_country(country_code, limit)
        elif name == "search_cities":
            country_code = arguments["country_code"]
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            return await step3_tools.search_cities(country_code, query, limit)
        elif name == "get_shipping_options":
            country_code = arguments["country_code"]
            return await step3_tools.get_shipping_options(country_code)
        elif name == "validate_location":
            country_code = arguments["country_code"]
            city = arguments["city"]
            postal_code = arguments["postal_code"]
            shipping_options = arguments["shipping_options"]
            return await step3_tools.validate_location(country_code, city, postal_code, shipping_options)

        # Step 4 tools
        elif name == "list_component_categories":
            return await step4_tools.list_component_categories()
        elif name == "get_components_for_bike_type":
            bike_type_id = arguments["bike_type_id"]
            category = arguments.get("category")
            return await step4_tools.get_components_for_bike_type(bike_type_id, category)
        elif name == "get_wheel_options":
            bike_type_id = arguments["bike_type_id"]
            return await step4_tools.get_wheel_options(bike_type_id)
        elif name == "get_tire_options":
            bike_type_id = arguments["bike_type_id"]
            return await step4_tools.get_tire_options(bike_type_id)
        elif name == "get_saddle_options":
            return await step4_tools.get_saddle_options()
        elif name == "get_handlebar_options":
            bike_type_id = arguments["bike_type_id"]
            return await step4_tools.get_handlebar_options(bike_type_id)
        elif name == "get_pedal_options":
            return await step4_tools.get_pedal_options()
        elif name == "get_upgrade_categories":
            return await step4_tools.get_upgrade_categories()
        elif name == "validate_components":
            bike_type_id = arguments["bike_type_id"]
            components = arguments["components"]
            return await step4_tools.validate_components(bike_type_id, components)

        # Step 5 tools
        elif name == "list_currencies":
            return await step5_tools.list_currencies()
        elif name == "get_currency_details":
            currency_code = arguments["currency_code"]
            return await step5_tools.get_currency_details(currency_code)
        elif name == "get_payment_methods":
            currency_code = arguments["currency_code"]
            return await step5_tools.get_payment_methods(currency_code)
        elif name == "get_price_suggestions":
            bike_type_id = arguments["bike_type_id"]
            brand_id = arguments["brand_id"]
            model_id = arguments["model_id"]
            year = arguments["year"]
            condition = arguments["condition"]
            return await step5_tools.get_price_suggestions(bike_type_id, brand_id, model_id, year, condition)
        elif name == "calculate_fees":
            asking_price = arguments["asking_price"]
            currency_code = arguments.get("currency_code", "EUR")
            return await step5_tools.calculate_fees(asking_price, currency_code)
        elif name == "validate_pricing":
            currency_code = arguments["currency_code"]
            asking_price = arguments["asking_price"]
            payment_methods = arguments["payment_methods"]
            original_price = arguments.get("original_price")
            negotiable = arguments.get("negotiable", False)
            return await step5_tools.validate_pricing(currency_code, asking_price, payment_methods, original_price, negotiable)

        # Step 6 tools
        elif name == "get_photo_requirements":
            return await step6_tools.get_photo_requirements()
        elif name == "get_photo_tips":
            bike_type_id = arguments["bike_type_id"]
            return await step6_tools.get_photo_tips(bike_type_id)
        elif name == "suggest_photo_descriptions":
            bike_type_id = arguments["bike_type_id"]
            photo_count = arguments["photo_count"]
            return await step6_tools.suggest_photo_descriptions(bike_type_id, photo_count)
        elif name == "validate_photo_order":
            photos = arguments["photos"]
            return await step6_tools.validate_photo_order(photos)

        else:
            return {
                "success": False,
                "error": {
                    "code": "UNKNOWN_TOOL",
                    "message": f"Tool '{name}' not found"
                }
            }

    except Exception as e:
        logger.error(f"Error handling tool call '{name}': {e}")
        return {
            "success": False,
            "error": {
                "code": "TOOL_EXECUTION_ERROR",
                "message": str(e)
            }
        }


async def main():
    """Main entry point for the MCP server."""
    try:
        # Load all data at startup
        logger.info("Starting Buycycle Listing MCP Server...")
        await data_loader.load_all()
        logger.info("Data loading complete. Server ready.")

        # Run the server
        await stdio_server(server)

    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())