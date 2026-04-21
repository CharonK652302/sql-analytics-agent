# 🔍 SQL Analytics Agent

Ask questions about Indian E-commerce data in plain English.
Get back SQL, results, charts, and explanations — instantly.

> Built to be better than typical Text-to-SQL implementations.

---

## 🚀 Live Demo
🌐 [Try it on Streamlit Cloud](https://sql-analytics-agent-zuc2vqbzfo8b64jq5ulpjs.streamlit.app/)

---

## ⚡ What Makes This Different

| Feature | Typical Text-to-SQL | This Project |
|---|---|---|
| Schema retrieval | Full schema in prompt | ✅ FAISS RAG — only relevant tables |
| LLM | OpenAI (paid) | ✅ Groq (free, 10x faster) |
| Results | Raw table | ✅ Auto Plotly charts |
| Explanation | None | ✅ Plain English after every query |
| SQL quality | No check | ✅ Evaluation score /100 |
| Observability | None | ✅ MLflow query tracking + Analytics Dashboard |
| Database | Single | ✅ SQLite + PostgreSQL toggle |
| API | None | ✅ FastAPI REST API (6 endpoints) |
| Export | None | ✅ CSV download |
| History | None | ✅ Last 10 queries with re-run |

---

## 🏗️ Architecture

```
User Question
↓
FAISS Schema Retrieval (semantic search — top 3 relevant tables)
↓
Semantic Layer (business descriptions injected into prompt)
↓
Few-shot Examples (in-context learning)
↓
Groq LLM (llama-3.1-8b-instant, temperature=0)
↓
Safety Guard (blocks INSERT/UPDATE/DELETE/DROP)
↓
SQL Execution (SQLite / PostgreSQL)
↓
Results + Auto Chart + Explanation + Evaluation Score
↓
Query Logged to query_log.db + MLflow experiment tracking
```

---

## 📈 MLflow Query Tracking

Every query is automatically tracked with MLflow:

```bash
mlflow ui   # → http://localhost:5000
```

| Metric tracked | Description |
|---|---|
| `latency_ms` | Query execution time |
| `row_count` | Number of rows returned |
| `success` | 1 = success, 0 = failed |
| `tables_used` | Which tables were retrieved |
| `question` | Natural language input |

Experiment name: `sql-analytics-agent`

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/query` | Natural language → SQL → results |
| GET | `/schema` | All table descriptions |
| GET | `/schema/{table}` | Single table schema |
| GET | `/stats` | Query statistics |

---

## 📊 Database

Synthetic Indian E-commerce dataset:

| Table | Records | Description |
|---|---|---|
| customers | 2,000 | Indian customers across 18 cities |
| products | 500 | 10 categories, Indian brands |
| sellers | 200 | Sellers across India |
| orders | 10,000 | Purchase transactions |
| deliveries | ~7,000 | Delivery performance data |
| reviews | ~3,000 | Customer ratings |

---

## 🚀 Run Locally

```bash
git clone https://github.com/CharonK652302/sql-analytics-agent.git
cd sql-analytics-agent
pip install -r requirements.txt
python database/create_db.py
python -m agent.schema_retriever
python -m uvicorn api.main:app --reload --port 8000
python -m streamlit run app.py
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq API (llama-3.1-8b-instant) |
| Schema Retrieval | FAISS + Sentence-Transformers |
| Semantic Layer | Custom business descriptions |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Charts | Plotly |
| Database | SQLite / PostgreSQL |
| Query Logging | SQLite (query_log.db) + MLflow |
| Experiment Tracking | MLflow (latency, success, row count) |
| Containerization | Docker |

---

## 📸 Screenshots

<img width="1920" height="1080" alt="fastapi" src="https://github.com/user-attachments/assets/b2641ff5-6727-4b1a-b0d5-694b05dd8e1c" />
<img width="1920" height="1080" alt="Screenshot (921)" src="https://github.com/user-attachments/assets/09b3f768-baf2-431e-8902-fe1dea73fa29" />

---

## 👨‍💻 Author

**Sai Charan Goud K**
AI/ML Engineer | RAG · FAISS · FastAPI · LangChain · Groq · MLflow
[GitHub](https://github.com/CharonK652302) ·
[LinkedIn](https://www.linkedin.com/in/sai-charan-goud-kowlampet-007654284/)
