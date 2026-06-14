from pathlib import Path
from agent.config import VAULT_PATH

ROOT = Path(VAULT_PATH)

def read_note(relative_path:str):
    return (ROOT / relative_path).read_text(encoding="utf-8")

def append_note(relative_path:str, text:str):
    p = ROOT / relative_path
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(text)
