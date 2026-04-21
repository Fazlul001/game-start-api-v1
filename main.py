import os
import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Load environment variables from the .env file (for local development)
load_dotenv()

# Fetch the API key from the environment
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

# Initialize your API app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, Thank you for visiting, the root url, check out other API links, Made Possible by, Fazlul, Joshua, Moh, Eitan, Fotios"}

# Create an endpoint that listens for GET requests
@app.get("/api/games")
def get_games():
    # The RAWG API URL, injecting your API key
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}"

    # Make the GET request to RAWG
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON data we got from RAWG straight to the user
        return response.json()
    else:
        # If RAWG is down or your key is wrong, return an error
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from RAWG API")