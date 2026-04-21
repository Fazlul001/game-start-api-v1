import os
import traceback
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv
# Load environment variables from the .env file (for local development)
load_dotenv()

RAWG = os.getenv("RAWG")
GROQ = os.getenv("GROQ")

# Groq client
client = Groq(GROQ)

# Initialize your API app
app = FastAPI()

class AIRecommendationRequest(BaseModel):
    query: str
    model: str = Field(default="llama-3.3-70b-versatile")

@app.get("/")
def root():
    return {"message": "Hello, Thank you for visiting, the root url, check out other API links, Made Possible by, Fazlul, Joshua, Moh, Eitan, Fotios"}

# Create an endpoint that listens for GET requests
@app.get("/api/games")
def get_games():
    url = f"https://api.rawg.io/api/games?key={RAWG}"

    # Make the GET request to RAWG
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON data we got from RAWG straight to the user
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from RAWG API")


@app.post("/com.gamestart/v1/ai/recommendation")
def aichat_recommendation(request_data: AIRecommendationRequest):
    try:
        # Call the Groq API
        message = client.chat.completions.create(
            model=request_data.model,
            max_tokens=1024,
            messages=[  # type: ignore
                {"role": "user", "content": request_data.query}
            ]
        )

        response_text = message.choices[0].message.content

        # FastAPI automatically converts dictionaries to JSON responses
        return {
            "success": True,
            "query": request_data.query,
            "response": response_text,
            "model": request_data.model
        }

    except Exception as e:
        # FastAPI's HTTPException replaces Django's JsonResponse for errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process Groq request",
                "details": str(e),
                "traceback": traceback.format_exc()
            }
        )