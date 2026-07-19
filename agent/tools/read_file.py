from pathlib import Path
from agent.tools.base_tool import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Legge un file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Percorso del file da leggere"},
        },
        "required": ["path"],
    }

    def execute(self, path):
        return Path(path).read_text(encoding="utf-8")
