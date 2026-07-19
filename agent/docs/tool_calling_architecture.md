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

Ogni scrittura (`append_note` / `create_note_if_missing`) esegue in coda `_commit_and_push`, che:

1. Fa `git add` **solo** del file appena scritto (mai `git add -A`/`.`), per non includere nel
   commit il rumore di `.obsidian/workspace.json` o delle cache `.smart-env/*.ajson` che cambiano
   ad ogni apertura di Obsidian.
2. Committa con autore `Documentation Agent <agent@local>` e messaggio `docs: aggiorna <path>`.
3. Fa `push`; se fallisce (rete assente, conflitto) logga l'errore ma non solleva eccezioni: il
   file è comunque salvato e committato in locale, il push verrà ritentato al prossimo giro.

## Path-safety

`agent/project_manager.py::resolve_note_path()` risolve ogni `path` ricevuto da un tool contro la
cartella del progetto **corrente** (non contro la root del vault) e rifiuta con `ValueError` ogni
percorso che, una volta risolto, finirebbe fuori da quella cartella. Necessario perché `path`
arriva in ultima istanza da testo utente/LLM non fidato.
