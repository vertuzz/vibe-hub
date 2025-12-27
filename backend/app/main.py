from fastapi import FastAPI

app = FastAPI(
    title="VibeHub API",
    description="Backend for VibeHub - The Dribbble for AI Apps",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to VibeHub API"}
