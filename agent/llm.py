from openai import OpenAI
from agent.config import LLM_BASE_URL, LLM_MODEL

client = OpenAI(base_url=LLM_BASE_URL, api_key="dummy")

def chat(messages, tools=None, temperature=0.3):
    """Ritorna l'intero oggetto message (non solo .content) così il chiamante
    può ispezionare eventuali tool_calls e re-iniettarlo nella history."""
    kwargs = {"model": LLM_MODEL, "messages": messages, "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message
