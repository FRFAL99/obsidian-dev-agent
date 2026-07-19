from importlib import import_module
from pathlib import Path
from typing import Dict, Type
import logging

from agent.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Tool caricati ma non esposti all'LLM in chat (uso interno/futuro).
HIDDEN_TOOLS = {'git'}

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Type['BaseTool']] = {}

    def register_tool(self, tool: 'BaseTool'):
        """Register a tool with the registry"""
        self.tools[tool.name] = tool

    def get_registered_tools(self) -> Dict[str, Type['BaseTool']]:
        """Get all registered tools"""
        return self.tools

    def load(self):
        td = Path(__file__).parent / 'tools'
        for f in td.glob('*.py'):
            if f.stem in ('base_tool', '__init__'):
                continue
            try:
                mod = import_module(f'agent.tools.{f.stem}')
            except Exception as e:
                logger.warning(f"Impossibile caricare il tool '{f.stem}': {e}")
                continue
            [self.tools.setdefault(c().name, c()) for c in mod.__dict__.values() if isinstance(c, type) and issubclass(c, BaseTool) and c is not BaseTool]

    def openai_schemas(self):
        """Schemi JSON (formato OpenAI function-calling) dei tool esposti all'LLM in chat."""
        return [t.to_openai_schema() for t in self.tools.values() if t.name not in HIDDEN_TOOLS]