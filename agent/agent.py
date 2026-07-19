import json
import logging

from agent.prompt_builder import PromptBuilder
from agent.llm import chat
from agent.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.builder = PromptBuilder()
        self.registry = ToolRegistry()
        self.registry.load()

    def ask(self, msg, history=None, max_iterations=5):
        messages = self.builder.build(msg, history or [])
        tools_schema = self.registry.openai_schemas()

        for _ in range(max_iterations):
            message = chat(messages, tools=tools_schema)
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                **({"tool_calls": message.tool_calls} if message.tool_calls else {}),
            })

            if not message.tool_calls:
                return message.content

            for call in message.tool_calls:
                tool = self.registry.tools.get(call.function.name)
                if tool is None:
                    result = f"Errore: tool '{call.function.name}' non trovato"
                else:
                    try:
                        args = json.loads(call.function.arguments)
                        result = tool.execute(**args)
                    except Exception as e:
                        logger.warning(f"Esecuzione tool '{call.function.name}' fallita: {e}")
                        result = f"Errore esecuzione tool: {e}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result if isinstance(result, str) else json.dumps(result, default=str),
                })

        return "Limite iterazioni raggiunto senza risposta finale."
