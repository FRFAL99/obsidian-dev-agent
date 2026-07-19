from pathlib import Path
from agent.config import VAULT_PATH
from agent.project_manager import ProjectManager
class PromptBuilder:
 FILES=['README.md','architettura.md','ai/context.md','ai/rules.md','ai/memory.md']
 def build(self,msg,h):
  m=[{'role':'system','content':'Sei Obsidian Dev Agent.'}]
  global_rules=Path(VAULT_PATH)/'ai'/'global_rules.md'
  if global_rules.exists():
   m.append({'role':'system','content':global_rules.read_text()})
  cfg=ProjectManager().current_config();
  if cfg:
   vp=Path(cfg['vault_path']);ctx=[]
   [ctx.append((vp/f).read_text()) for f in self.FILES if (vp/f).exists()]
   if ctx: m.append({'role':'system','content':'\n\n'.join(ctx)})
  [m.extend([{'role':'user','content':u},{'role':'assistant','content':a}]) for u,a in h if a is not None]
  m.append({'role':'user','content':msg});return m
