import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Database Configuration (PostgreSQL required)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/jee_agent"
)

# Model Configuration
PRIMARY_MODEL = "mistral/mistral-large-latest"
FALLBACK_MODEL = "groq/llama-3.3-70b-versatile"
FAST_MODEL = "mistral/open-mistral-nemo"
EMBEDDING_MODEL = "mistral-embed"

# JEE Exam Config
EXAM_DATE = "2026-01-23"
TOTAL_MARKS = 300
QUESTIONS_PER_SUBJECT = 25

# Session Config
MAX_SESSION_HOURS = 3
BREAK_INTERVAL_MINS = 90
DEFAULT_DAILY_HOURS = 10