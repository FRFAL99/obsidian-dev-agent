import json
import re
from pathlib import Path
from agent.config import VAULT_PATH

SAFE_SLUG = re.compile(r'^[a-zA-Z0-9_-]+$')
DISCOVERY_SKIP = {'node_modules', '.git', 'venv', '.venv', 'mcp_env', '__pycache__', 'dist', 'build'}


class ProjectManager:
    def __init__(self): self.root=Path(VAULT_PATH)/'projects'; self.cur=Path(VAULT_PATH)/'.current_project'
    def current_config(self):
        if not self.cur.exists(): return None
        n=self.cur.read_text().strip()
        project_json = self.root/n/'ai'/'project.json'
        if not project_json.exists(): return None
        return json.loads(project_json.read_text())

    def current_project_dir(self) -> Path:
        """Cartella del progetto attivo nel vault. Solleva RuntimeError se non c'è un progetto corrente configurato."""
        cfg = self.current_config()
        if not cfg:
            raise RuntimeError("Nessun progetto corrente configurato nel vault (.current_project / ai/project.json mancanti).")
        return Path(cfg['vault_path'])

    def resolve_note_path(self, relative_path: str) -> Path:
        """Risolve relative_path contro la cartella del progetto corrente, rifiutando ogni path che
        finirebbe fuori da quella cartella (protezione da path-traversal, es. '../../.obsidian/workspace.json')."""
        project_dir = self.current_project_dir().resolve()
        resolved = (project_dir / relative_path).resolve()
        if resolved != project_dir and project_dir not in resolved.parents:
            raise ValueError(f"Path fuori dal progetto corrente, operazione rifiutata: {relative_path}")
        return resolved.relative_to(Path(VAULT_PATH).resolve())

    def list_projects(self):
        """Elenca VAULT_PATH/projects/*/ con ai/project.json valido (JSON parsabile).
        Non richiede README/architettura/devlog/TODO: il requisito minimo per essere 'un
        progetto' resta ai/project.json. Progetti incompleti vengono inclusi con
        complete=False, non esclusi: l'LLM può segnalarlo invece di nasconderlo."""
        current = self.cur.read_text().strip() if self.cur.exists() else None
        out = []
        if not self.root.exists():
            return out
        for d in sorted(self.root.iterdir()):
            if not d.is_dir():
                continue
            pj = d / 'ai' / 'project.json'
            if not pj.exists():
                continue
            try:
                cfg = json.loads(pj.read_text())
            except json.JSONDecodeError:
                continue
            first_line = ''
            readme = d / 'README.md'
            if readme.exists():
                for line in readme.read_text().splitlines():
                    if line.strip():
                        first_line = line.lstrip('#').strip()
                        break
            out.append({
                'name': cfg.get('name', d.name),
                'description': first_line,
                'active': d.name == current,
                'complete': all((d / f).exists() for f in ('README.md', 'architettura.md', 'devlog.md', 'TODO.md')),
            })
        return out

    def switch_to(self, name: str) -> str:
        """Cambia il progetto attivo scrivendo .current_project. Stato locale, non versionato
        nel vault (non è documentazione)."""
        if not SAFE_SLUG.match(name):
            raise ValueError(f"Nome progetto non valido: {name!r} (atteso [a-zA-Z0-9_-]+)")
        if not (self.root / name / 'ai' / 'project.json').exists():
            raise FileNotFoundError(f"Progetto '{name}' non trovato (manca ai/project.json)")
        self.cur.write_text(name)
        return name

    def current_repo_path(self) -> Path:
        """Cartella del repo sorgente reale del progetto attivo (campo repo_path in ai/project.json,
        distinto da vault_path). Solleva RuntimeError se manca progetto/repo_path o non esiste su disco."""
        cfg = self.current_config()
        if not cfg:
            raise RuntimeError("Nessun progetto corrente configurato.")
        rp = cfg.get('repo_path')
        if not rp:
            raise RuntimeError(f"Il progetto corrente ({cfg.get('name')}) non ha 'repo_path' in ai/project.json.")
        p = Path(rp)
        if not p.exists():
            raise RuntimeError(f"repo_path '{rp}' del progetto corrente non esiste sul filesystem.")
        return p

    def resolve_repo_path(self, relative_path: str) -> Path:
        """Come resolve_note_path ma per il repo_path (letture di codice sorgente, non
        scritture nel vault): rifiuta ogni path che uscirebbe dal repo del progetto corrente."""
        repo_dir = self.current_repo_path().resolve()
        resolved = (repo_dir / relative_path).resolve()
        if resolved != repo_dir and repo_dir not in resolved.parents:
            raise ValueError(f"Path fuori dal repo del progetto corrente, operazione rifiutata: {relative_path}")
        return resolved

    def discover_repo_candidates(self, name_hint: str, max_depth: int = 3):
        """Scansiona PROJECTS_PATH cercando cartelle con .git il cui nome contiene name_hint
        (case-insensitive), fino a max_depth livelli (alcuni repo reali sono annidati, es.
        PROJECTS_PATH/Curriculum/Curriculum/.git). Esclude DISCOVERY_SKIP dalla ricorsione."""
        from agent.config import PROJECTS_PATH
        if not PROJECTS_PATH:
            raise RuntimeError("PROJECTS_PATH non configurato in .env.")
        base = Path(PROJECTS_PATH)
        hint = name_hint.lower()
        found = []

        def walk(d: Path, depth: int):
            if depth > max_depth:
                return
            try:
                entries = list(d.iterdir())
            except (PermissionError, OSError):
                return
            for e in entries:
                if not e.is_dir() or e.name in DISCOVERY_SKIP:
                    continue
                if (e / '.git').is_dir() and hint in e.name.lower():
                    found.append(e)
                walk(e, depth + 1)

        walk(base, 0)
        return found
