import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PropertyDetails:
    latitude: float
    longitude: float
    property_family_type_id: int
    usable_area: float
    balcony_area: Optional[float] = None
    parking_lots: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    year_construction: Optional[int] = None
    warehouse: Optional[int] = None
    common_expense: Optional[float] = None
    role: Optional[str] = None


class TocTocApiClient:
    """Client for interacting with the property valuation API."""

    BASE_URL = "https://gw.toctoc.com/1.0"

    def __init__(self, access_token: str):
        """Initialize the client with authentication token.

        Args:
            access_token (str): Bearer token for API authentication
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        )

    def get_sale_appraisal(self, property_details: PropertyDetails) -> Dict[Any, Any]:
        """Get property sale appraisal based on location and specifications.

        Args:
            property_details (PropertyDetails): Details of the property to evaluate

        Returns:
            dict: API response containing the property valuation

        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If required parameters are invalid
        """
        self._validate_coordinates(
            property_details.latitude, property_details.longitude
        )

        params = {
            "lat": property_details.latitude,
            "long": property_details.longitude,
            "propertyFamilyTypeId": property_details.property_family_type_id,
            "usableArea": property_details.usable_area,
        }

        # Add optional parameters if they are provided
        optional_params = {
            "balconyArea": property_details.balcony_area,
            "parkingLots": property_details.parking_lots,
            "bedrooms": property_details.bedrooms,
            "bathrooms": property_details.bathrooms,
            "yearConstruction": property_details.year_construction,
            "warehouse": property_details.warehouse,
            "commonExpense": property_details.common_expense,
            "role": property_details.role,
        }

        params.update({k: v for k, v in optional_params.items() if v is not None})

        response = self.session.get(
            f"{self.BASE_URL}/valorization/appraisal/sale", params=params
        )
        response.raise_for_status()

        return response.json()

    def _validate_coordinates(self, lat: float, long: float) -> None:
        """Validate that coordinates are within valid ranges.

        Args:
            lat (float): Latitude value
            long (float): Longitude value

        Raises:
            ValueError: If coordinates are outside valid ranges
        """
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= long <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")

    def close(self) -> None:
        """Close the session when done."""
        self.session.close()
