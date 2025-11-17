# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import tiktoken

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
    
    def contar_tokens(self, msg):
        encoding_modelo = tiktoken.encoding_for_model("gpt-5-nano")
        tokens = encoding_modelo.encode(msg)
        return len(tokens)
    
    def verificar_num_tokens(self, msg):
        return self.contar_tokens(msg) <= self.max_token_msg


# Cria a instancia
import os
Agent = ChatAgent(api_key=os.getenv("INFORBOT_MODEL_SECRET_KEY"))