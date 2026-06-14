from pathlib import Path
from agent.tools.base_tool import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Legge un file"

    def execute(self, path):
        return Path(path).read_text(encoding="utf-8")
