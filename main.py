import json
import os
import traceback
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

RAWG_TOOL_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_rawg_games",
            "description": "Search the RAWG database for video games. Use this when the user asks for game suggestions, release dates, or specific game details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "The name of the game or keywords (e.g., 'Elden Ring')"},
                    "page_size": {"type": "integer", "description": "Number of games to return (default 5)"}
                },
                "required": ["search_query"]
            }
        }
    }
]

# Load environment variables from the .env file (for local development)
load_dotenv()

RAWG_API_KEY = os.getenv("RAWG_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq client
client = Groq(api_key=GROQ_API_KEY)

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
    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}"

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


@app.post("/com.gamestart/v1/ai/recommendation-with-rawg")
def aichat_recommendation_rawg(request_data: AIRecommendationRequest):
    # A. Initial messages with the user's query
    messages = [{"role": "user", "content": request_data.query}]

    # B. Ask Groq (giving it access to the tool)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=RAWG_TOOL_DEFINITION,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # C. If the AI wants to use RAWG...
    if tool_calls:
        # We process the first tool call
        tool_call = tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)

        # Actually hit the REAL RAWG API
        print(f"DEBUG: AI is searching RAWG for: {function_args.get('search_query')}")
        rawg_url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={function_args.get('search_query')}&page_size={function_args.get('page_size', 5)}"
        rawg_results = requests.get(rawg_url).json()

        # D. Give the RAWG data back to Groq so it can explain it to the user
        messages.append(response_message)  # Add the AI's "request" to the history
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": "search_rawg_games",
            "content": json.dumps(rawg_results.get("results", []))
        })

        # E. Get the FINAL human-friendly response from Groq
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return {"recommendation": final_response.choices[0].message.content}

    # If the AI didn't need the tool, just return its text answer
    return {"recommendation": response_message.content}