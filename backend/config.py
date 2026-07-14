import os
from dotenv import load_dotenv



load_dotenv(".secrets")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

