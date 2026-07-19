# Architettura del tool-calling

## Flusso

```
utente (chat Gradio)
    │
    ▼
agent/server.py ──► Agent.ask(msg, history)
                         │
                         ├─ PromptBuilder.build()  → messaggi di sistema + contesto progetto
                         ├─ ToolRegistry.openai_schemas() → schemi dei tool per l'LLM
                         │
                         ▼
                    agent/llm.py::chat(messages, tools=schemi)
                         │
                         ▼
              risposta LLM: contenuto testuale  O  tool_calls
                         │
              se tool_calls ──► ToolRegistry esegue ogni tool richiesto
                         │            │
                         │            ▼
                         │      agent/vault/vault_manager.py
                         │      (scrive nel vault + commit/push git mirato)
                         │
                         └─ risultato del tool re-iniettato come messaggio role="tool"
                                       │
                                       ▼
                         si richiama l'LLM (fino a max_iterations)
                                       │
                                       ▼
                         risposta testuale finale mostrata in chat
```

## Schema dei tool (JSON Schema, formato OpenAI function-calling)

Ogni tool eredita da `agent/tools/base_tool.py::BaseTool`, che espone `name`, `description` e
`parameters` (JSON Schema dei parametri di `execute()`) come attributi di classe:

```python
class BaseTool:
    name = ""
    description = ""
    parameters = {"type": "object", "properties": {}, "required": []}

    def to_openai_schema(self):
        return {"type": "function", "function": {
            "name": self.name, "description": self.description, "parameters": self.parameters,
        }}
```

`ToolRegistry.load()` scansiona `agent/tools/*.py`, importa ogni modulo (isolando eventuali
errori di un singolo tool con un `try/except`, così un tool rotto non impedisce il caricamento
degli altri) e registra ogni sottoclasse di `BaseTool` trovata. `ToolRegistry.openai_schemas()`
genera la lista da passare a `chat(tools=...)`, escludendo i tool elencati in `HIDDEN_TOOLS`
(oggi: `git`, riservato a uso interno).

## Loop di orchestrazione (`agent/agent.py`)

```python
for _ in range(max_iterations):
    message = chat(messages, tools=tools_schema)
    messages.append({"role": "assistant", "content": message.content or "", ...tool_calls...})
    if not message.tool_calls:
        return message.content
    for call in message.tool_calls:
        tool = registry.tools.get(call.function.name)
        result = tool.execute(**json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
```

Punti di attenzione:
- `max_iterations` (default 5) evita loop infiniti se un tool fallisce ripetutamente.
- Argomenti JSON malformati restituiti dal modello vengono catturati ed esposti come errore nel
  messaggio `role="tool"`, senza far crashare il loop.
- I risultati non stringa (es. dict) vengono serializzati con `json.dumps` prima di essere
  reinseriti nella history.
- Il campo `reasoning_content` (thinking di Qwen3) non viene re-iniettato nella history: solo
  `content` e `tool_calls` sono standard OpenAI.

## Sync col vault (`agent/vault/vault_manager.py`)

`_commit_and_push(paths, message)` accetta una LISTA di path (uno o più) e fa un solo commit+push
che li copre tutti:

1. Fa `git add` **solo** dei file effettivamente toccati (mai `git add -A`/`.`), per non includere
   nel commit il rumore di `.obsidian/workspace.json` o delle cache `.smart-env/*.ajson` che
   cambiano ad ogni apertura di Obsidian.
2. Committa con autore `Documentation Agent <agent@local>`.
3. Fa `push`; se fallisce (rete assente, conflitto) logga l'errore ma non solleva eccezioni: i
   file sono comunque salvati e committati in locale, il push verrà ritentato al prossimo giro.

`append_note`/`create_note_if_missing` (usati da `update_devlog`/`write_doc`) chiamano
`_commit_and_push` con un solo file, messaggio `docs: aggiorna <path>`. `create_files_and_commit`
(usato da `init_project`) scrive più file in un colpo solo con un pre-check "tutto o niente" (se
anche uno solo esiste già, niente viene scritto) e un unico commit `docs: inizializza progetto <nome>`.

## Path-safety: due assi paralleli

Esistono due percorsi di risoluzione path indipendenti in `agent/project_manager.py`, da non confondere:

- **`resolve_note_path()`** — per le **scritture** (`write_doc`/`update_devlog`): risolve `path`
  contro `vault_path` (cartella del progetto nel vault Obsidian) e rifiuta con `ValueError` ogni
  percorso che uscirebbe da quella cartella.
- **`resolve_repo_path()`** — per le **letture** (`read_file`/`search_code`, quando il path non è
  assoluto): risolve `path` contro `repo_path` (cartella del codice sorgente reale sul filesystem,
  letta da `ai/project.json`) con la stessa protezione anti path-traversal.

In entrambi i casi il path arriva in ultima istanza da testo utente/LLM non fidato, quindi va
sempre validato prima di toccare il filesystem.

## Gestione progetti (`list_projects` / `switch_project` / `init_project`)

- `ProjectManager.list_projects()` elenca `VAULT_PATH/projects/*/` con `ai/project.json` valido,
  marcando `active` (confronto con `.current_project`) e `complete` (presenza di
  README/architettura/devlog/TODO) senza escludere i progetti incompleti.
- `ProjectManager.switch_to(name)` valida che il nome sia uno slug sicuro (`^[a-zA-Z0-9_-]+$`,
  anti path-traversal sul nome stesso) e che il progetto esista, poi scrive `.current_project`.
  È l'unica scrittura che **non** passa da un commit: è stato locale (quale progetto sto
  guardando ora), non contenuto documentale.
- `ProjectManager.discover_repo_candidates(name_hint)` — usato da `init_project` quando
  `repo_path` è omesso — cerca ricorsivamente (fino a 3 livelli, escludendo `node_modules`,
  `.git`, `venv`, `mcp_env`, `__pycache__`, `dist`, `build`) cartelle con un `.git` il cui nome
  contiene `name_hint`. Se il match non è unico, l'errore elenca i candidati invece di indovinare.
