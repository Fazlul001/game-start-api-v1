from fastapi import FastAPI

# Initialize your API app
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, Thank you for visiting, the root url, check out other API links, Made Possible by, Fazlul, Joshua, Moh, Eitan, Fotios"}

# Create an endpoint that listens for GET requests
@app.get("/api/games")
def get_games():
    # When someone hits this URL, send back this JSON data
    return {
        "store": "Gamestart an E-commerce, Online platform for Game enthusiasts",
        "inventory": ["Super Mario Odyssey", "Elden Ring", "Cyberpunk 2077"]
    }
