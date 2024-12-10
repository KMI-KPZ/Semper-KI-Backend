"""
Part of Semper-KI Software

Akshay NS 2024

Contains:
1. get_coordinates: This function gets the coordinates of an address using the geopy library.
2. calculate_haversine_distance: This function calculates the Haversine distance between two addresses using the geopy library.
"""
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError
import asyncio

async def get_coordinates(address, retries=3):
    """
    Get latitude and longitude for a given address using Nominatim asynchronously.

    Parameters:
    address (str): The address to geocode.
    retries (int): The number of times to retry the geocoding request in case of failure (default is 3).

    Returns:
    tuple: A tuple containing the latitude and longitude of the address, or None if the address could not be geocoded.
    """
    async with Nominatim(user_agent="geo_distance_calculator", adapter_factory=AioHTTPAdapter) as geolocator:
        # Ensure the address is properly formatted
        address = address.strip()  # Remove leading/trailing whitespace
        print(f"Formatted address for geocoding: '{address}'")  # Debugging output
        
        for attempt in range(retries):
            try:
                location = await geolocator.geocode(address, exactly_one=True, timeout=10)  # Increased timeout to 10 seconds
                if location is None:
                    raise ValueError("Location not found.")
                return (location.latitude, location.longitude)
            except GeocoderServiceError as e:
                print(f"Geocoding service error: {e}. Attempt {attempt + 1} of {retries}.")
                if attempt == retries - 1:
                    return None  # Return None after exhausting retries
            except Exception as e:
                print(f"An error occurred: {e}")
                return None  # Return None on other exceptions

async def calculate_haversine_distance(address1=None, address2=None):
    """
    Calculate the Haversine distance between two addresses asynchronously.

    Parameters:
    address1 (str): The first address to calculate the distance from (default is None, which uses a preset address).
    address2 (str): The second address to calculate the distance to (default is None, which uses a preset address).

    Returns:
    None: Prints the distance between the two addresses or an error message if the distance could not be calculated.
    """
    if address1 is None:
        address1 = 'Georg Schwarz Strasse 87, 04719, Leipzig'
    if address2 is None:
        address2 = 'Klasingstrasse 12, 04315, Leipzig'
    
    coords1 = await get_coordinates(address1)
    coords2 = await get_coordinates(address2)
    
    if coords1 and coords2:
        # Use geopy's geodesic function to calculate distance
        distance = geodesic(coords1, coords2).kilometers
        print(f'the coords1 are "{coords1}"')
        print(f'the coords2 are "{coords2}"')
        print(f"The distance between '{address1}' and '{address2}' is {distance:.2f} kilometers.")
    else:
        print("Error: Could not calculate distance due to missing or invalid address data.")

if __name__ == "__main__":
    """
    Main entry point for the Haversine Distance Calculator.

    Prompts the user for two addresses and calculates the Haversine distance between them.
    """
    print("Welcome to the Haversine Distance Calculator!")
    
    # Ask for the first address components
    street1 = input("Enter the street for the first address: ")
    postalcode1 = input("Enter the postal code for the first address: ")
    city1 = input("Enter the city for the first address: ")
    address1 = f"{street1}, {postalcode1}, {city1}"
    
    # Ask for the second address components
    street2 = input("Enter the street for the second address: ")
    postalcode2 = input("Enter the postal code for the second address: ")
    city2 = input("Enter the city for the second address: ")
    address2 = f"{street2}, {postalcode2}, {city2}"
    
    # Run the asynchronous distance calculation
    asyncio.run(calculate_haversine_distance(address1, address2))
