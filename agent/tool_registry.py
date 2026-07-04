from importlib import import_module
from pathlib import Path
class ToolRegistry:
 def __init__(self): self.tools={}
 def load(self):
  td=Path(__file__).parent/'tools'
  for f in td.glob('*.py'):
   if f.stem in ('base_tool','__init__'): continue
   mod=import_module(f'agent.tools.{f.stem}')
   [self.tools.setdefault(c().name,c()) for c in mod.__dict__.values() if isinstance(c,type) and hasattr(c,'name') and c.__name__!='BaseTool']
