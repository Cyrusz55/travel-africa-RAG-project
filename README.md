# Travel Africa RAG Assistant

![Travel Africa](Travel%20Africa.png)

An intelligent travel assistant powered by Retrieval-Augmented Generation (RAG) that helps users discover hotels, explore destinations, and plan trips across **Kenya and East Africa**.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3FCF8F?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-4F6BFF?style=for-the-badge&logo=deepseek&logoColor=white)](https://deepseek.com/)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Challenges & Lessons](#challenges--lessons)
- [Future Improvements](#future-improvements)

---

## Overview

Travel Africa RAG is a full-stack AI travel assistant that answers natural-language questions about hotels, destinations, and trip planning across East Africa. Users type questions like *"Find luxury hotels in Nairobi"* or *"Plan a 6-day Kenya safari"*, and the system retrieves relevant hotel data from a vector database, then generates a coherent, sourced answer using a large language model.

The system scrapes hotel data from public sources, cleans and structures it, generates vector embeddings using an ONNX-optimized Sentence Transformer, stores them in a PostgreSQL database with pgvector, and serves a responsive frontend through FastAPI.

### Key Features

- **Natural Language Queries** — Ask about hotels, locations, or trip plans in plain English
- **RAG Architecture** — Retrieves relevant hotel records before generating answers, reducing hallucination
- **Semantic Search** — Uses cosine similarity on 384-dimensional embeddings to find contextually relevant results
- **Sourced Answers** — Every response includes the hotel names and locations used to generate it
- **Supabase pgvector** — Embeddings stored and searched in PostgreSQL with vector similarity indexing
- **Responsive Frontend** — Premium editorial UI with chat overlay, destination cards, and interactive prompt interface
- **DeepSeek Integration** — Powered by DeepSeek Chat for answer generation

---

## Architecture

```
                    ┌──────────────────┐
                    │   User Browser   │
                    │  (HTML + CSS +   │
                    │     JavaScript)   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    FastAPI App   │
                    │  (backend/main.py)│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌───────────────┐ ┌──────────┐ ┌──────────────┐
    │  RAG Pipeline │ │  Vector  │ │   CSV Data   │
    │(rag_pipeline  │ │  Store   │ │  (cleaned_   │
    │    .py)       │ │(vector_  │ │  hotels.csv) │
    └───────┬───────┘ │ store.py)│ └──────────────┘
            │         └────┬─────┘
            │              │
            ▼              ▼
    ┌─────────────────────────────────────┐
    │       Supabase PostgreSQL           │
    │      (pgvector extension)           │
    │   hotels table + embedding column   │
    │         vector(384)                 │
    └─────────────────────────────────────┘
            │
            ▼
    ┌──────────────────┐
    │   DeepSeek API   │
    │ (answer generation) │
    └──────────────────┘
```

### RAG Flow

1. User submits a question via the frontend chat interface
2. The question is converted into a 384-dimensional embedding using `all-MiniLM-L6-v2` (ONNX runtime)
3. The embedding is compared against all hotel embeddings in Supabase using cosine similarity (`<=>` operator)
4. The top 5 most relevant hotel records are retrieved
5. Retrieved records are formatted as context and sent to DeepSeek Chat API
6. The LLM generates a natural-language answer using only the provided context
7. The answer and source citations are returned to the frontend

---

## Data Pipeline

### 1. Scraping (`data/scraper.py`)

- Collects hotel data from OpenStreetMap via the Nominatim and Overpass APIs
- Targets 16 locations across Kenya, Tanzania, and Uganda
- Respects ethical scraping practices: respectful rate limiting (5-second delays), descriptive User-Agent headers, public data only
- Saves raw data to `data/raw_data/raw_hotels.csv`

### 2. Cleaning (`data/data_cleaner.py`)

- Drops records with missing hotel names
- Removes duplicate entries by hotel name and location
- Normalizes inconsistent location names (e.g., "Mombasa City" → "Mombasa")
- Fills missing values for descriptions, amenities, contact info, and websites
- Drops unused columns (Room Types, Rating, Review Summary, Nearby Attractions, Image URL)
- Outputs a structured dataset to `data/clean_data/cleaned_hotels.csv`

### 3. Embedding (`backend/vector_store.py`)

- Reads cleaned CSV and formats each hotel as structured text
- Generates 384-dimensional embeddings using ONNX-optimized `all-MiniLM-L6-v2`
- Stores embeddings directly in Supabase PostgreSQL using psycopg2 with `::vector` casting
- Supports idempotent re-upload — truncates and repopulates on each run

### Dataset Summary

| Metric | Value |
|---|---|
| Total Hotels | **1,459** |
| Unique Hotels | **1,441** |
| Locations Covered | **14** |
| Countries | Kenya (808), Tanzania (447), Uganda (204) |
| Price Range | Varies per hotel |

---

## Tech Stack

### Backend

| Technology | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **SQLAlchemy** | ORM and database connection management |
| **psycopg2** | PostgreSQL driver with vector cast support |
| **Supabase (pgvector)** | Hosted PostgreSQL with vector similarity search |
| **chromadb (ONNX)** | Embedding generation (MiniLM-L6-v2 via ONNX runtime) |
| **OpenAI SDK** | DeepSeek Chat API client |
| **Pandas** | Data cleaning and CSV management |
| **python-dotenv** | Environment variable management |

### Frontend

| Technology | Purpose |
|---|---|
| **HTML5** | Semantic page structure |
| **CSS3** | Responsive styling with custom properties |
| **JavaScript** | Async fetch for chat overlay and API calls |
| **Google Fonts** | Inter + Playfair Display typography |

### Infrastructure

| Service | Purpose |
|---|---|
| **Supabase** | PostgreSQL database with pgvector for embeddings |
| **Render** | Web service deployment (optional) |
| **GitHub** | Version control and deployment integration |

---

## Project Structure

```
TravelAfricaRAGProject/
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
├── .secrets                          # Environment variables (excluded from git)

├── templates/
│   └── index.html                    # Frontend landing page + chat overlay

├── static/
│   └── css/
│       └── styles.css                # All frontend styling

├── backend/
│   ├── main.py                       # FastAPI application and route definitions
│   ├── config.py                     # Configuration loader (legacy)
│   ├── rag_pipeline.py               # RAG query pipeline (embed → search → generate)
│   └── vector_store.py               # Embedding creation and Supabase upload

├── database/
│   ├── __init__.py                   # Package initializer
│   ├── db_connection.py              # SQLAlchemy engine and session management
│   └── models.py                     # SQLAlchemy ORM models

├── data/
│   ├── scraper.py                    # Hotel data collection from OpenStreetMap
│   ├── data_cleaner.py               # Data cleaning and normalization
│   ├── raw_data/
│   │   ├── raw_hotels.csv            # Raw scraped data
│   │   └── raw_hotels_checkpoint.csv # Scraping checkpoint
│   └── clean_data/
│       └── cleaned_hotels.csv        # Final cleaned dataset

├── chroma_db/                        # Legacy ChromaDB directory (migrated to Supabase)

├── photos/
│   ├── page1.1.png                   # Landing page — hero section
│   ├── page1.2.png                   # Landing page — demo/interaction section
│   ├── page1.3.png                   # Landing page — destinations section
│   ├── page1.4.png                   # Landing page — testimonials section
│   └── prompt_example.png            # Example AI chat interaction

├── run.py                            # Local development launcher (dual server)
├── start.py                          # Alternative launcher with data flag
└── Travel Africa.png                 # Project logo / branding image
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A Supabase project with pgvector extension enabled
- A DeepSeek API key

### Setup

**1. Clone the repository**

```bash
git clone https://github.com/your-username/TravelAfricaRAGProject.git
cd TravelAfricaRAGProject
```

**2. Create and activate a virtual environment**

```bash
python -m venv .env
# Windows
.env\Scripts\activate
# macOS / Linux
source .env/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.secrets` file in the project root:

```
DATABASE_URL="postgresql://postgres.your-ref:***@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**5. Set up the database**

Run this SQL in your Supabase SQL Editor:

```sql
create extension if not exists vector;

create table if not exists hotels (
  id serial primary key,
  name text not null,
  location text not null,
  county_region text,
  country text,
  description text,
  price_range text,
  amenities text,
  category text,
  contact text,
  website text,
  embedding vector(384)
);

create index if not exists hotels_embedding_idx
  on hotels using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);
```

**6. Run the application**

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**7. Upload hotel data to the vector database**

```bash
curl -X POST http://localhost:8000/upload-data
```

Allow 30–120 seconds for embedding generation.

**8. Open the application**

Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend landing page |
| `HEAD` | `/` | Health check (HEAD method for uptime monitoring) |
| `POST` | `/upload-data` | Generates embeddings and uploads hotel data to Supabase |
| `POST` | `/ask` | Ask a travel-related question |
| `GET` | `/hotels` | Returns all hotels in the dataset |
| `GET` | `/hotels/{location}` | Returns hotels filtered by location |
| `POST` | `/plan-trip` | Generates a day-by-day itinerary based on preferences |

### Example: Ask a Question

**Request:**
```bash
curl -X POST https://your-service.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Find luxury hotels in Nairobi"}'
```

**Response:**
```json
{
  "answer": "Here are luxury hotels in Nairobi...",
  "sources": [
    { "hotel_name": "Radisson Blu Hotel", "location": "Nairobi" }
  ]
}
```

---

## Screenshots

### Landing Page — Hero Section

![Hero Section](photos/page1.1.png)

The landing page features a full-viewport hero with a search prompt card, quick action buttons, and an organic photo collage of East African destinations.

### AI Chat Interaction

![Chat Interaction](photos/prompt_example.png)

Users can type travel questions in the chat overlay, which queries the RAG pipeline and returns sourced, AI-generated answers.

### Demo & How It Works

![Demo Section](photos/page1.2.png)

The "See it in Action" section shows a browser mockup with a sample itinerary, demonstrating the AI trip planning workflow.

### Destination Cards

![Destinations Section](photos/page1.3.png)

Destination cards showcase featured travel locations with curated imagery and quick-access tags.

### Testimonials

![Testimonials Section](photos/page1.4.png)

Social proof section with traveler testimonials and reviews.

---

## Challenges & Lessons

### Data Quality
The initial scraped data had limited information — most hotels lacked pricing, ratings, and detailed descriptions. The scraper collected from OpenStreetMap, which provides basic metadata but not the rich amenity and pricing detail found on booking platforms. Future iterations could integrate additional sources or supplement with manual curation.

### pgvector Type Casting
Integrating vector embeddings with SQLAlchemy required using raw psycopg2 connections for the `::vector` cast, as SQLAlchemy's `text()` bind parameters conflicted with the cast syntax. Using `engine.raw_connection()` provided a clean workaround.

### Frontend-Backend Serving
Transitioning from a dual-server setup (separate static file server + FastAPI) to serving everything from FastAPI simplified deployment. Adding a `StaticFiles` mount for CSS and `@app.head("/")` for uptime monitoring compatibility were key refinements.

### Ethical Scraping
The Nominatim API required a descriptive User-Agent and rate limiting. Balancing data collection volume with API fairness policies meant the scraping process ran overnight for the full dataset of 1,400+ hotels.

---

## Future Improvements

- **Multi-source data** — Integrate hotel booking APIs for live pricing, real availability, and user ratings
- **Caching layer** — Add Redis or in-memory caching for frequently asked queries
- **User accounts** — Save trip plans, favorite hotels, and search history
- **Multi-language support** — Expand beyond English to Swahili, French, and other regional languages
- **Map integration** — Display hotel locations on an interactive map (Leaflet or Mapbox)
- **Image search** — Allow users to search by uploading photos of destinations
- **Expanded coverage** — Add more countries (Rwanda, Ethiopia, South Africa) and more granular location data
- **Performance optimization** — Batch embedding generation and consider GPU acceleration for larger datasets

---

## License

This project was developed as a student portfolio project. Data sourced from OpenStreetMap is © OpenStreetMap contributors, distributed under the Open Database License.
