from datetime import date
from agent.vault.vault_manager import append_note
from agent.tools.base_tool import BaseTool

class UpdateDevlogTool(BaseTool):
    name = "update_devlog"
    description = "Aggiunge una entry al devlog"

    def execute(self, path, content):
        today = date.today().isoformat()
        entry = f"\n## {today}\n\n### Fatto\n\n- {content}\n"
        append_note(path, entry)
        return "OK"
