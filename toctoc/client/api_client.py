from typing import Optional, Dict, Any, List, TypedDict
from dataclasses import dataclass

import requests


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


@dataclass
class RegisterReference:
    register_commune: int
    register_block: int
    register_site: int
    register_commune_common_property: int
    register_block_common_property: int
    register_site_common_property: int


@dataclass
class Address:
    name_commune: str
    id_commune: int
    region: int
    street: str


@dataclass
class Finances:
    fiscal_appraisal: float
    semiannual_contribution: float
    exempt_appraisal: float


@dataclass
class Information:
    total_area: float
    area_of_construction_line: float
    min_year_of_construction: int
    max_year_of_construction: int


@dataclass
class HousingType:
    housing_type_name: str
    housing_type_code: str
    housing_type_id: int


@dataclass
class Location:
    coordinates: List[float]


@dataclass
class RoleInformation:
    register_reference: RegisterReference
    address: Address
    finances: Finances
    information: Information
    housing_type: HousingType
    location: Location


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

    def get_role_information(self, role: str, id_commune: int) -> RoleInformation:
        """Get detailed information for a specific role and commune.

        Args:
            role (str): The role identifier (e.g., "1234-22")
            id_commune (int): The commune identifier

        Returns:
            RoleInformation: Detailed information about the property

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        params = {"role": role, "idCommune": id_commune}
        response = self.call_endpoint("/info/role", params=params)
        data = response["data"]

        return RoleInformation(
            register_reference=RegisterReference(
                register_commune=data["registerReference"]["registerCommune"],
                register_block=data["registerReference"]["registerBlock"],
                register_site=data["registerReference"]["registerSite"],
                register_commune_common_property=data["registerReference"][
                    "registerCommuneCommonProperty"
                ],
                register_block_common_property=data["registerReference"][
                    "registerBlockCommonProperty"
                ],
                register_site_common_property=data["registerReference"][
                    "registerSiteCommonProperty"
                ],
            ),
            address=Address(
                name_commune=data["address"]["nameCommune"],
                id_commune=data["address"]["idCommune"],
                region=data["address"]["region"],
                street=data["address"]["street"],
            ),
            finances=Finances(
                fiscal_appraisal=data["finances"]["fiscalAppraisal"],
                semiannual_contribution=data["finances"]["semiannualContribution"],
                exempt_appraisal=data["finances"]["exemptAppraisal"],
            ),
            information=Information(
                total_area=data["information"]["totalArea"],
                area_of_construction_line=data["information"]["areaofConstructionLine"],
                min_year_of_construction=data["information"]["minYearofConstruction"],
                max_year_of_construction=data["information"]["maxYearofConstruction"],
            ),
            housing_type=HousingType(
                housing_type_name=data["housingType"]["housingTypeName"],
                housing_type_code=data["housingType"]["housingTypeCode"],
                housing_type_id=data["housingType"]["housingTypeId"],
            ),
            location=Location(coordinates=data["location"]["coordinates"]),
        )

    def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[Any, Any]:
        """Make a generic API call to any endpoint.

        Args:
            endpoint (str): The API endpoint path (e.g., "/info/role")
            method (str): HTTP method to use (GET, POST, PUT, etc.)
            params (Optional[Dict[str, Any]]): Query parameters
            data (Optional[Dict[str, Any]]): Request body data for POST/PUT requests

        Returns:
            Dict[Any, Any]: API response data

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=data,
        )
        response.raise_for_status()
        return response.json()
