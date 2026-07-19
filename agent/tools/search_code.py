from pathlib import Path
from agent.tools.base_tool import BaseTool

class SearchCodeTool(BaseTool):
    name = "search_code"
    description = "Cerca testo nel codice"
    parameters = {
        "type": "object",
        "properties": {
            "root": {"type": "string", "description": "Cartella radice da cui iniziare la ricerca"},
            "query": {"type": "string", "description": "Testo da cercare (case-insensitive)"},
        },
        "required": ["root", "query"],
    }

    def execute(self, root, query):
        results = []
        for file in Path(root).rglob("*"):
            if file.is_file():
                try:
                    txt = file.read_text(encoding="utf-8")
                    if query.lower() in txt.lower():
                        results.append(str(file))
                except Exception:
                    pass
        return results
