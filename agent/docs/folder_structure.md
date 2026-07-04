# Project Folder Structure Documentation

## 📁 Root Directory
```
obsidian-dev-agent/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # Core agent logic
│   ├── config.py         # Configuration settings
│   ├── llm.py            # LLM integration
│   ├── tools/            # Tool implementations
│   │   ├── base_tool.py  # Base class for tools
│   │   ├── read_file.py  # File reading utility
│   │   ├── search_code.py# Code search tool
│   │   └── update_devlog.py# Dev log updater
│   ├── vault/            # Documentation storage
│   │   └── vault_manager.py# Vault management
├── agent/docs/           # Documentation files
│   ├── documentation_engine.md
│   └── agent_usage.md
├── README.md
├── requirements.txt
└── .env.example
```

## 📌 Key Directories

1. **`agent/`** - Core agent components
   - `agent.py`: Main agent implementation
   - `config.py`: Configuration management
   - `llm.py`: LLM integration layer

2. **`agent/tools/`** - Functional tools
   - `read_file.py`: File content retrieval
   - `search_code.py`: Codebase search capabilities
   - `update_devlog.py`: Development log management
   - `git_tool.py`: Version control integration

3. **`agent/vault/`** - Documentation storage
   - `vault_manager.py`: Documentation organization and retrieval

4. **`agent/docs/`** - Documentation resources
   - `documentation_engine.md`: Engine documentation
   - `agent_usage.md`: Usage guidelines

This structure enables modular development while maintaining clear separation between core logic, tools, and documentation.