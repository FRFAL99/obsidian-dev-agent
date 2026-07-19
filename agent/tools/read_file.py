from pathlib import Path
from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager

class ReadFileTool(BaseTool):
    name = "read_file"
    description = (
        "Legge un file. Se il path è assoluto viene usato così com'è; se è relativo, "
        "viene risolto contro il repo_path del progetto attivo."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Percorso assoluto, oppure relativo al repo del progetto corrente"},
        },
        "required": ["path"],
    }

    def execute(self, path):
        p = Path(path)
        if not p.is_absolute():
            p = ProjectManager().resolve_repo_path(path)
        return p.read_text(encoding="utf-8")
