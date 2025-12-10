from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List

ddg = DuckDuckGoSearchRun()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

@tool("Pesquisa_DuckDuckGo", description="Util para buscar informações na internet.")
def pesquisa_ddg(query: str):
    return ddg.run(query)

@tool("Pesquisa_Wikipedia", description="Util para pesquisas historicas ou detalhadas sobre algum tema.")
def pesquisa_wikipedia(query: str):
    return wikipedia.run(query)

tools = [pesquisa_ddg, pesquisa_wikipedia]




def load_pdf_docs(pdf_path: str):
    """Carrega páginas do PDF como Document objects do LangChain."""
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()  # lista de Documents, um por página
    return docs


def chunk_documents(docs, chunk_size=1200, chunk_overlap=200):
    """Quebra documentos em chunks com índices para rastreabilidade."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def build_vectorstore(chunks):
    """Gera embeddings e constrói um FAISS local."""
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.from_documents(chunks, embedder)
    return vs


def make_retriever(vs, k=6):
    """Cria um retriever (Top-k) em cima do índice FAISS."""
    return vs.as_retriever(search_kwargs={"k": k})


def format_docs(docs: List) -> str:
    """Concatena chunks em um único contexto com metadados de página/índice."""
    out = []
    for i, d in enumerate(docs, start=1):
        page = d.metadata.get("page", "NA")
        start = d.metadata.get("start_index", "NA")
        out.append(f"[Chunk {i} | page {page} | start {start}]\n{d.page_content}")
    return "\n\n".join(out)


def query_and_summarize(pdf_paths, question):
    # 1. Loading
    documentos = []
    for path in pdf_paths:
        docs = load_pdf_docs(path)

        # Tag de rastreio pra cada fonte
        for d in docs:
            d.metadata["source_pdf"] = path

        documentos.extend(docs)        

    # 2. Chunking
    chunks = chunk_documents(documentos)

    # 3. Embedding + Indexing
    vectorstore = build_vectorstore(chunks)

    # 4. Retrieval
    retriever = make_retriever(vectorstore)
    relevant_chunks = retriever.invoke(question)

    # 5. Generation
    context = format_docs(relevant_chunks)
    return context