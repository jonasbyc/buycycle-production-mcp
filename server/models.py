"""Pydantic models for type safety and validation."""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"


class MCPResponse(BaseModel):
    """Standard MCP response format."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPError(BaseModel):
    """Standard MCP error format."""
    success: bool = False
    error: Dict[str, Any]


class BikeType(BaseModel):
    """Bike type model."""
    id: str
    name: str
    description: str
    category: str


class Brand(BaseModel):
    """Bike brand model."""
    id: str
    name: str
    logo_url: Optional[str] = None
    country: Optional[str] = None


class Model(BaseModel):
    """Bike model/family model."""
    id: str
    name: str
    brand_id: str
    bike_type_id: str
    year_range: List[int]
    msrp_range: Optional[Dict[str, int]] = None


class BikeDetails(BaseModel):
    """Step 2: Bike details and specifications."""
    year: int = Field(ge=1990, le=2025)
    frame_material_code: str
    frame_size: str
    color: str
    condition: str

    # Conditional fields for e-bikes
    motor_brand: Optional[str] = None
    battery_capacity_wh: Optional[int] = None
    motor_position: Optional[str] = None

    # Conditional fields for suspension
    suspension_type: Optional[str] = None
    front_suspension_travel_mm: Optional[int] = None
    rear_suspension_travel_mm: Optional[int] = None

    # Drivetrain
    shifter_brand: Optional[str] = None
    shifter_model: Optional[str] = None
    cassette_speeds: Optional[int] = None

    # Brakes
    brake_type: str
    brake_brand: Optional[str] = None


class Location(BaseModel):
    """Step 3: Location and shipping."""
    country_code: str = Field(min_length=2, max_length=3)
    city: str
    postal_code: str
    shipping_options: List[str]


class Components(BaseModel):
    """Step 4: Components and upgrades."""
    wheels: Dict[str, str]
    tires: Dict[str, str]
    saddle: Dict[str, str]
    handlebars: Dict[str, str]
    pedals: Dict[str, str]
    upgrades: List[Dict[str, str]] = []


class Pricing(BaseModel):
    """Step 5: Pricing and financial details."""
    currency_code: str = Field(min_length=3, max_length=3)
    asking_price: float = Field(gt=0)
    original_price: Optional[float] = None
    negotiable: bool = False
    payment_methods: List[str]


class Photo(BaseModel):
    """Photo model for step 6."""
    url: str
    description: str
    order: int = Field(ge=1)
    is_main: bool = False


class Photos(BaseModel):
    """Step 6: Photos and media."""
    photos: List[Photo] = Field(min_length=3, max_length=20)
    main_photo_index: int = Field(ge=0)

    @field_validator('photos')
    def validate_main_photo(cls, v, values):
        if 'main_photo_index' in values.data:
            main_index = values.data['main_photo_index']
            if main_index >= len(v):
                raise ValueError("main_photo_index out of range")
        return v


class CompleteListing(BaseModel):
    """Complete bike listing model."""
    # Step 1
    bike_type_id: str
    brand_id: str
    model_id: str

    # Step 2
    details: BikeDetails

    # Step 3
    location: Location

    # Step 4
    components: Components

    # Step 5
    pricing: Pricing

    # Step 6
    photos: Photos

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    listing_id: Optional[str] = None