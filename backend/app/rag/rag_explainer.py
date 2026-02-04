from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
import os

class RAGExplainer:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma(
            persist_directory="data/vector_store",
            embedding_function=self.embeddings
        )

        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2
        )

        self._load_knowledge()

    def _load_knowledge(self):
        if self.vectorstore._collection.count() > 0:
            return

        loader = TextLoader("data/knowledge/risk_explanations.txt")
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20
        )

        chunks = splitter.split_documents(docs)
        self.vectorstore.add_documents(chunks)

    def explain(self, risk_factors: list[str]) -> str:
        query = "Explain the following risk factors: " + ", ".join(risk_factors)

        docs = self.vectorstore.similarity_search(query, k=3)
        context = "\n".join(d.page_content for d in docs)

        prompt = f"""
You are a fraud risk analyst.

Using the context below, explain the transaction risk clearly and concisely.

Risk factors:
{", ".join(risk_factors)}

Context:
{context}

Write 2–3 short sentences explaining why this transaction is risky.
Avoid theory. Be concrete and user-focused.
"""

        response = self.llm.invoke(prompt)
        return response.content.strip()