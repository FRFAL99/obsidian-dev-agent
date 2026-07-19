import logging
import os
import subprocess
from pathlib import Path

from agent.config import VAULT_PATH

logger = logging.getLogger(__name__)

ROOT = Path(VAULT_PATH)


def _validate_root():
    if not VAULT_PATH:
        raise RuntimeError("VAULT_PATH non configurato (manca .env?). Impossibile operare sul vault.")
    if not ROOT.exists():
        raise RuntimeError(f"VAULT_PATH '{VAULT_PATH}' non esiste sul filesystem.")


def read_note(relative_path: str) -> str:
    _validate_root()
    p = ROOT / relative_path
    if not p.exists():
        raise FileNotFoundError(f"Nota non trovata nel vault: {p}")
    return p.read_text(encoding="utf-8")


def append_note(relative_path: str, text: str) -> str:
    _validate_root()
    p = ROOT / relative_path
    p.parent.mkdir(parents=True, exist_ok=True)
    needs_leading_newline = p.exists() and p.stat().st_size > 0
    with open(p, "a", encoding="utf-8") as f:
        if needs_leading_newline:
            f.write("\n")
        f.write(text)
    _commit_and_push(p)
    return str(p)


def create_note_if_missing(relative_path: str, text: str) -> str:
    _validate_root()
    p = ROOT / relative_path
    if p.exists():
        raise FileExistsError(f"Il file esiste già nel vault: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    _commit_and_push(p)
    return str(p)


def _commit_and_push(absolute_path: Path):
    """Commit + push mirato al SOLO file toccato. Non fa mai `git add -A`/`.`,
    per non trascinare dentro il rumore di .obsidian/workspace.json e delle
    cache .smart-env/*.ajson che cambiano ad ogni apertura di Obsidian."""
    rel = absolute_path.relative_to(ROOT)
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Documentation Agent",
        "GIT_AUTHOR_EMAIL": "agent@local",
        "GIT_COMMITTER_NAME": "Documentation Agent",
        "GIT_COMMITTER_EMAIL": "agent@local",
    }
    try:
        subprocess.run(
            ["git", "add", str(rel)],
            cwd=ROOT, check=True, capture_output=True, text=True, env=env,
        )
        result = subprocess.run(
            ["git", "commit", "-m", f"docs: aggiorna {rel}"],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logger.warning(f"git commit fallito su {rel}: {result.stderr}")
            return
        push = subprocess.run(
            ["git", "push"],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if push.returncode != 0:
            logger.error(f"git push fallito per {rel}: {push.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"git add fallito su {rel}: {e.stderr}")
