import json
from pathlib import Path
from agent.config import VAULT_PATH
class ProjectManager:
    def __init__(self): self.root=Path(VAULT_PATH)/'projects'; self.cur=Path(VAULT_PATH)/'.current_project'
    def current_config(self):
        if not self.cur.exists(): return None
        n=self.cur.read_text().strip(); return json.loads((self.root/n/'ai'/'project.json').read_text())
