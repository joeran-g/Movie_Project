import os
import requests
from dotenv import load_dotenv

# Load the environment variable from the .env file
load_dotenv()

API_KEY = os.environ.get('API_KEY')
REQUEST_GET_URL = f"http://www.omdbapi.com/?apikey={API_KEY}&"

def get_movie_by_title(title):
    """
    Fetch data from a movie by requesting the OMDb-API.
    return data as dictionary.
    """
    movie_data = requests.get(REQUEST_GET_URL, params={"t":title})
    return movie_data.json()
