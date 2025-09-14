# Buycycle Listing MCP Server - Project Specification

## Project Overview

This project implements a Model Context Protocol (MCP) server for the Buycycle bike marketplace listing system. The server provides AI agents with structured access to create bike listings through a 6-step process, optimized for low latency and high performance.

## Use Cases

### Primary Use Cases
1. **Agentic Listing**: AI agents chat with users to guide them through creating a complete bike listing
2. **Mirroring Service**: AI agents parse existing listings from other marketplaces and map them to Buycycle format (handled by external agents - this MCP provides the structure)

### Performance Requirements
- **Target Response Time**: <1 second per tool call
- **Architecture**: Short-chained requests to minimize context window usage
- **Data Access Pattern**: Granular, step-by-step data retrieval (brands → models → variants)

## Technical Architecture

### Core Components
- **Transport**: STDIO (Standard MCP transport)
- **Data Source**: Static JSON files (no live API integration in v1)
- **Validation**: Strict - reject invalid combinations
- **State Management**: Stateless - AI client handles all state
- **Language**: Python with `mcp` package
- **Performance**: Async/await throughout

### MCP Server Structure
```
buycycle-listing-mcp/
├── server/
│   ├── __init__.py
│   ├── main.py              # MCP server entry point
│   ├── tools/               # Individual tool implementations
│   │   ├── __init__.py
│   │   ├── step1_tools.py   # Bike types, brands, models
│   │   ├── step2_tools.py   # Bike details
│   │   ├── step3_tools.py   # Location
│   │   ├── step4_tools.py   # Components
│   │   ├── step5_tools.py   # Pricing
│   │   └── step6_tools.py   # Photos
│   ├── data_loader.py       # JSON data loading and caching
│   ├── validators.py        # Strict validation logic
│   └── models.py           # Pydantic models for type safety
├── data/                    # Static JSON data files
│   ├── brands.json
│   ├── models_by_brand.json
│   ├── bike_types.json
│   ├── conditional_fields.json
│   ├── step2_details.json
│   ├── countries.json
│   ├── components.json
│   └── currencies.json
├── tests/
├── examples/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 6-Step Listing Process

### Step 1: Bike Type, Brand, and Model Selection
**Purpose**: Identify the specific bike being listed

**Tools**:
- `list_bike_types()` → Returns available bike types (road, mountain, e-bike, etc.)
- `list_brands()` → Returns all available bike brands
- `list_models(brand_id: str)` → Returns models for specific brand
- `get_model_details(brand_id: str, model_id: str)` → Returns detailed model information

**Required Fields**:
- `bike_type_id`: Selected bike type
- `brand_id`: Selected brand
- `model_id`: Selected model/family

**Validation**:
- Brand must exist in brands.json
- Model must exist for specified brand
- Bike type must be compatible with brand/model

### Step 2: Bike Details and Specifications
**Purpose**: Capture detailed bike specifications

**Tools**:
- `get_detail_options(bike_type_id: str)` → Returns available options based on bike type
- `validate_bike_details(details: dict)` → Validates detail combination

**Required Fields** (conditional based on bike type):
- `year`: Manufacturing year
- `frame_material_code`: carbon, aluminum, steel, titanium
- `frame_size`: Size designation
- `color`: Bike color
- `condition`: new, like-new, very-good, good, fair
- **For E-bikes only**:
  - `motor_brand`: Bosch, Shimano, Yamaha, Brose, etc.
  - `battery_capacity_wh`: Battery capacity in Wh
  - `motor_position`: mid-drive, hub-rear, hub-front
- **For suspension bikes**:
  - `suspension_type`: hardtail, full-suspension, rigid
  - `front_suspension_travel_mm`: Travel in mm
  - `rear_suspension_travel_mm`: Travel in mm (full-suspension only)
- **Drivetrain**:
  - `shifter_brand`: Shimano, SRAM, Campagnolo, etc.
  - `shifter_model`: Specific shifter model
  - `cassette_speeds`: Number of speeds
- **Brakes**:
  - `brake_type`: disc-hydraulic, disc-mechanical, rim
  - `brake_brand`: Shimano, SRAM, etc.

**Validation**:
- All fields must be from predefined options
- Conditional field requirements based on bike type
- Compatibility checks between components

### Step 3: Location and Shipping
**Purpose**: Define where the bike is located and shipping options

**Tools**:
- `list_countries()` → Returns supported countries
- `list_cities(country_code: str)` → Returns cities for country
- `get_shipping_options(country_code: str)` → Returns available shipping methods

**Required Fields**:
- `country_code`: ISO country code
- `city`: City name
- `postal_code`: Postal/ZIP code
- `shipping_options`: Array of selected shipping methods

**Validation**:
- Country must be supported
- City must exist in country
- Shipping options must be available for country

### Step 4: Components and Upgrades
**Purpose**: Detail specific components and any upgrades

**Tools**:
- `list_component_categories()` → Returns component categories
- `list_components(category: str, bike_type_id: str)` → Returns components for category/bike type
- `validate_component_compatibility(components: list)` → Checks component compatibility

**Required Fields**:
- `wheels`: Wheel specifications
- `tires`: Tire brand and model
- `saddle`: Saddle details
- `handlebars`: Handlebar type and brand
- `pedals`: Pedal type and brand
- `upgrades`: List of any upgrades from stock

**Validation**:
- Components must be appropriate for bike type
- Upgrades must be compatible with base bike
- No conflicting component selections

### Step 5: Pricing and Financial Details
**Purpose**: Set pricing and payment options

**Tools**:
- `list_currencies()` → Returns supported currencies
- `get_price_suggestions(bike_details: dict)` → Returns AI-powered price suggestions
- `validate_pricing(price_data: dict)` → Validates price reasonableness

**Required Fields**:
- `currency_code`: ISO currency code
- `asking_price`: Listing price
- `original_price`: Original MSRP (if known)
- `negotiable`: Boolean if price is negotiable
- `payment_methods`: Accepted payment methods

**Validation**:
- Currency must be supported
- Price must be reasonable (within algorithm bounds)
- Payment methods must be valid for region

### Step 6: Photos and Media
**Purpose**: Handle photo uploads and media assets

**Tools**:
- `get_photo_requirements()` → Returns photo requirements and limits
- `validate_photo_order(photo_list: list)` → Validates photo sequence
- `get_photo_tips()` → Returns photography best practices

**Required Fields**:
- `photos`: Array of photo objects with order and descriptions
- `main_photo_index`: Index of primary photo
- `photo_descriptions`: Descriptions for each photo

**Validation**:
- Minimum 3 photos required
- Maximum 20 photos allowed
- Main photo must show full bike
- All photos must meet size/format requirements

## Conditional Fields Configuration

### File: `data/conditional_fields.json`
```json
{
  "bike_types": {
    "road": {
      "required_fields": ["frame_material", "drivetrain", "brakes"],
      "optional_fields": ["aerodynamic_features"],
      "excluded_fields": ["motor_brand", "battery_capacity", "suspension_travel"]
    },
    "mountain": {
      "required_fields": ["frame_material", "suspension_type", "drivetrain", "brakes"],
      "conditional_fields": {
        "full_suspension": ["rear_suspension_travel"],
        "hardtail": ["front_suspension_travel"]
      }
    },
    "e_bike": {
      "required_fields": ["motor_brand", "battery_capacity", "motor_position", "frame_material"],
      "conditional_fields": {
        "mountain_ebike": ["suspension_type", "suspension_travel"],
        "road_ebike": ["aerodynamic_features"]
      }
    }
  }
}
```

## Tool Design for Performance

### Chaining Strategy
1. **Minimize Context**: Each tool returns only essential data for next step
2. **Granular Access**: Separate tools for each data subset
3. **Lazy Loading**: Only fetch data when specifically requested
4. **Structured Responses**: Consistent JSON schema for all responses

### Example Tool Chain for Step 1:
```
AI Agent: list_bike_types()
→ Returns: ["road", "mountain", "e-bike", "gravel", "city"]

