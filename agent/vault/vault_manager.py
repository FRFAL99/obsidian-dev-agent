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


def _write_append(relative_path: str, text: str) -> Path:
    p = ROOT / relative_path
    p.parent.mkdir(parents=True, exist_ok=True)
    needs_leading_newline = p.exists() and p.stat().st_size > 0
    with open(p, "a", encoding="utf-8") as f:
        if needs_leading_newline:
            f.write("\n")
        f.write(text)
    return p


def _write_create(relative_path: str, text: str) -> Path:
    p = ROOT / relative_path
    if p.exists():
        raise FileExistsError(f"Il file esiste già nel vault: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def append_note(relative_path: str, text: str) -> str:
    _validate_root()
    p = _write_append(relative_path, text)
    _commit_and_push([p], f"docs: aggiorna {p.relative_to(ROOT)}")
    return str(p)


def create_note_if_missing(relative_path: str, text: str) -> str:
    _validate_root()
    p = _write_create(relative_path, text)
    _commit_and_push([p], f"docs: aggiorna {p.relative_to(ROOT)}")
    return str(p)


def create_files_and_commit(files: dict, message: str) -> list:
    """files: {relative_path: content}. Pre-check 'tutto o niente': se anche un solo file
    esiste già, solleva FileExistsError PRIMA di scrivere qualsiasi cosa (niente scaffold
    parziali). Un solo commit+push copre tutti i file scritti insieme."""
    _validate_root()
    paths = {rel: ROOT / rel for rel in files}
    existing = [rel for rel, p in paths.items() if p.exists()]
    if existing:
        raise FileExistsError(f"File già esistenti, scrittura multi-file annullata: {existing}")
    written = []
    for rel, content in files.items():
        p = paths[rel]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        written.append(p)
    _commit_and_push(written, message)
    return [str(p) for p in written]


def _commit_and_push(absolute_paths: list, message: str):
    """Commit + push mirato ai SOLI file toccati. Non fa mai `git add -A`/`.`,
    per non trascinare dentro il rumore di .obsidian/workspace.json e delle
    cache .smart-env/*.ajson che cambiano ad ogni apertura di Obsidian."""
    rels = [p.relative_to(ROOT) for p in absolute_paths]
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Documentation Agent",
        "GIT_AUTHOR_EMAIL": "agent@local",
        "GIT_COMMITTER_NAME": "Documentation Agent",
        "GIT_COMMITTER_EMAIL": "agent@local",
    }
    try:
        subprocess.run(
            ["git", "add"] + [str(r) for r in rels],
            cwd=ROOT, check=True, capture_output=True, text=True, env=env,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logger.warning(f"git commit fallito su {rels}: {result.stderr}")
            return
        push = subprocess.run(
            ["git", "push"],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        if push.returncode != 0:
            logger.error(f"git push fallito per {rels}: {push.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"git add fallito su {rels}: {e.stderr}")
