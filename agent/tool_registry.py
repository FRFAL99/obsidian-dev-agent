from importlib import import_module
from pathlib import Path
from typing import Dict, Type

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
            mod = import_module(f'agent.tools.{f.stem}')
            [self.tools.setdefault(c().name, c()) for c in mod.__dict__.values() if isinstance(c, type) and hasattr(c, 'name') and c.__name__ != 'BaseTool']