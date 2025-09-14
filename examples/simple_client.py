#!/usr/bin/env python3
"""
Simple MCP client example for testing the Buycycle Listing MCP Server.

This demonstrates how to connect to and use the MCP server tools
for creating a bike listing through the 6-step process.
"""
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def test_step1_flow():
    """Test Step 1: Bike type, brand, and model selection."""
    print("\n=== STEP 1: Bike Type, Brand, and Model Selection ===")

    async with stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "server.main"]
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List bike types
            print("\n1. Listing bike types...")
            result = await session.call_tool("list_bike_types", {})
            print(f"Available bike types: {len(result.content[0].text)}")

            # List brands
            print("\n2. Listing brands (limited to 10)...")
            result = await session.call_tool("list_brands", {"limit": 10})
            print(f"First 10 brands retrieved")

            # Search for a specific brand
            print("\n3. Searching for 'Trek' brand...")
            result = await session.call_tool("search_brands", {"query": "Trek"})
            print(f"Search results for Trek")

            # Get models for Trek mountain bikes
            print("\n4. Getting Trek mountain bike models...")
            result = await session.call_tool("list_models_for_brand", {
                "brand_id": "trek",
                "bike_type_id": "mountain"
            })
            print(f"Trek mountain bike models retrieved")

            # Get details for specific model
            print("\n5. Getting details for Trek Fuel EX...")
            result = await session.call_tool("get_model_details", {
                "brand_id": "trek",
                "model_id": "fuel_ex",
                "bike_type_id": "mountain"
            })
            print(f"Model details retrieved")

            # Validate the selection
            print("\n6. Validating Step 1 selection...")
            result = await session.call_tool("validate_step1_selection", {
                "bike_type_id": "mountain",
                "brand_id": "trek",
                "model_id": "fuel_ex"
            })
            print(f"Step 1 validation: {'PASSED' if result.content[0].text else 'FAILED'}")


async def test_step2_flow():
    """Test Step 2: Bike details and specifications."""
    print("\n=== STEP 2: Bike Details and Specifications ===")

    async with stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "server.main"]
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get detail options for mountain bike
            print("\n1. Getting detail options for mountain bike...")
            result = await session.call_tool("get_step2_detail_options", {
                "bike_type_id": "mountain"
            })
            print("Detail options retrieved")

            # Get frame materials
            print("\n2. Getting frame materials...")
            result = await session.call_tool("get_frame_materials", {})
            print("Frame materials retrieved")

            # Get suspension options
            print("\n3. Getting suspension options...")
            result = await session.call_tool("get_suspension_options", {})
            print("Suspension options retrieved")

            # Validate bike details
            print("\n4. Validating bike details...")
            details = {
                "year": 2022,
                "frame_material_code": "aluminum",
                "frame_size": "l",
                "color": "blue",
                "condition": "very_good",
                "suspension_type": "full_suspension",
                "front_suspension_travel_mm": 150,
                "rear_suspension_travel_mm": 140,
                "brake_type": "disc_hydraulic",
                "brake_brand": "shimano"
            }
            result = await session.call_tool("validate_bike_details", {
                "bike_type_id": "mountain",
                "details": details
            })
            print(f"Step 2 validation: {'PASSED' if result.content[0].text else 'FAILED'}")


async def test_complete_listing_flow():
    """Test a complete listing workflow through all 6 steps."""
    print("\n=== COMPLETE LISTING WORKFLOW ===")

    async with stdio_client(
        StdioServerParameters(
            command="python",
            args=["-m", "server.main"]
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 1: Basic bike selection
            print("\nStep 1: Selecting Trek Fuel EX mountain bike...")
            await session.call_tool("validate_step1_selection", {
                "bike_type_id": "mountain",
                "brand_id": "trek",
                "model_id": "fuel_ex"
            })

            # Step 2: Bike details
            print("Step 2: Adding bike details...")
            details = {
                "year": 2023,
                "frame_material_code": "carbon",
                "frame_size": "l",
                "color": "black",
                "condition": "like_new",
                "suspension_type": "full_suspension",
                "front_suspension_travel_mm": 150,
                "rear_suspension_travel_mm": 140,
                "brake_type": "disc_hydraulic"
            }
            await session.call_tool("validate_bike_details", {
                "bike_type_id": "mountain",
                "details": details
            })

            # Step 3: Location
            print("Step 3: Setting location...")
            await session.call_tool("validate_location", {
                "country_code": "DE",
                "city": "Berlin",
                "postal_code": "10115",
                "shipping_options": ["pickup", "domestic_shipping"]
            })

            # Step 4: Components
            print("Step 4: Specifying components...")
            components = {
                "wheels": {"brand": "DT Swiss", "model": "XM 1501"},
                "tires": {"brand": "Maxxis", "model": "Minion DHR II"},
                "saddle": {"brand": "Specialized", "model": "Power"},
                "handlebars": {"brand": "Race Face", "model": "Aeffect R"},
                "pedals": {"brand": "Shimano", "model": "PD-M8020"}
            }
            await session.call_tool("validate_components", {
                "bike_type_id": "mountain",
                "components": components
            })

            # Step 5: Pricing
            print("Step 5: Setting pricing...")
            await session.call_tool("validate_pricing", {
                "currency_code": "EUR",
                "asking_price": 3500.0,
                "payment_methods": ["bank_transfer", "paypal"],
                "negotiable": True
            })

            # Step 6: Photos
            print("Step 6: Organizing photos...")
            photos = [
                {"description": "Full bike profile view", "order": 1, "is_main": True},
                {"description": "Full bike front view", "order": 2, "is_main": False},
                {"description": "Drivetrain closeup", "order": 3, "is_main": False},
                {"description": "Suspension detail", "order": 4, "is_main": False},
                {"description": "Cockpit view", "order": 5, "is_main": False}
            ]
            await session.call_tool("validate_photo_order", {
                "photos": photos
            })

            print("\n✅ Complete listing workflow completed successfully!")


async def main():
    """Run all example tests."""
    print("Buycycle Listing MCP Server - Example Client")
    print("=" * 50)

    try:
        await test_step1_flow()
        await test_step2_flow()
        await test_complete_listing_flow()

        print("\n🎉 All tests completed successfully!")
        print("\nThe MCP server is working correctly and ready for use with AI agents.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the MCP server dependencies are installed and the server can start.")


if __name__ == "__main__":
    asyncio.run(main())