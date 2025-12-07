# agent.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
import tiktoken
from tools import tools

class ChatAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-5-nano",
            api_key=api_key,
            temperature=0.7,
            reasoning_effort="low"  # diminui o tempo de esforço de pensamento para respostas mais rapidas (minimal, low)
        )
        self.agent = create_agent(
            tools=tools,                # ferramentas/agentes
            model=self.llm,             # modelo do gpt
        )

    def enviar_mensagem(self, lista_msg, msg_usuario):
        # Transforma a lista de mensagens (dicts) em um unico dict
        # Nomes em ingles por definicao do Langgraph (checar no docs se customizavel)
        dict_msg = {
            "messages": [
                {"role": "user" if msg["papel"].upper() == "USUARIO" else "assistant", "content": msg["mensagem"]}
                for msg in lista_msg
            ]
        }

        # Adiciona a mensagem do usuario no dict
        dict_msg["messages"].append({"role": "user", "content": msg_usuario})
        
        # Envia para o agente
        response = self.agent.invoke(dict_msg)



        # Extrai a ultima mensagem da conversa (resposta do modelo)
        mensagens_conversa = response.get("messages", [])
        ult_assistant_msg = next(
            (m for m in reversed(mensagens_conversa) if isinstance(m, AIMessage)), 
            None
        )

        return ult_assistant_msg.content
    
    def contar_tokens(self, msg):
        encoding_modelo = tiktoken.encoding_for_model("gpt-5-nano")
        tokens = encoding_modelo.encode(msg)
        return len(tokens)
    
    def verificar_num_tokens(self, msg):
        return self.contar_tokens(msg) <= self.max_token_msg


# Cria a instancia
import os
Agent = ChatAgent(api_key=os.getenv("INFORBOT_MODEL_SECRET_KEY"))