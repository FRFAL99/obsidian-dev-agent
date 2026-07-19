from agent.tools.base_tool import BaseTool
from agent.project_manager import ProjectManager
from agent.vault import vault_manager


class WriteDocTool(BaseTool):
    name = "write_doc"
    description = (
        "Scrive o aggiorna un file Markdown nel vault del progetto corrente "
        "(es. TODO.md, architettura.md, note in improvements/). Non sovrascrive mai contenuto esistente."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Percorso relativo al progetto corrente, es. 'TODO.md' o 'improvements/nuova-nota.md'",
            },
            "content": {
                "type": "string",
                "description": "Contenuto Markdown da aggiungere (append) o da usare per creare il file",
            },
            "mode": {
                "type": "string",
                "enum": ["append", "create_if_missing"],
                "description": "append: aggiunge in coda a un file esistente (o lo crea se non c'è). "
                                "create_if_missing: crea il file solo se non esiste già, altrimenti errore.",
            },
        },
        "required": ["path", "content", "mode"],
    }

    def execute(self, path, content, mode):
        safe_path = str(ProjectManager().resolve_note_path(path))

        if mode == "append":
            return vault_manager.append_note(safe_path, content)
        elif mode == "create_if_missing":
            return vault_manager.create_note_if_missing(safe_path, content)
        else:
            raise ValueError(f"mode non valido: {mode!r} (atteso 'append' o 'create_if_missing')")
