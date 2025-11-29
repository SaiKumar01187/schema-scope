

# 📘 **README.md — SchemaScope (Full Version)**

*(Includes banner, badges, installation guide, architecture diagram, screenshots, lineage explanation, and more)*

---

# 🧠 SchemaScope – Data Contract & Schema Assistant
<p align="center">
<img width="500" height="250" alt="banner" src="https://github.com/user-attachments/assets/774c37bd-1997-4bf8-a512-a3add4667edf" />


<p align="center">

  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-WebApp-red?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-LLM-%23ff5a5f?logo=lightning&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS-VectorDB-green" />
  <img src="https://img.shields.io/badge/HuggingFace-Embeddings-yellow?logo=huggingface&logoColor=black" />
  <img src="https://img.shields.io/badge/SQL-Lineage-orange?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen" />

</p>

---

## 🚀 Overview

**SchemaScope** is an AI-powered assistant that helps you understand your **database schemas**, **PII fields**, **upstream/downstream lineage**, and **auto-generate data contracts** — all through a chat-based interface.

It uses:

* **Groq Llama 3.3** for ultra-fast schema Q&A
* **FAISS** + **HuggingFace** embeddings for RAG
* **SQL parsing** + **LLM reasoning** for lineage detection
* **Streamlit UI** for an interactive browser experience

---

## 🎯 Key Features

### 🔍 **1. Chat with your Schemas**

Ask questions like:

* *"Which fields are PII in customers?"*
* *"What breaks if I remove the email column?"*
* *"What are upstream tables for high_value_customers?"*

### 📄 **2. Auto-Generate Data Contracts (YAML)**

SchemaScope generates production-ready YAML files including:

* Field types
* Required flags
* PII classification
* Upstream / downstream relationships

### 🔗 **3. SQL Lineage Extraction**

Place all your SQL models in `/sql/` and the app will produce:

* A full lineage graph
* Upstream and downstream mapping
* Table dependencies

### 🧠 **4. Built on AI-first Architecture**

* Groq Llama 3.3
* FAISS vector search
* HuggingFace MiniLM embeddings
* Custom SQL lineage parser

---

## 🖼️ Screenshots

### **Schema Chat Interface**
<img width="500" height="250" alt="image" src="https://github.com/user-attachments/assets/dcd200ec-0a7d-4c0b-abff-0fafbb7f7dc9" />

### **Lineage Graph**
<img width="500" height="250" alt="image" src="https://github.com/user-attachments/assets/606723c7-56ad-45b6-8138-c3f009baffdc" />


---

## 📂 Project Structure

```
schema-scope/
│
├── data/
│   └── schemas/
│       ├── sample_schema.yml
│       └── sql_lineage.yml
│
├── sql/
│   └── views.sql
│
├── src/
│   ├── config.py
│   ├── ui_app.py
│   ├── schema_models.py
│   ├── yaml_loader.py
│   ├── lineage_graph.py
│   ├── sql_lineage_llm.py
│   └── sql_lineage_to_yaml.py
│
├── images/
│   └── banner.png      <- place banner here
│
├── requirements.txt
├── lineage.html
└── README.md
```

---

## ⚙️ Installation

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/schema-scope.git
cd schema-scope
```

### **2️⃣ Create Virtual Environment**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### **3️⃣ Install Requirements**

```bash
pip install -r requirements.txt
```

### **4️⃣ Add Groq API Key**

Create `.env` file:

```
GROQ_API_KEY=your_key_here
```

### **5️⃣ Run Application**

```bash
streamlit run src/ui_app.py
```

---

## 🧠 How SchemaScope Works (Architecture)

```
YAML Schemas →─────────────→ FAISS Vector DB →────────────→ LLM (Groq)
SQL Files     → SQL Parser → Lineage Engine   → Lineage Graph (HTML)
```

### **RAG Pipeline**

1. Load schema YAML files
2. Convert them into chunked documents
3. Embed using MiniLM
4. Store in FAISS
5. Query using LLM

### **Lineage Engine**

1. Reads `/sql/*.sql`
2. Detects SELECT → FROM → JOIN dependencies
3. Builds directed graph
4. Exports `lineage.html`

---

## 🗂️ Add Your Own SQL for Real Lineage

Place your warehouse SQL:

```
schema-scope/sql/
    staging_customers.sql
    fact_orders.sql
    dims/dim_customer.sql
```

Then run:

```bash
python -m src.sql_lineage_to_yaml
python -m src.lineage_graph
```

This generates the lineage YAML + graph automatically.

---

## 📄 Example Data Contract Output

```yaml
entities:
  - name: customers
    entity_type: table
    upstream: [stg_customers]
    downstream: [customer_created_event]
    fields:
      - name: id
        type: integer
        required: true
      - name: email
        type: string
        pii: true
      - name: address
        type: string
        pii: true
```

---

## 💻 Tech Stack

| Component          | Technology           |
| ------------------ | -------------------- |
| UI                 | Streamlit            |
| LLM                | Groq Llama 3.3       |
| Embeddings         | HuggingFace MiniLM   |
| Vector DB          | FAISS                |
| SQL Lineage Engine | Custom Python parser |
| Packaging          | Python 3.10          |

---

## 🤝 Contributing

PRs welcome!
If you'd like to contribute:

1. Fork
2. Create a branch
3. Submit PR

---

## 📧 Contact

**Sai Kumar**
🔗 LinkedIn: *[your link here](https://www.linkedin.com/in/saip01/)*
📬 Email: *saikumarp919@gmail.com*

---

## 📝 License

MIT License.

---



