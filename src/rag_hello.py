from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config import GROQ_API_KEY
from src.yaml_loader import load_yaml_entities


def build_demo_rag_chain():
    # 1. Load SchemaEntity objects from YAML
    entities = load_yaml_entities("data/schemas")

    # 2. Convert them to LangChain Documents
    docs = []
    for e in entities:
        text = e.raw_text or e.to_document_text()
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "name": e.name,
                    "entity_type": e.entity_type,
                },
            )
        )

    # 3. Free local embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 4. Build FAISS vector store + retriever
    vectordb = FAISS.from_documents(docs, embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    # 5. LLM – Groq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # or "llama-3.1-8b-instant"
        api_key=GROQ_API_KEY,
        temperature=0.1,
    )

    # 6. Prompt template
    prompt = ChatPromptTemplate.from_template(
        """
You are a schema lineage assistant.

You answer questions about:
- data contracts
- schema fields
- PII classification
- upstream/downstream lineage
- impact analysis (e.g., adding/removing fields)
- event/table dependencies

Use STRICTLY the provided context. If the answer is not found, say:
"I cannot find that information in the schema."


Context:
{context}

Question: {question}
"""
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def main():
    rag_chain = build_demo_rag_chain()

    question = "If I add a new field credit_score to the customers table, which downstream systems will be impacted?"
    answer = rag_chain.invoke(question)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)


if __name__ == "__main__":
    main()
