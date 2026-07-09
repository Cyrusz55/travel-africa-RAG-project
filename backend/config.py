import os
from dotenv import load_dotenv

from backend.vector_store import CHROMA_PATH

load_dotenv(".secrets")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
CHROMA_PATH = "chroma_db"
DATA_PATH = "data/raw_data/raw_hotels.csv"