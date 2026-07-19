import json
from pathlib import Path
from agent.config import VAULT_PATH

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
