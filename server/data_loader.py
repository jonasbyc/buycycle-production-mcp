"""Data loading and caching for MCP server."""
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and caching of JSON data files."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self._cache: Dict[str, Any] = {}
        self._loaded = False

    async def load_all(self) -> None:
        """Load all data files into memory cache."""
        if self._loaded:
            return

        logger.info("Loading all data files...")
        start_time = asyncio.get_event_loop().time()

        # Load all data files concurrently
        load_tasks = [
            self._load_file("bike_types.json", "bike_types"),
            self._load_file("brands.json", "brands"),
            self._load_file("models_by_brand.json", "models_by_brand"),
            self._load_file("conditional_fields.json", "conditional_fields"),
            self._load_file("step2_details.json", "step2_details"),
            self._load_file("countries.json", "countries"),
            self._load_file("components.json", "components"),
            self._load_file("currencies.json", "currencies"),
        ]

        await asyncio.gather(*load_tasks)

        end_time = asyncio.get_event_loop().time()
        logger.info(f"Data loading completed in {end_time - start_time:.3f}s")
        self._loaded = True

    async def load_all_optimized(self) -> None:
        """Load all optimized data files into memory cache."""
        if self._loaded:
            return

        logger.info("Loading all optimized data files...")
        start_time = asyncio.get_event_loop().time()

        # Load all data files concurrently
        load_tasks = [
            self._load_file("enhanced_bike_types.json", "bike_types"),
            self._load_file("optimized_brands.json", "brands"),
            self._load_file("models_by_brand.json", "models_by_brand"),
            self._load_file("conditional_fields.json", "conditional_fields"),
            self._load_file("step2_details.json", "step2_details"),
            self._load_file("enhanced_countries.json", "countries"),
            self._load_file("enhanced_components.json", "components"),
            self._load_file("currencies.json", "currencies"),
        ]

        await asyncio.gather(*load_tasks)

        end_time = asyncio.get_event_loop().time()
        logger.info(f"Optimized data loading completed in {end_time - start_time:.3f}s")
        self._loaded = True

    async def _load_file(self, filename: str, cache_key: str) -> None:
        """Load a single JSON file."""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[cache_key] = data
                logger.debug(f"Loaded {filename}")
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            raise

    def get(self, key: str) -> Any:
        """Get cached data by key."""
        if not self._loaded:
            raise RuntimeError("Data not loaded. Call load_all() first.")
        return self._cache.get(key)

    def get_bike_types(self) -> Dict[str, Any]:
        """Get all bike types."""
        return self.get("bike_types") or {}

    def get_brands(self) -> Dict[str, Any]:
        """Get all brands."""
        return self.get("brands") or {}

    def get_models_for_brand(self, brand_id: str) -> Dict[str, List[Any]]:
        """Get all models for a specific brand."""
        models_by_brand = self.get("models_by_brand") or {}
        return models_by_brand.get(brand_id, {})

    def get_brand_models_by_type(self, brand_id: str, bike_type: str) -> List[Any]:
        """Get models for a specific brand and bike type."""
        brand_models = self.get_models_for_brand(brand_id)
        return brand_models.get(bike_type, [])

    def get_conditional_fields(self) -> Dict[str, Any]:
        """Get conditional fields configuration."""
        return self.get("conditional_fields") or {}

    def get_step2_details(self) -> Dict[str, Any]:
        """Get step 2 detail options."""
        return self.get("step2_details") or {}

    def get_countries(self) -> List[Dict[str, Any]]:
        """Get all countries."""
        return self.get("countries") or []

    def get_country_by_code(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get country by country code."""
        countries = self.get_countries()
        return next((c for c in countries if c["code"] == country_code), None)

    def get_components(self) -> Dict[str, Any]:
        """Get all components."""
        return self.get("components") or {}

    def get_components_for_bike_type(self, bike_type: str) -> Dict[str, Any]:
        """Get components appropriate for bike type."""
        components = self.get_components()

        # Filter components based on bike type
        filtered = {}
        for category, items in components.items():
            if isinstance(items, dict):
                if bike_type in items:
                    filtered[category] = items[bike_type]
                elif "all" in items:
                    filtered[category] = items["all"]
            else:
                filtered[category] = items

        return filtered

    def get_currencies(self) -> List[Dict[str, Any]]:
        """Get all currencies."""
        return self.get("currencies") or []

    def get_currency_by_code(self, currency_code: str) -> Optional[Dict[str, Any]]:
        """Get currency by code."""
        currencies = self.get_currencies()
        return next((c for c in currencies if c["code"] == currency_code), None)

    def validate_brand_exists(self, brand_id: str) -> bool:
        """Check if brand exists."""
        brands = self.get_brands()
        return brand_id in brands

    def validate_model_exists(self, brand_id: str, model_id: str, bike_type: str) -> bool:
        """Check if model exists for brand and bike type."""
        models = self.get_brand_models_by_type(brand_id, bike_type)
        return any(model["id"] == model_id for model in models)

    def validate_bike_type_exists(self, bike_type_id: str) -> bool:
        """Check if bike type exists."""
        bike_types = self.get_bike_types()
        return bike_type_id in bike_types

    def validate_country_exists(self, country_code: str) -> bool:
        """Check if country exists."""
        return self.get_country_by_code(country_code) is not None

    def validate_currency_exists(self, currency_code: str) -> bool:
        """Check if currency exists."""
        return self.get_currency_by_code(currency_code) is not None


# Global data loader instance
data_loader = DataLoader()