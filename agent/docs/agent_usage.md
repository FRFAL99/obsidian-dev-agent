# Obsidian Dev Agent — Guida d'uso

Agente locale che chatta con un LLM (llama.cpp, modello configurabile) e può scrivere
documentazione direttamente nel vault Obsidian del progetto su cui stai lavorando, tramite
tool-calling: durante la conversazione l'LLM decide autonomamente se e quando chiamare uno dei
tool disponibili.

## Setup

```bash
# 1. Installare le dipendenze Python nel venv del progetto (mcp_env non include pip al suo
# interno: si usa il pip di sistema puntato al python del venv con --python)
python3 -m pip --python mcp_env/bin/python3 install -r requirements.txt

# 2. Configurare l'ambiente
cp .env.example .env
# poi modificare .env con i tuoi percorsi reali:
#   VAULT_PATH=/percorso/al/tuo/vault-obsidian
#   PROJECTS_PATH=/percorso/ai/tuoi/repo
#   LLM_BASE_URL=http://localhost:8080/v1   (endpoint OpenAI-compatible, es. llama.cpp)
#   LLM_MODEL=qwen3

# 3. Assicurarsi che il server LLM (llama.cpp) sia in ascolto su LLM_BASE_URL
```

## Avvio

```bash
mcp_env/bin/python -m agent.server
```

Apre una chat Gradio su `http://localhost:7860`.

## Contesto di progetto

Il vault deve avere una struttura per progetto:

```
vault/
├── .current_project              # nome del progetto attivo, es. "antichita-fallavena"
└── projects/
    └── <nome-progetto>/
        ├── README.md, architettura.md, devlog.md, TODO.md
        └── ai/
            ├── project.json        # {"name", "repo_path", "vault_path", "default_branch", "languages"}
            ├── context.md, rules.md, memory.md, prompts.md
```

All'avvio di ogni richiesta, l'agente legge `.current_project` per sapere qual è il progetto
attivo, poi inietta come contesto di sistema `README.md`, `architettura.md`, `ai/context.md`,
`ai/rules.md`, `ai/memory.md` del progetto corrente (se presenti). Se `.current_project` o
`ai/project.json` mancano, l'agente funziona comunque ma senza contesto di progetto.

## Tool disponibili in chat

L'LLM può chiamare questi tool durante la conversazione (schemi generati automaticamente da
`agent/tool_registry.py`):

- **`read_file(path)`** — legge un file dal filesystem.
- **`search_code(root, query)`** — cerca una stringa (case-insensitive) nei file sotto `root`.
- **`update_devlog(path, content)`** — aggiunge una entry datata a `devlog.md` del progetto
  corrente. Sempre in append, non sovrascrive mai.
- **`write_doc(path, content, mode)`** — crea o aggiorna un file Markdown nel progetto corrente
  (`mode="append"` per aggiungere in coda, `mode="create_if_missing"` per creare solo se non
  esiste già). Non sovrascrive mai contenuto esistente.

Il tool `git` esiste nel codice ma **non è esposto all'LLM in chat** (è riservato a uso interno):
il commit/push sul vault è già automatico dentro `write_doc`/`update_devlog`, non serve che il
modello lo richiami esplicitamente, ed evitare di esporlo previene che un comando git arbitrario
venga eseguito da testo generato dal modello.

## Regole di scrittura nel vault

- `path` viene sempre risolto contro la cartella del progetto **corrente**, mai contro la root
  del vault: un tentativo di uscire dal progetto (es. `../../.obsidian/workspace.json`) viene
  rifiutato esplicitamente.
- Ogni scrittura riuscita genera un commit + push automatico nel repo del vault, mirato al solo
  file toccato (mai `git add -A`), con autore `Documentation Agent <agent@local>` e messaggio
  `docs: aggiorna <path>`. Se il push fallisce (es. rete assente), il file resta comunque scritto
  e committato in locale: nessun dato viene perso, il push va ripetuto al giro successivo.
- `devlog.md` è append-only per design: non esiste un parametro che permetta di sovrascriverlo.
