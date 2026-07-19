from pathlib import Path
from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager

class SearchCodeTool(BaseTool):
    name = "search_code"
    description = (
        "Cerca testo nel codice. root opzionale: se omesso, usa il repo_path del progetto "
        "attivo; se assoluto viene usato così com'è; se relativo viene risolto contro il "
        "repo_path del progetto attivo."
    )
    parameters = {
        "type": "object",
        "properties": {
            "root": {"type": "string", "description": "Cartella radice (assoluta o relativa al progetto corrente); se omessa, repo_path del progetto attivo"},
            "query": {"type": "string", "description": "Testo da cercare (case-insensitive)"},
        },
        "required": ["query"],
    }

    def execute(self, query, root=None):
        if root is None:
            base = ProjectManager().current_repo_path()
        else:
            p = Path(root)
            base = p if p.is_absolute() else ProjectManager().resolve_repo_path(root)

        results = []
        for file in base.rglob("*"):
            if file.is_file():
                try:
                    txt = file.read_text(encoding="utf-8")
                    if query.lower() in txt.lower():
                        results.append(str(file))
                except Exception:
                    pass
        return results
