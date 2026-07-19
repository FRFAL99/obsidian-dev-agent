import json
from pathlib import Path

from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager, SAFE_SLUG
from agent.config import VAULT_PATH
from agent.vault import vault_manager


class InitProjectTool(BaseTool):
    name = "init_project"
    description = (
        "Crea un nuovo progetto nel vault con lo scaffold minimo (ai/project.json, README.md, "
        "architettura.md, devlog.md, TODO.md, ai/context.md). Se repo_path è omesso, cerca "
        "automaticamente il repository sotto PROJECTS_PATH."
    )
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Nome/slug del progetto (lettere, cifre, - e _)"},
            "repo_path": {"type": "string", "description": "Percorso assoluto del repo sorgente; se omesso, auto-discovery via PROJECTS_PATH"},
        },
        "required": ["name"],
    }

    def execute(self, name, repo_path=None):
        pm = ProjectManager()

        if not SAFE_SLUG.match(name):
            raise ValueError(f"Nome non valido: {name!r} (atteso [a-zA-Z0-9_-]+)")
        if (pm.root / name / 'ai' / 'project.json').exists():
            raise FileExistsError(f"Il progetto '{name}' esiste già.")

        if repo_path is None:
            candidates = pm.discover_repo_candidates(name)
            if len(candidates) != 1:
                raise RuntimeError(
                    f"Match trovati per '{name}' sotto PROJECTS_PATH: {len(candidates)} "
                    f"({[str(c) for c in candidates]}). Specifica repo_path esplicitamente."
                )
            repo_path = str(candidates[0])
        elif not Path(repo_path).exists():
            raise RuntimeError(f"repo_path '{repo_path}' non esiste sul filesystem.")

        vp = f"projects/{name}"
        project_json = json.dumps({
            "name": name,
            "repo_path": repo_path,
            "vault_path": str(Path(VAULT_PATH) / vp),
            "default_branch": "main",
            "languages": [],
        }, indent=2, ensure_ascii=False)

        files = {
            f"{vp}/ai/project.json": project_json,
            f"{vp}/README.md": f"# {name}\n\n_Descrizione da completare._\n",
            f"{vp}/architettura.md": "# Architettura\n\n_Da completare._\n",
            f"{vp}/devlog.md": f"# Devlog — {name}\n",
            f"{vp}/TODO.md": "# TODO\n",
            f"{vp}/ai/context.md": f"# Context\n\n## Nome progetto\n{name}\n\n## Repository\n`{repo_path}`\n",
        }
        written = vault_manager.create_files_and_commit(files, f"docs: inizializza progetto {name}")
        return {"created": written, "repo_path": repo_path}
