from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

ddg = DuckDuckGoSearchRun()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

@tool("Pesquisa_DuckDuckGo", description="Util para buscar informações na internet.")
def pesquisa_ddg(query: str):
    return ddg.run(query)

@tool("Pesquisa_Wikipedia", description="Util para pesquisas historicas ou detalhadas sobre algum tema.")
def pesquisa_wikipedia(query: str):
    return wikipedia.run(query)

tools = [pesquisa_ddg, pesquisa_wikipedia]