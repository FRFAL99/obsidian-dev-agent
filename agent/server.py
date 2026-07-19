import gradio as gr

from agent.agent import Agent

agent = Agent()


def answer(message, history):
    return agent.ask(message, history)


if __name__ == "__main__":
    gr.ChatInterface(
        fn=answer,
        title="Obsidian Dev Agent",
        description="Chat locale collegata a llama.cpp, con accesso in scrittura al vault Obsidian"
    ).launch(server_name="0.0.0.0", server_port=7860)
