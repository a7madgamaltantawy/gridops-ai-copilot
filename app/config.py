from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "grid.db"

USE_LLM = False
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"