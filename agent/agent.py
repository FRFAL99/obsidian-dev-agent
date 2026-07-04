from agent.prompt_builder import PromptBuilder
from agent.llm import chat
class Agent:
    def __init__(self): self.builder=PromptBuilder()
    def ask(self,msg,history=None):
        return chat(self.builder.build(msg,history or []))