AI Agent: list_brands()
→ Returns: ["Trek", "Specialized", "Canyon", ...] (first 50)

User: "I have a Trek mountain bike"
AI Agent: list_models(brand_id="trek", bike_type="mountain")
→ Returns: Trek mountain bike models only

User: "It's a Trek Fuel EX 8"
AI Agent: get_model_details(brand_id="trek", model_id="fuel-ex-8")
→ Returns: Detailed specs for validation
```

## Data Schema Standards

### Response Format
All tools return JSON with this structure:
```json
{
  "success": true,
  "data": {...},
  "metadata": {
    "step": 1,
    "next_suggested_tools": ["list_models"],
    "validation_status": "pending"
  }
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Brand 'xyz' not found",
    "details": {...}
  }
}
```

## Performance Specifications

### Response Time Targets
- Simple data retrieval: <200ms
- Complex validation: <500ms
- Full tool chain completion: <5s total

### Memory Usage
- Keep all JSON data in memory for fast access
- Total memory footprint: <50MB
- No disk I/O during tool execution

### Caching Strategy
- Load all data at server startup
- No runtime data fetching
- Immutable data assumption

## Validation Rules

### Strict Validation Requirements
1. **Existence Checks**: All IDs must exist in reference data
2. **Compatibility Checks**: Components must be compatible with bike type
3. **Range Validation**: Numeric values within reasonable bounds
4. **Format Validation**: Strings match expected patterns
5. **Completeness**: All required fields present and valid

### Error Handling
- Return detailed error messages
- Include suggestions for fixes
- Never auto-correct user input
- Fail fast on validation errors

## Integration Guidelines

### For AI Agents
1. **State Management**: Maintain listing state in agent, not MCP server
2. **Error Recovery**: Handle validation errors gracefully
3. **User Experience**: Guide users through validation failures
4. **Context Optimization**: Use tool chaining to minimize context usage

### For Mirroring Services
1. **Data Mapping**: Map external data to Buycycle schema before validation
2. **Confidence Scoring**: Rate mapping confidence for user review
3. **Fallback Strategy**: Ask users for clarification on low-confidence mappings

## Testing Strategy

### Unit Tests
- Each tool individually tested
- Validation logic thoroughly covered
- Edge cases and error conditions

### Integration Tests
- Complete listing workflows
- Tool chaining scenarios
- Performance benchmarks

### Example Conversations
- Document common usage patterns
- Include error scenarios
- Show optimal tool usage

## Future Enhancements

### Version 2 Considerations
- Live API integration
- Regional variations
- Multi-language support
- Enhanced validation rules
- Performance monitoring
- Caching strategies

### Extensibility
- Plugin architecture for new bike types
- Custom validation rules
- External data source integration
- Webhook notifications

---

## Implementation Checklist

- [ ] Set up MCP server with STDIO transport
- [ ] Create all JSON data files with realistic data
- [ ] Implement all 26+ tools across 6 steps
- [ ] Add comprehensive validation logic
- [ ] Create conditional fields configuration
- [ ] Write unit tests for all tools
- [ ] Create integration test suites
- [ ] Document example conversations
- [ ] Performance testing and optimization
- [ ] Create deployment documentation

## Success Metrics

- All tools respond within target times
- 100% validation accuracy
- Zero false positives in compatibility checks
- Complete listing creation in <2 minutes via agent
- Memory usage stays under 50MB
- All tests passing with >95% coverage

---

*Last Updated: 2025-09-14*
*Version: 1.0 Specification*