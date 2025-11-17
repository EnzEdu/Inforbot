# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict

class ChatAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-5-nano",
            api_key=api_key,
            temperature=0
        )

    def enviar_mensagem(self, lista_msg):
        mensagens = []
        for msg in lista_msg:
            if (msg["papel"] == "USUARIO"):
                mensagens.append(HumanMessage(content=msg["mensagem"]))
            else:
                mensagens.append(AIMessage(content=msg["mensagem"]))
        
        response = self.llm.invoke(mensagens)
        return response.content


# Cria a instancia
import os
Agent = ChatAgent(os.getenv("INFORBOT_MODEL_SECRET_KEY"))
