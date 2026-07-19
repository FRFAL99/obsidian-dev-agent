from dotenv import load_dotenv
from pathlib import Path
import os

# Path assoluto, indipendente dalla cwd del processo: necessario perché il server MCP
# viene spawnato da un client (Claude Code o altro) da una cwd non garantita, non solo
# da `python -m agent.server` lanciato a mano dalla root del repo.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3")
VAULT_PATH = os.getenv("VAULT_PATH", "")
PROJECTS_PATH = os.getenv("PROJECTS_PATH", "")
