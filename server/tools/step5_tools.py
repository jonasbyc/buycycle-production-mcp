"""Step 5 MCP Tools: Pricing and Financial Details."""
from typing import Dict, Any, List
from ..data_loader import data_loader
from ..validators import validator, ValidationError
import logging

logger = logging.getLogger(__name__)


async def list_currencies() -> Dict[str, Any]:
    """
    Get all supported currencies for bike listings.

    Returns currencies that can be used for pricing bikes.
    Use this to show available pricing currencies.
    """
    try:
        currencies = data_loader.get_currencies()

        return {
            "success": True,
            "data": {
                "currencies": currencies,
                "total_count": len(currencies)
            },
            "metadata": {
                "step": 5,
                "next_suggested_tools": ["get_currency_details", "get_price_suggestions"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in list_currencies: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_currency_details(currency_code: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific currency.

    Args:
        currency_code: ISO currency code (e.g., 'EUR', 'USD', 'GBP')

    Returns detailed currency information including payment methods.
    Use after currency selection to get specific details.
    """
    try:
        currency = data_loader.get_currency_by_code(currency_code.upper())

        if not currency:
            available_codes = [c["code"] for c in data_loader.get_currencies()]
            return {
                "success": False,
                "error": {
                    "code": "INVALID_CURRENCY",
                    "message": f"Currency code '{currency_code}' not supported",
                    "valid_values": available_codes
                }
            }

        return {
            "success": True,
            "data": {
                "currency": currency,
                "payment_methods": currency.get("payment_methods", []),
                "supported_countries": currency.get("countries", [])
            },
            "metadata": {
                "step": 5,
                "next_suggested_tools": ["get_payment_methods", "validate_pricing"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_currency_details: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_payment_methods(currency_code: str) -> Dict[str, Any]:
    """
    Get available payment methods for a specific currency.

    Args:
        currency_code: ISO currency code

    Returns payment methods available for the currency.
    Use to understand what payment options are available.
    """
    try:
        currency = data_loader.get_currency_by_code(currency_code.upper())

        if not currency:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_CURRENCY",
                    "message": f"Currency code '{currency_code}' not supported"
                }
            }

        payment_methods = currency.get("payment_methods", [])

        # Add descriptions for payment methods
        method_descriptions = {
            "bank_transfer": {
                "name": "Bank Transfer",
                "description": "Direct bank-to-bank transfer",
                "security": "High",
                "speed": "1-3 business days"
            },
            "paypal": {
                "name": "PayPal",
                "description": "PayPal payment processing",
                "security": "High",
                "speed": "Instant"
            },
            "credit_card": {
                "name": "Credit Card",
                "description": "Credit or debit card payment",
                "security": "High",
                "speed": "Instant"
            },
            "klarna": {
                "name": "Klarna",
                "description": "Buy now, pay later service",
                "security": "High",
                "speed": "Instant"
            },
            "venmo": {
                "name": "Venmo",
                "description": "Mobile payment service",
                "security": "Medium",
                "speed": "Instant"
            },
            "zelle": {
                "name": "Zelle",
                "description": "US bank-to-bank transfer",
                "security": "High",
                "speed": "Minutes"
            }
        }

        formatted_methods = []
        for method in payment_methods:
            method_info = method_descriptions.get(method, {
                "name": method.title(),
                "description": f"{method.title()} payment method",
                "security": "Medium",
                "speed": "Varies"
            })
            formatted_methods.append({
                "id": method,
                **method_info
            })

        return {
            "success": True,
            "data": {
                "payment_methods": formatted_methods,
                "currency_code": currency_code.upper(),
                "currency_name": currency["name"]
            },
            "metadata": {
                "step": 5,
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_payment_methods: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def get_price_suggestions(bike_type_id: str, brand_id: str, model_id: str, year: int, condition: str) -> Dict[str, Any]:
    """
    Get AI-powered price suggestions based on bike details.

    Args:
        bike_type_id: The bike type
        brand_id: The bike brand
        model_id: The bike model
        year: Manufacturing year
        condition: Bike condition

    Returns suggested price ranges based on market data.
    Use to help determine appropriate pricing.
    """
    try:
        # Get model details for MSRP reference
        models = data_loader.get_brand_models_by_type(brand_id, bike_type_id)
        model = next((m for m in models if m["id"] == model_id), None)

        if not model:
            return {
                "success": False,
                "error": {
                    "code": "MODEL_NOT_FOUND",
                    "message": "Model not found for price suggestion"
                }
            }

        msrp_range = model.get("msrp_range", {})
        min_msrp = msrp_range.get("min", 1000)
        max_msrp = msrp_range.get("max", 5000)

        # Calculate depreciation based on age and condition
        current_year = 2024
        age = max(0, current_year - year)

        # Depreciation factors
        age_depreciation = 0.15 * min(age, 5)  # 15% per year, max 5 years
        condition_factors = {
            "new": 1.0,
            "like_new": 0.85,
            "very_good": 0.75,
            "good": 0.60,
            "fair": 0.45
        }

        condition_factor = condition_factors.get(condition, 0.60)
        total_factor = condition_factor * (1 - age_depreciation)

        # Calculate suggested prices
        suggested_min = int(min_msrp * total_factor * 0.8)  # Conservative estimate
        suggested_max = int(max_msrp * total_factor * 1.1)  # Optimistic estimate
        suggested_mid = int((suggested_min + suggested_max) / 2)

        return {
            "success": True,
            "data": {
                "price_suggestions": {
                    "conservative": suggested_min,
                    "recommended": suggested_mid,
                    "optimistic": suggested_max
                },
                "reference_data": {
                    "original_msrp_range": msrp_range,
                    "age_years": age,
                    "condition": condition,
                    "depreciation_applied": f"{int(age_depreciation * 100)}%"
                },
                "market_insights": [
                    f"Similar {condition} {brand_id} bikes typically sell for {suggested_min}-{suggested_max}",
                    f"Consider starting at {suggested_mid} and be open to negotiation",
                    "Premium brands may hold value better than suggested",
                    "Rare or discontinued models may command higher prices"
                ]
            },
            "metadata": {
                "step": 5,
                "next_suggested_tools": ["validate_pricing"],
                "validation_status": "pending"
            }
        }

    except Exception as e:
        logger.error(f"Error in get_price_suggestions: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def validate_pricing(currency_code: str, asking_price: float, payment_methods: List[str], original_price: float = None, negotiable: bool = False) -> Dict[str, Any]:
    """
    Validate Step 5 pricing and financial details.

    Args:
        currency_code: Selected currency code
        asking_price: The listing price
        payment_methods: List of accepted payment method IDs
        original_price: Optional original MSRP
        negotiable: Whether price is negotiable

    Validates pricing information and payment method selections.
    Use this to verify pricing before proceeding to Step 6.
    """
    try:
        # Run validation
        result = await validator.validate_step5(currency_code, asking_price, payment_methods)

        # Additional checks
        warnings = []
        if original_price and asking_price > original_price:
            warnings.append("Asking price is higher than original MSRP - this may reduce interest")

        if asking_price < 100:
            warnings.append("Very low price may attract bargain hunters or seem suspicious")

        if asking_price > 10000 and "paypal" not in payment_methods:
            warnings.append("High-value items often benefit from PayPal buyer protection")

        return {
            "success": True,
            "data": {
                "validation_result": result,
                "pricing": {
                    "currency_code": currency_code,
                    "asking_price": asking_price,
                    "original_price": original_price,
                    "negotiable": negotiable,
                    "payment_methods": payment_methods
                },
                "warnings": warnings
            },
            "metadata": {
                "step": 5,
                "next_suggested_tools": ["get_photo_requirements"],
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
        logger.error(f"Error in validate_pricing: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }


@app.tool()
async def calculate_fees(asking_price: float, currency_code: str = "EUR") -> Dict[str, Any]:
    """
    Calculate estimated platform and payment processing fees.

    Args:
        asking_price: The listing price
        currency_code: Currency for fee calculation (default: EUR)

    Returns fee breakdown and net amount seller receives.
    Use to help sellers understand the costs involved.
    """
    try:
        # Mock fee structure (replace with real Buycycle fees)
        platform_fee_rate = 0.04  # 4% platform fee
        payment_fee_rate = 0.029  # 2.9% payment processing
        fixed_fee = 0.30  # Fixed transaction fee

        platform_fee = asking_price * platform_fee_rate
        payment_fee = asking_price * payment_fee_rate
        total_fees = platform_fee + payment_fee + fixed_fee
        net_amount = asking_price - total_fees

        return {
            "success": True,
            "data": {
                "fee_breakdown": {
                    "asking_price": asking_price,
                    "platform_fee": round(platform_fee, 2),
                    "payment_processing_fee": round(payment_fee, 2),
                    "fixed_transaction_fee": fixed_fee,
                    "total_fees": round(total_fees, 2),
                    "net_amount": round(net_amount, 2)
                },
                "fee_rates": {
                    "platform_fee_rate": f"{platform_fee_rate * 100}%",
                    "payment_fee_rate": f"{payment_fee_rate * 100}%"
                },
                "currency_code": currency_code
            },
            "metadata": {
                "step": 5,
                "validation_status": "informational"
            }
        }

    except Exception as e:
        logger.error(f"Error in calculate_fees: {e}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }