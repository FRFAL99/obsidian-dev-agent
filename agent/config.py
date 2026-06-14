from dotenv import load_dotenv
import os

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3")
VAULT_PATH = os.getenv("VAULT_PATH", "")
PROJECTS_PATH = os.getenv("PROJECTS_PATH", "")
