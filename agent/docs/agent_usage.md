# Obsidian Dev Agent — Guida d'uso

Agente che scrive documentazione direttamente nel vault Obsidian del progetto su cui stai
lavorando, tramite tool-calling: chi ti chiede di documentare decide autonomamente se e quando
chiamare uno dei tool disponibili — inclusa la gestione dei progetti stessi (crearli, elencarli,
cambiare quello attivo).

Due modi di usarlo:
- **Server MCP** (`agent/mcp_server.py`, consigliato) — gli stessi tool richiamabili direttamente
  da Claude Code o da qualunque altro client MCP, dentro la chat con cui stai già lavorando.
  Vedi `agent/docs/mcp_server.md`.
- **Chatbot Gradio standalone** (`agent/server.py`, modalità legacy/opzionale) — chat separata con
  un LLM locale (llama.cpp), descritta più sotto. Utile per uso offline senza un client MCP.

## Setup

```bash
# 1. Installare le dipendenze Python nel venv del progetto (mcp_env non include pip al suo
# interno: si usa il pip di sistema puntato al python del venv con --python)
python3 -m pip --python mcp_env/bin/python3 install -r requirements.txt

# 2. Configurare l'ambiente
cp .env.example .env
# poi modificare .env con i tuoi percorsi reali:
#   VAULT_PATH=/percorso/al/tuo/vault-obsidian
#   PROJECTS_PATH=/percorso/base/dove/vivono/i/tuoi/repo   (usato da init_project per l'auto-discovery)
#   LLM_BASE_URL=http://localhost:8080/v1   (endpoint OpenAI-compatible, es. llama.cpp)
#   LLM_MODEL=qwen3

# 3. Assicurarsi che il server LLM (llama.cpp) sia in ascolto su LLM_BASE_URL
```

## Avvio (chatbot Gradio standalone)

```bash
mcp_env/bin/python -m agent.server
```

Apre una chat Gradio su `http://localhost:7860`. Per usare invece il server MCP (consigliato),
vedi `agent/docs/mcp_server.md`.

## Contesto di progetto

Il vault ha una struttura per progetto, più un file di regole condiviso a livello di vault:

```
vault/
├── .current_project              # nome del progetto attivo, es. "curriculum"
├── ai/
│   └── global_rules.md            # regole comuni a TUTTI i progetti, iniettate sempre
└── projects/
    └── <nome-progetto>/
        ├── README.md, architettura.md, devlog.md, TODO.md
        └── ai/
            ├── project.json        # {"name", "repo_path", "vault_path", "default_branch", "languages"}
            ├── context.md, memory.md
            └── rules.md            # opzionale: solo eccezioni/convenzioni specifiche di QUESTO progetto
```

`repo_path` è distinto da `vault_path`: il primo punta al codice sorgente reale sul filesystem
(usato da `read_file`/`search_code`), il secondo alla cartella del progetto dentro il vault
(usato da `write_doc`/`update_devlog`). Non vanno confusi.

All'avvio di ogni richiesta, l'agente inietta sempre `vault/ai/global_rules.md` (se presente),
poi — se c'è un progetto attivo — anche `README.md`, `architettura.md`, `ai/context.md`,
`ai/rules.md`, `ai/memory.md` del progetto corrente (quelli che esistono). Se `.current_project`
o `ai/project.json` mancano, l'agente funziona comunque, con le sole regole globali.

## Tool disponibili

Stessi tool in entrambe le modalità (nel chatbot Gradio via `agent/tool_registry.py`, nel server
MCP via i wrapper in `agent/mcp_server.py` — stessa logica sottostante in entrambi i casi):

**Gestione progetti**
- **`list_projects()`** — elenca i progetti nel vault (nome, breve descrizione, se completo, quale è attivo).
- **`switch_project(name)`** — cambia il progetto attivo (deve già esistere). Scrive solo
  `.current_project`: è stato locale, non genera commit nel vault.
- **`init_project(name, repo_path=None)`** — crea un nuovo progetto nel vault con lo scaffold
  minimo (`ai/project.json`, README, architettura, devlog, TODO, `ai/context.md`) in un unico
  commit. Se `repo_path` è omesso, cerca automaticamente il repository sotto `PROJECTS_PATH`
  (per nome, fino a 3 livelli di profondità); se trova 0 o più match, chiede di specificarlo esplicitamente.

**Lettura codice**
- **`read_file(path)`** — legge un file. Path assoluto: usato così com'è. Path relativo: risolto
  contro il `repo_path` del progetto attivo (con protezione anti path-traversal).
- **`search_code(query, root=None)`** — cerca una stringa (case-insensitive) sotto `root`; se
  omesso, usa il `repo_path` del progetto attivo. Stessa risoluzione assoluto/relativo di `read_file`.

**Scrittura nel vault**
- **`update_devlog(path, content)`** — aggiunge una entry datata a `devlog.md` del progetto
  corrente. Sempre in append, non sovrascrive mai.
- **`write_doc(path, content, mode)`** — crea o aggiorna un file Markdown nel progetto corrente
  (`mode="append"` per aggiungere in coda, `mode="create_if_missing"` per creare solo se non
  esiste già). Non sovrascrive mai contenuto esistente.

Il tool `git` esiste nel codice ma **non è esposto all'LLM in chat** (è riservato a uso interno):
il commit/push sul vault è già automatico dentro `write_doc`/`update_devlog`/`init_project`, non
serve che il modello lo richiami esplicitamente, ed evitare di esporlo previene che un comando git
arbitrario venga eseguito da testo generato dal modello.

## Regole di scrittura nel vault

- `path` per `write_doc`/`update_devlog` viene sempre risolto contro la cartella del progetto
  **corrente**, mai contro la root del vault: un tentativo di uscire dal progetto (es.
  `../../.obsidian/workspace.json`) viene rifiutato esplicitamente. Stessa protezione per i path
  relativi di `read_file`/`search_code`, ma contro il `repo_path` invece che il `vault_path`.
- Ogni scrittura riuscita genera un commit + push automatico nel repo del vault, mirato ai soli
  file toccati (mai `git add -A`), con autore `Documentation Agent <agent@local>`. `init_project`
  fa un solo commit per tutti i file dello scaffold; `write_doc`/`update_devlog` un commit per
  singola scrittura, messaggio `docs: aggiorna <path>`. Se il push fallisce (es. rete assente), i
  file restano comunque scritti e committati in locale: nessun dato viene perso, il push va
  ripetuto al giro successivo.
- `devlog.md` è append-only per design: non esiste un parametro che permetta di sovrascriverlo.
- `switch_project` è l'unica eccezione: scrive `.current_project` senza passare da un commit
  (è stato locale, non contenuto documentale).
