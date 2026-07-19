from datetime import date
from agent.vault.vault_manager import append_note
from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager

class UpdateDevlogTool(BaseTool):
    name = "update_devlog"
    description = "Aggiunge una entry al devlog.md del progetto corrente. Sempre in append, mai sovrascrive."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Percorso relativo al progetto corrente del devlog, es. 'devlog.md'"},
            "content": {"type": "string", "description": "Cosa è stato fatto, in una riga"},
        },
        "required": ["path", "content"],
    }

    def execute(self, path, content):
        today = date.today().isoformat()
        entry = f"\n## {today}\n\n### Fatto\n\n- {content}\n"
        safe_path = ProjectManager().resolve_note_path(path)
        append_note(str(safe_path), entry)
        return "OK"
