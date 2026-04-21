from fastapi import FastAPI

# Initialize your API app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

# Create an endpoint that listens for GET requests
@app.get("/api/games")
def get_games():
    # When someone hits this URL, send back this JSON data
    return {
        "store": "Mock GameStop",
        "inventory": ["Super Mario Odyssey", "Elden Ring", "Cyberpunk 2077"]
    }
