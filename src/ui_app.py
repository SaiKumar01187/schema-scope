import os
import sys

# Ensure project root is on sys.path so `import src.*` works when run via Streamlit
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
import yaml
from pathlib import Path
import streamlit.components.v1 as components

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import GROQ_API_KEY
from src.yaml_loader import load_yaml_entities
from src.schema_models import SchemaEntity


# --------------------------
# Helpers
# --------------------------
def entity_to_contract_yaml(entity: SchemaEntity) -> str:
    """Convert a single SchemaEntity into a YAML data contract string."""
    data = {
        "entities": [
            {
                "name": entity.name,
                "entity_type": entity.entity_type,
                "upstream": entity.upstream,
                "downstream": entity.downstream,
                "fields": [
                    {
                        "name": f.name,
                        "type": f.type,
                        "required": f.required,
                        "pii": f.pii,
                        "description": f.description,
                    }
                    for f in entity.fields
                ],
            }
        ]
    }
    # Keep keys in natural order
    return yaml.safe_dump(data, sort_keys=False)


# --------------------------
# Build RAG pipeline (cached)
# --------------------------
@st.cache_resource
def get_rag_chain_and_entities():
    # 1. Load schema entities from YAML
    entities = load_yaml_entities("data/schemas")

    # 2. Convert to Documents
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

    # 3. Embeddings (free HF model)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 4. Vector store + retriever
    vectordb = FAISS.from_documents(docs, embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    # 5. LLM – Groq
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # or "llama-3.1-8b-instant"
        api_key=GROQ_API_KEY,
        temperature=0.1,
    )

    # 6. Prompt
    prompt = ChatPromptTemplate.from_template(
        """
You are a data schema and data contract assistant.

You can answer questions about:
- tables and events
- required / optional fields
- PII fields
- upstream and downstream lineage
- impact of adding/removing fields

Use ONLY the context below. 
If the answer is not clearly in the context, say "I don't know from the current schema."

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

    return rag_chain, entities


# --------------------------
# Streamlit UI
# --------------------------
def main():
    st.set_page_config(page_title="SchemaScope – Schema Assistant", layout="wide")

    st.title("🧠 SchemaScope – Data Contract & Schema Assistant")

    rag_chain, entities = get_rag_chain_and_entities()

    # ---- Sidebar: Entity browser ----
    st.sidebar.header("📚 Entities")
        # Button to reload YAML schemas and rebuild the RAG stack
    if st.sidebar.button("🔄 Reload schemas"):
        st.cache_resource.clear()
        st.rerun()



    entity_names = [e.name for e in entities]
    selected_name = st.sidebar.selectbox("Select an entity", options=entity_names)

    selected_entity = next(e for e in entities if e.name == selected_name)

    st.sidebar.subheader("Entity details")
    st.sidebar.markdown(f"**Name:** `{selected_entity.name}`")
    st.sidebar.markdown(f"**Type:** `{selected_entity.entity_type}`")
    if selected_entity.upstream:
        st.sidebar.markdown("**Upstream:** " + ", ".join(selected_entity.upstream))
    if selected_entity.downstream:
        st.sidebar.markdown("**Downstream:** " + ", ".join(selected_entity.downstream))

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Fields:**")
    for f in selected_entity.fields:
        flags = []
        if f.required:
            flags.append("required")
        if f.pii:
            flags.append("PII")
        flags_text = f" _({' ,'.join(flags)})_" if flags else ""
        st.sidebar.markdown(f"- `{f.name}` ({f.type}){flags_text}")

    # ---- Data contract generation ----
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Data Contract (YAML)")

    contract_yaml = entity_to_contract_yaml(selected_entity)

    st.sidebar.code(contract_yaml, language="yaml")

    st.sidebar.download_button(
        label="💾 Download contract",
        data=contract_yaml,
        file_name=f"{selected_entity.name}_contract.yml",
        mime="text/yaml",
        use_container_width=True,
    )

    # ---- Main area: Tabs ----
    tab_chat, tab_lineage = st.tabs(["💬 Chat", "🕸 Lineage Graph"])

    # ===== Chat tab =====
    with tab_chat:
        st.subheader("Ask questions about your schemas")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Show previous messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        user_input = st.chat_input(
            "Ask something like: 'Which fields are PII in customers?'"
        )

        if user_input:
            # Show user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate answer
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = rag_chain.invoke(user_input)
                    st.markdown(answer)

            st.session_state.messages.append({"role": "assistant", "content": answer})

    # ===== Lineage Graph tab =====
    with tab_lineage:
        st.subheader("End-to-end lineage")

        lineage_path = Path("lineage.html")
        if lineage_path.exists():
            html = lineage_path.read_text(encoding="utf-8")
            components.html(html, height=700, scrolling=True)
        else:
            st.info(
                "No lineage graph found yet. Run `python -m src.lineage_graph` "
                "from the project root to generate lineage.html."
            )


if __name__ == "__main__":
    main()
