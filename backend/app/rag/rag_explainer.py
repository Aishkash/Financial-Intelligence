from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

import os

class RAGExplainer:
    def __init__(self):
        # 3i embedding
        self.embedding_fn = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # 4i vector store
        self.vectorstore = Chroma(
            persist_directory="data/vector_store",
            embedding_function=self.embedding_fn
        )

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

        # self._load_knowledge()

    # def _load_knowledge(self):
    #     #5i Avoid duplicating ingestion
    #     if self.vectorstore._collection.count() > 0:
    #         return
    #     # 1i load
    #     loader = TextLoader("data/knowledge/risk_explanations.txt")
    #     docs = loader.load()

    #     # 2i chunk
    #     splitter = RecursiveCharacterTextSplitter(
    #         chunk_size=200,
    #         chunk_overlap=20
    #     )
    #     chunks = splitter.split_documents(docs)
    #     # 3i embedding
    #     # 4i vector store
    #     self.vectorstore.add_documents(chunks)

    def explain(self, risk_factors: list[str]) -> str:
        query = "Explain the following risk factors:\n" + ", ".join(risk_factors)
        # 1,2r retrival, Convert user query to vector
        docs = self.vectorstore.similarity_search(query, k=3)

        context = "\n".join([d.page_content for d in docs])

        prompt = f"""
You are a financial risk analyst.
Explain the transaction risk clearly using only the context below.

Context:
{context}

Risk Factors:
{', '.join(risk_factors)}
"""

        response = self.llm.invoke(prompt)
        return response.content