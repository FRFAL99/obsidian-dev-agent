from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager


class ListProjectsTool(BaseTool):
    name = "list_projects"
    description = "Elenca i progetti disponibili nel vault, con nome, breve descrizione e quale è attivo."
    parameters = {"type": "object", "properties": {}, "required": []}

    def execute(self):
        return ProjectManager().list_projects()
