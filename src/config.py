import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path.home() / "Desktop" / "tjm-project"
DEBUG_DIR = BASE_DIR / "debug_output"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

# System constants
TARGET_API_URL = "https://jsonplaceholder.typicode.com/posts"