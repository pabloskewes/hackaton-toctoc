import json


def extract_json_from_text(text):
    """Extracts a valid JSON from a given text.

    Args:
      text: The text from which JSON will be extracted.

    Returns:
      A Python dictionary representing the extracted JSON, or None if no valid
      JSON is found.
    """

    # Find the start and end positions of JSON
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        # Extract the JSON text and parse it
        json_text = text[start : end + 1]
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            print("Error: The text is not a valid JSON.")
            return None
    else:
        print("No valid JSON was found in the text.")
        return None


if __name__ == "__main__":
    # Usage example
    text = """Excellent, we have gathered all the necessary information. Here is a summary of your preferences for the apartment in Santiago:

    {
      "location": "Santiago",
      "property_type": "Apartment",
      "bedrooms": 4,
      "bathrooms": 3,
      "additional_features": ["parking", "terrace"],
      "price_range": "300,000,000 CLP"
    }

    Would you like to make any adjustments or add more information before proceeding to search for options that match your preferences?
    """

    result = extract_json_from_text(text)
    print(result)
