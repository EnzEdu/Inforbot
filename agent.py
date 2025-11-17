# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

class ChatAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-5-nano",
            api_key=api_key,
            temperature=0
        )

    def enviar_mensagem(self, user_msg: str):
        messages = [
            HumanMessage(content=user_msg)
        ]
        
        response = self.llm.invoke(messages)
        return response.content


# Cria a instancia
import os
Agent = ChatAgent(os.getenv("INFORBOT_MODEL_SECRET_KEY"))
