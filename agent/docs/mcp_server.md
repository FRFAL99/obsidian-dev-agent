# Server MCP

Espone gli stessi tool disponibili in chat (`list_projects`, `switch_project`,
`init_project`, `read_file`, `search_code`, `update_devlog`, `write_doc` — non `git`,
tenuto solo interno) come server MCP (Model Context Protocol) standard, così che
qualunque assistente di coding con cui stai già lavorando (Claude Code, Claude Desktop,
o altri client MCP presenti/futuri) possa richiamarli direttamente, senza passare dal
chatbot Gradio separato.

Il server (`agent/mcp_server.py`) è generico: non contiene nulla di specifico per un
client in particolare. Comunica su stdio (stdin/stdout in JSON-RPC), lo standard per
server MCP locali — qualunque client che parli MCP lo può usare con lo stesso comando.

## Setup

```bash
# Installare le dipendenze (include il pacchetto mcp)
python3 -m pip --python mcp_env/bin/python3 install -r requirements.txt

# .env deve già esistere con VAULT_PATH/PROJECTS_PATH configurati (vedi agent_usage.md)
```

## Registrazione con Claude Code

```bash
claude mcp add obsidian-dev-agent -s user -- \
  /home/frfal/frfal/obsidian-dev-agent/mcp_env/bin/python3 \
  /home/frfal/frfal/obsidian-dev-agent/agent/mcp_server.py
```

`-s user`: disponibile in ogni sessione Claude Code su questa macchina, in qualunque
progetto tu stia lavorando — non solo dentro il repo `obsidian-dev-agent`.

Dopo la registrazione, serve una nuova sessione Claude Code perché il server venga
caricato (la registrazione non è "a caldo" su sessioni già aperte).

## Registrazione con altri client MCP

Stesso principio, stesso comando+argomenti assoluti, cambia solo dove il client li
configura. Esempio Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "obsidian-dev-agent": {
      "command": "/home/frfal/frfal/obsidian-dev-agent/mcp_env/bin/python3",
      "args": ["/home/frfal/frfal/obsidian-dev-agent/agent/mcp_server.py"]
    }
  }
}
```

Path assoluti per interprete e script: necessario perché il client spawna il processo
da una cwd non garantita (qualunque progetto tu abbia aperto in quel momento).

## Perché FastMCP

Il server usa `mcp.server.fastmcp.FastMCP` (API alto livello, documentata e stabile),
non l'API a basso livello `Server`/`@list_tools()`/`@call_tool()` — quest'ultima
permetterebbe di generare i tool MCP direttamente da `ToolRegistry` (zero duplicazione
degli schemi), ma l'SDK Python di MCP sta attraversando un rework importante (v2), quindi
si è preferita l'API più stabile per questa prima versione. Ogni tool MCP è una funzione
wrapper tipata che delega interamente a `tool.execute()` già esistente — la logica
(path-safety, commit/push automatico, ecc.) non è duplicata, solo la firma.

## Nota tecnica: perché `sys.path.insert` in cima al file

Quando un client MCP spawna `agent/mcp_server.py` per path assoluto (non con
`python -m`), Python non aggiunge automaticamente la root del repo al `sys.path`, quindi
`agent` non risulterebbe un pacchetto importabile. Il file risolve questo da solo in
testa (`sys.path.insert(0, ...)`), così funziona indipendentemente da come/da dove viene
invocato — verificato con un client MCP di test che lo spawna da una cwd diversa dal repo.
