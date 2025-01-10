from api_client import TocTocApiClient, PropertyDetails


def main():
    # Initialize the client with your access token
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkdlcmFyZG8gTXXDsW96IiwiaWF0IjoxNTE2MjM5MDIyLCJ1c2VyX2lkIjoiMTIzNCJ9.FpthiZ_xC_U0RlVnlvR-axVKCmUVoN200VXJ6FD8mAU"
    client = TocTocApiClient(access_token)

    try:
        # Create a PropertyDetails instance with sample data
        property_details = PropertyDetails(
            latitude=-33.4569,  # Santiago, Chile coordinates
            longitude=-70.6483,
            property_family_type_id=1,  # Example property type ID
            usable_area=120.5,  # Square meters
            balcony_area=10.0,
            parking_lots=2,
            bedrooms=3,
            bathrooms=2,
            year_construction=2015,
            warehouse=1,
            common_expense=150000.0,  # Chilean Pesos
        )

        # Get the property appraisal
        result = client.get_sale_appraisal(property_details)

        # Print the result
        print("Property Appraisal Result:")
        print(result)

    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Always close the client when done
        client.close()


if __name__ == "__main__":
    main()
