"""Strict validation logic for Buycycle listings."""
from typing import Dict, List, Any, Optional, Tuple
from .data_loader import data_loader
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class BikeListingValidator:
    """Strict validator for bike listing data."""

    def __init__(self):
        self.data = data_loader

    async def validate_step1(self, bike_type_id: str, brand_id: str, model_id: str) -> Dict[str, Any]:
        """Validate Step 1: Bike type, brand, and model selection."""
        errors = []

        # Validate bike type
        if not self.data.validate_bike_type_exists(bike_type_id):
            errors.append({
                "field": "bike_type_id",
                "code": "INVALID_BIKE_TYPE",
                "message": f"Bike type '{bike_type_id}' does not exist",
                "valid_values": list(self.data.get_bike_types().keys())
            })

        # Validate brand
        if not self.data.validate_brand_exists(brand_id):
            errors.append({
                "field": "brand_id",
                "code": "INVALID_BRAND",
                "message": f"Brand '{brand_id}' does not exist",
                "valid_values": list(self.data.get_brands().keys())
            })

        # Validate model (only if brand and bike_type are valid)
        if not errors and not self.data.validate_model_exists(brand_id, model_id, bike_type_id):
            available_models = self.data.get_brand_models_by_type(brand_id, bike_type_id)
            model_ids = [m["id"] for m in available_models]
            errors.append({
                "field": "model_id",
                "code": "INVALID_MODEL",
                "message": f"Model '{model_id}' does not exist for brand '{brand_id}' and bike type '{bike_type_id}'",
                "valid_values": model_ids
            })

        if errors:
            raise ValidationError(
                "Step 1 validation failed",
                "STEP1_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 1}

    async def validate_step2(self, bike_type_id: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Step 2: Bike details and specifications."""
        errors = []
        conditional_fields = self.data.get_conditional_fields()
        step2_options = self.data.get_step2_details()
        bike_type_rules = conditional_fields.get("bike_types", {}).get(bike_type_id, {})

        # Check required fields
        required_fields = bike_type_rules.get("required_fields", [])
        for field in required_fields:
            if field not in details or details[field] is None:
                errors.append({
                    "field": field,
                    "code": "MISSING_REQUIRED_FIELD",
                    "message": f"Required field '{field}' is missing for bike type '{bike_type_id}'"
                })

        # Check excluded fields
        excluded_fields = bike_type_rules.get("excluded_fields", [])
        for field in excluded_fields:
            if field in details and details[field] is not None:
                errors.append({
                    "field": field,
                    "code": "EXCLUDED_FIELD_PRESENT",
                    "message": f"Field '{field}' is not allowed for bike type '{bike_type_id}'"
                })

        # Validate specific fields
        self._validate_year(details.get("year"), errors)
        self._validate_frame_material(details.get("frame_material_code"), step2_options, errors)
        self._validate_condition(details.get("condition"), step2_options, errors)
        self._validate_frame_size(details.get("frame_size"), bike_type_id, step2_options, errors)
        self._validate_color(details.get("color"), step2_options, errors)

        # Conditional validations
        if bike_type_id == "e_bike" or "motor" in str(details):
            self._validate_motor_fields(details, step2_options, errors)

        if "suspension" in str(details) or bike_type_id == "mountain":
            self._validate_suspension_fields(details, errors)

        # Validate brake and drivetrain
        self._validate_brake_fields(details, step2_options, errors)
        self._validate_drivetrain_fields(details, step2_options, errors)

        if errors:
            raise ValidationError(
                "Step 2 validation failed",
                "STEP2_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 2}

    def _validate_year(self, year: Any, errors: List[Dict]) -> None:
        """Validate year field."""
        if year is None:
            return

        step2_options = self.data.get_step2_details()
        valid_years = step2_options.get("years", [])

        if not isinstance(year, int) or year not in valid_years:
            errors.append({
                "field": "year",
                "code": "INVALID_YEAR",
                "message": f"Year must be one of: {valid_years}",
                "valid_values": valid_years
            })

    def _validate_frame_material(self, material: Any, options: Dict, errors: List[Dict]) -> None:
        """Validate frame material."""
        if material is None:
            return

        valid_materials = list(options.get("frame_materials", {}).keys())
        if material not in valid_materials:
            errors.append({
                "field": "frame_material_code",
                "code": "INVALID_FRAME_MATERIAL",
                "message": f"Frame material must be one of: {valid_materials}",
                "valid_values": valid_materials
            })

    def _validate_condition(self, condition: Any, options: Dict, errors: List[Dict]) -> None:
        """Validate condition."""
        if condition is None:
            return

        valid_conditions = list(options.get("conditions", {}).keys())
        if condition not in valid_conditions:
            errors.append({
                "field": "condition",
                "code": "INVALID_CONDITION",
                "message": f"Condition must be one of: {valid_conditions}",
                "valid_values": valid_conditions
            })

    def _validate_frame_size(self, size: Any, bike_type: str, options: Dict, errors: List[Dict]) -> None:
        """Validate frame size for bike type."""
        if size is None:
            return

        frame_sizes = options.get("frame_sizes", {})
        valid_sizes = frame_sizes.get(bike_type, [])

        if not valid_sizes:
            valid_sizes = frame_sizes.get("road", [])  # Default fallback

        if size not in valid_sizes:
            errors.append({
                "field": "frame_size",
                "code": "INVALID_FRAME_SIZE",
                "message": f"Frame size '{size}' not valid for bike type '{bike_type}'",
                "valid_values": valid_sizes
            })

    def _validate_color(self, color: Any, options: Dict, errors: List[Dict]) -> None:
        """Validate color."""
        if color is None:
            return

        valid_colors = options.get("common_colors", [])
        if color not in valid_colors:
            errors.append({
                "field": "color",
                "code": "INVALID_COLOR",
                "message": f"Color must be one of: {valid_colors}",
                "valid_values": valid_colors
            })

    def _validate_motor_fields(self, details: Dict, options: Dict, errors: List[Dict]) -> None:
        """Validate e-bike motor fields."""
        motor_brand = details.get("motor_brand")
        battery_capacity = details.get("battery_capacity_wh")
        motor_position = details.get("motor_position")

        # Validate motor brand
        if motor_brand:
            valid_brands = list(options.get("motor_brands", {}).keys())
            if motor_brand not in valid_brands:
                errors.append({
                    "field": "motor_brand",
                    "code": "INVALID_MOTOR_BRAND",
                    "message": f"Motor brand must be one of: {valid_brands}",
                    "valid_values": valid_brands
                })

        # Validate battery capacity
        if battery_capacity:
            valid_capacities = options.get("battery_capacities", [])
            if battery_capacity not in valid_capacities:
                errors.append({
                    "field": "battery_capacity_wh",
                    "code": "INVALID_BATTERY_CAPACITY",
                    "message": f"Battery capacity must be one of: {valid_capacities}",
                    "valid_values": valid_capacities
                })

        # Validate motor position
        if motor_position:
            valid_positions = list(options.get("motor_positions", {}).keys())
            if motor_position not in valid_positions:
                errors.append({
                    "field": "motor_position",
                    "code": "INVALID_MOTOR_POSITION",
                    "message": f"Motor position must be one of: {valid_positions}",
                    "valid_values": valid_positions
                })

    def _validate_suspension_fields(self, details: Dict, errors: List[Dict]) -> None:
        """Validate suspension fields."""
        suspension_type = details.get("suspension_type")
        front_travel = details.get("front_suspension_travel_mm")
        rear_travel = details.get("rear_suspension_travel_mm")

        if suspension_type:
            valid_types = ["rigid", "hardtail", "full_suspension"]
            if suspension_type not in valid_types:
                errors.append({
                    "field": "suspension_type",
                    "code": "INVALID_SUSPENSION_TYPE",
                    "message": f"Suspension type must be one of: {valid_types}",
                    "valid_values": valid_types
                })

            # Validate travel requirements
            if suspension_type == "hardtail" and not front_travel:
                errors.append({
                    "field": "front_suspension_travel_mm",
                    "code": "MISSING_FRONT_TRAVEL",
                    "message": "Front suspension travel required for hardtail bikes"
                })

            if suspension_type == "full_suspension":
                if not front_travel:
                    errors.append({
                        "field": "front_suspension_travel_mm",
                        "code": "MISSING_FRONT_TRAVEL",
                        "message": "Front suspension travel required for full suspension bikes"
                    })
                if not rear_travel:
                    errors.append({
                        "field": "rear_suspension_travel_mm",
                        "code": "MISSING_REAR_TRAVEL",
                        "message": "Rear suspension travel required for full suspension bikes"
                    })

    def _validate_brake_fields(self, details: Dict, options: Dict, errors: List[Dict]) -> None:
        """Validate brake fields."""
        brake_type = details.get("brake_type")
        brake_brand = details.get("brake_brand")

        if brake_type:
            valid_types = list(options.get("brake_types", {}).keys())
            if brake_type not in valid_types:
                errors.append({
                    "field": "brake_type",
                    "code": "INVALID_BRAKE_TYPE",
                    "message": f"Brake type must be one of: {valid_types}",
                    "valid_values": valid_types
                })

        if brake_brand:
            valid_brands = list(options.get("brake_brands", {}).keys())
            if brake_brand not in valid_brands:
                errors.append({
                    "field": "brake_brand",
                    "code": "INVALID_BRAKE_BRAND",
                    "message": f"Brake brand must be one of: {valid_brands}",
                    "valid_values": valid_brands
                })

    def _validate_drivetrain_fields(self, details: Dict, options: Dict, errors: List[Dict]) -> None:
        """Validate drivetrain fields."""
        shifter_brand = details.get("shifter_brand")
        cassette_speeds = details.get("cassette_speeds")

        if shifter_brand:
            valid_brands = list(options.get("shifter_brands", {}).keys())
            if shifter_brand not in valid_brands:
                errors.append({
                    "field": "shifter_brand",
                    "code": "INVALID_SHIFTER_BRAND",
                    "message": f"Shifter brand must be one of: {valid_brands}",
                    "valid_values": valid_brands
                })

        if cassette_speeds:
            if not isinstance(cassette_speeds, int) or cassette_speeds < 1 or cassette_speeds > 12:
                errors.append({
                    "field": "cassette_speeds",
                    "code": "INVALID_CASSETTE_SPEEDS",
                    "message": "Cassette speeds must be between 1 and 12",
                    "valid_values": list(range(1, 13))
                })

    async def validate_step3(self, country_code: str, city: str, postal_code: str, shipping_options: List[str]) -> Dict[str, Any]:
        """Validate Step 3: Location and shipping."""
        errors = []

        # Validate country
        country = self.data.get_country_by_code(country_code)
        if not country:
            available_codes = [c["code"] for c in self.data.get_countries()]
            errors.append({
                "field": "country_code",
                "code": "INVALID_COUNTRY",
                "message": f"Country code '{country_code}' not supported",
                "valid_values": available_codes
            })
        else:
            # Validate city (basic check - city should be in major_cities or non-empty)
            if not city or not city.strip():
                errors.append({
                    "field": "city",
                    "code": "MISSING_CITY",
                    "message": "City is required"
                })

            # Validate postal code (basic format check)
            if not postal_code or not postal_code.strip():
                errors.append({
                    "field": "postal_code",
                    "code": "MISSING_POSTAL_CODE",
                    "message": "Postal code is required"
                })

        if errors:
            raise ValidationError(
                "Step 3 validation failed",
                "STEP3_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 3}

    async def validate_step4(self, bike_type_id: str, components: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Step 4: Components and upgrades."""
        errors = []
        available_components = self.data.get_components_for_bike_type(bike_type_id)

        required_component_types = ["wheels", "tires", "saddle", "handlebars", "pedals"]

        for component_type in required_component_types:
            if component_type not in components:
                errors.append({
                    "field": component_type,
                    "code": "MISSING_COMPONENT",
                    "message": f"Component '{component_type}' is required"
                })

        if errors:
            raise ValidationError(
                "Step 4 validation failed",
                "STEP4_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 4}

    async def validate_step5(self, currency_code: str, asking_price: float, payment_methods: List[str]) -> Dict[str, Any]:
        """Validate Step 5: Pricing and financial details."""
        errors = []

        # Validate currency
        currency = self.data.get_currency_by_code(currency_code)
        if not currency:
            available_codes = [c["code"] for c in self.data.get_currencies()]
            errors.append({
                "field": "currency_code",
                "code": "INVALID_CURRENCY",
                "message": f"Currency '{currency_code}' not supported",
                "valid_values": available_codes
            })

        # Validate price
        if asking_price <= 0:
            errors.append({
                "field": "asking_price",
                "code": "INVALID_PRICE",
                "message": "Asking price must be greater than 0"
            })

        if asking_price > 50000:  # Reasonable upper limit
            errors.append({
                "field": "asking_price",
                "code": "PRICE_TOO_HIGH",
                "message": "Asking price seems unreasonably high (>50,000)"
            })

        # Validate payment methods
        if currency and payment_methods:
            valid_methods = currency.get("payment_methods", [])
            for method in payment_methods:
                if method not in valid_methods:
                    errors.append({
                        "field": "payment_methods",
                        "code": "INVALID_PAYMENT_METHOD",
                        "message": f"Payment method '{method}' not available for {currency_code}",
                        "valid_values": valid_methods
                    })

        if errors:
            raise ValidationError(
                "Step 5 validation failed",
                "STEP5_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 5}

    async def validate_step6(self, photos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate Step 6: Photos and media."""
        errors = []

        # Check minimum photos
        if len(photos) < 3:
            errors.append({
                "field": "photos",
                "code": "INSUFFICIENT_PHOTOS",
                "message": "Minimum 3 photos required"
            })

        # Check maximum photos
        if len(photos) > 20:
            errors.append({
                "field": "photos",
                "code": "TOO_MANY_PHOTOS",
                "message": "Maximum 20 photos allowed"
            })

        # Validate main photo exists
        main_photos = [p for p in photos if p.get("is_main", False)]
        if len(main_photos) != 1:
            errors.append({
                "field": "photos",
                "code": "INVALID_MAIN_PHOTO",
                "message": "Exactly one main photo must be specified"
            })

        # Validate photo order
        orders = [p.get("order", 0) for p in photos]
        if len(set(orders)) != len(orders):
            errors.append({
                "field": "photos",
                "code": "DUPLICATE_PHOTO_ORDER",
                "message": "Photo order values must be unique"
            })

        if errors:
            raise ValidationError(
                "Step 6 validation failed",
                "STEP6_VALIDATION_ERROR",
                {"errors": errors}
            )

        return {"valid": True, "step": 6}


# Global validator instance
validator = BikeListingValidator()