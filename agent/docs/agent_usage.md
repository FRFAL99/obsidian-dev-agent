# AI Agent Documentation Agent Usage Guide

## 📁 Project Structure Overview
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

## 🛠 Setup Instructions
1. Clone the repository: `git clone https://github.com/FRFAL99/obsidian-dev-agent.git`
2. Install dependencies: `npm install` or `pip install -r requirements.txt`
3. Configure environment variables in `.env.example`

## 📌 Key Components
1. **`agent/`** - Main agent implementation
   - `agent.py`: Core functionality
   - `config.py`: Configuration management
   - `llm.py`: Large Language Model integration

2. **`agent/tools/`** - Available tools
   - `read_file.py`: Retrieve file content
   - `search_code.py`: Search codebase
   - `update_devlog.py`: Manage development logs
   - `git_tool.py`: Version control operations

3. **`agent/vault/`** - Documentation storage
   - `vault_manager.py`: Documentation organization

## 📚 Usage Examples
```bash
# Start development server
npm run dev

# Run tests
npm test

# Generate documentation
npm run docs
```

## 📝 Documentation Resources
- [Documentation Engine](documentation_engine.md)
- [Folder Structure](folder_structure.md)
- [API Reference](agent/docs/api.md)