from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq


class RAGExplainer:
    def __init__(self):
        # DO NOT load heavy models at startup
        self.embeddings = None
        self.vectorstore = None
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        self.loaded = False

    # lazy load heavy components
    def _initialize_rag(self):
        if self.loaded:
            return

        print("Loading RAG components...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma(
            persist_directory="data/vector_store",
            embedding_function=self.embeddings
        )

        self._load_knowledge()

        self.loaded = True
        print("RAG loaded successfully")

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
        # load ONLY when explanation needed
        self._initialize_rag()

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