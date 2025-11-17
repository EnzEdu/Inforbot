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
            temperature=0.7
        )
        self.agent = create_agent(
            tools=tools,            # your decorated functions
            model=self.llm,              # ChatOpenAI model
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
        


        # Se alguma ferramenta foi chamada pelo modelo
        if response.get("tool_calls"):
            for chamada in response["tool_calls"]:
                tool_nome = chamada["name"]
                tool_args = chamada["args"]

                # Executa cada ferramenta chamada
                tool = next(t for t in tools if t.name == tool_nome)
                tool_result = tool.run(tool_args)

                # Adiciona o resultado de cada ferramenta
                dict_msg["messages"].append({"role": "tool", "content": tool_result})

            # Recebe a resposta apos incluir os dados das pesquisas
            response_final = self.agent.invoke(dict_msg)
            response = response_final



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