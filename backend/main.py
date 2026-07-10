from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from backend.rag_pipeline import ask_question
from backend.vector_store import create_embeddings
import os
from pathlib import Path

app = FastAPI(title="Travel Africa RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class Question(BaseModel):
    question: str

class TripPlan(BaseModel):
    preferences: str

@app.head("/")
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return Path("templates/index.html").read_text(encoding="utf-8")

@app.post("/upload-data")
def upload_data():
    # simply triggers embedding creation from cleaned CSV
    create_embeddings()
    return {"message": "Embeddings created successfully"}
@app.post("/ask")
def ask(req: Question):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    result = ask_question(req.question, api_key)
    return result
@app.get("/hotels")
def get_all_hotels():
    df = pd.read_csv("data/clean_data/cleaned_hotels.csv")
    return df.to_dict(orient="records")

@app.get("/hotels/{location}")
def get_hotels_by_location(location: str):
    df = pd.read_csv("data/clean_data/cleaned_hotels.csv")
    filtered_df = df[df['Location'].str.contains(location, case=False, na=False)]
    if filtered_df.empty:
        raise HTTPException(status_code=404, detail=f"No hotels found in {location}")
    return filtered_df.to_dict(orient="records")

@app.post("/plan-trip")
def plan_trip(plan: TripPlan):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    result = ask_question(
        f"Plan a trip based on: {plan.preferences}."
        f"Give a day-by-day itinerary with hotel recommendations and activities in Kenya & East Africa.",
        api_key=api_key
    )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
