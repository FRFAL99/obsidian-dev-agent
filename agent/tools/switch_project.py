from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager


class SwitchProjectTool(BaseTool):
    name = "switch_project"
    description = "Cambia il progetto attivo. Il progetto deve già esistere (vedi list_projects/init_project)."
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Nome esatto del progetto (slug: lettere, cifre, - e _)"},
        },
        "required": ["name"],
    }

    def execute(self, name):
        ProjectManager().switch_to(name)
        return f"Progetto attivo ora: {name}"
