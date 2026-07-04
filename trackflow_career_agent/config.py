import os

# Root package directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database path (stored in the storage subfolder)
DB_PATH = os.path.join(BASE_DIR, "storage", "trackflow.db")

# Default model configuration
DEFAULT_MODEL = "gemini-2.5-flash"
