import sys
from pathlib import Path

# Necessario perché il server viene spawnato da un client MCP come script per path
# assoluto (non con `python -m`), da una cwd non garantita: senza questo, "agent" non
# risulta un pacchetto importabile.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP

from agent.tools.read_file import ReadFileTool
from agent.tools.search_code import SearchCodeTool
from agent.tools.update_devlog import UpdateDevlogTool
from agent.tools.write_doc import WriteDocTool
from agent.tools.list_projects import ListProjectsTool
from agent.tools.switch_project import SwitchProjectTool
from agent.tools.init_project import InitProjectTool

mcp = FastMCP("obsidian-dev-agent")


@mcp.tool()
def read_file(path: str) -> str:
    """Legge un file. Path assoluto: usato così com'è. Path relativo: risolto contro il repo_path del progetto attivo."""
    return ReadFileTool().execute(path=path)


@mcp.tool()
def search_code(query: str, root: str | None = None) -> list[str]:
    """Cerca una stringa (case-insensitive) nel codice. root opzionale: se omesso usa il repo_path del progetto attivo."""
    return SearchCodeTool().execute(query=query, root=root)


@mcp.tool()
def update_devlog(path: str, content: str) -> str:
    """Aggiunge una entry datata a devlog.md del progetto corrente. Sempre append, mai sovrascrive."""
    return UpdateDevlogTool().execute(path=path, content=content)


@mcp.tool()
def write_doc(path: str, content: str, mode: str) -> str:
    """Crea o aggiorna un file Markdown nel progetto corrente. mode: 'append' o 'create_if_missing'."""
    return WriteDocTool().execute(path=path, content=content, mode=mode)


@mcp.tool()
def list_projects() -> list[dict]:
    """Elenca i progetti nel vault: nome, descrizione, se completo, quale è attivo."""
    return ListProjectsTool().execute()


@mcp.tool()
def switch_project(name: str) -> str:
    """Cambia il progetto attivo (deve già esistere)."""
    return SwitchProjectTool().execute(name=name)


@mcp.tool()
def init_project(name: str, repo_path: str | None = None) -> dict:
    """Crea un nuovo progetto nel vault (scaffold minimo). Se repo_path è omesso, auto-discovery via PROJECTS_PATH."""
    return InitProjectTool().execute(name=name, repo_path=repo_path)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
