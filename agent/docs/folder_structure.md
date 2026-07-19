# Struttura del progetto

```
obsidian-dev-agent/
├── .env.example           # template variabili d'ambiente (copiare in .env)
├── .gitignore
├── requirements.txt        # gradio, openai, python-dotenv, requests, gitpython
├── README.md
└── agent/
    ├── __init__.py
    ├── agent.py             # classe Agent: loop di tool-calling (PromptBuilder + chat + ToolRegistry)
    ├── config.py             # legge .env: LLM_BASE_URL, LLM_MODEL, VAULT_PATH, PROJECTS_PATH
    ├── llm.py                 # client OpenAI-compatible verso llama.cpp locale
    ├── prompt_builder.py       # costruisce i messaggi di sistema dal contesto del progetto corrente
    ├── project_manager.py      # legge .current_project / ai/project.json dal vault, risolve path in sicurezza
    ├── server.py                # entrypoint: Gradio ChatInterface che usa Agent()
    ├── tool_registry.py          # carica dinamicamente i tool da agent/tools/, genera gli schemi per l'LLM
    ├── docs/                     # questa documentazione
    ├── tools/
    │   ├── base_tool.py           # classe base: name, description, parameters (JSON Schema), execute()
    │   ├── read_file.py            # legge un file dal filesystem
    │   ├── search_code.py           # cerca una stringa nei file sotto una cartella
    │   ├── update_devlog.py          # aggiunge una entry a devlog.md del progetto corrente (append-only)
    │   ├── write_doc.py               # crea/aggiorna un file Markdown nel progetto corrente
    │   └── git_tool.py                 # operazioni git generiche; NON esposto all'LLM in chat (uso interno)
    └── vault/
        └── vault_manager.py            # read/append/create note nel vault + commit/push automatico mirato
```

## Cosa è stato rimosso e perché

Il progetto conteneva uno scaffolding a più livelli (`agent/capabilities/`, `agent/services/`,
`agent/tools/agent_tools/`, `agent/documentation_engine.py`, `agent/memory_engine.py`) risultato
di un refactor incompleto: import verso moduli/cartelle mai esistiti, classi mai istanziate da
nessun punto d'ingresso reale. È stato rimosso interamente invece di essere riparato, perché il
loop di tool-calling in `agent.py` + `tool_registry.py` copre lo stesso bisogno (l'LLM che decide
quali tool chiamare) in modo più semplice e verificato.

`documentation_engine.py` in particolare era uno stub che scriveva JSON in una cartella locale,
scollegato dal vault Obsidian: è stato sostituito dal tool `write_doc.py`, che scrive davvero
Markdown nel vault.
