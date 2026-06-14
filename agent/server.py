import gradio as gr
from agent.llm import chat

SYSTEM_PROMPT = (
    "Sei Obsidian Dev Agent. "
    "Aiuti a documentare progetti e puoi usare il vault come memoria."
)

def answer(message, history):
    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    for user, assistant in history:
        messages.append({"role":"user","content":user})
        if assistant:
            messages.append({"role":"assistant","content":assistant})

    messages.append({"role":"user","content":message})
    return chat(messages)

if __name__ == "__main__":
    gr.ChatInterface(
        fn=answer,
        title="Obsidian Dev Agent",
        description="Chat locale collegata a llama.cpp"
    ).launch(server_name="0.0.0.0", server_port=7860)
