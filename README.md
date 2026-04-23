# ⚡ GridOps AI Copilot

AI-powered copilot for grid / SCADA / EMS operations that explains outages using telemetry, events, incident history, and operational procedures.

---

## 🚀 What this project does

GridOps AI Copilot answers real operational questions like:

> Why did feeder F-12 trip, what evidence supports it, and what should the operator check next?

---

## 🧠 Key Features

- Incident explanation from telemetry + events  
- Evidence-based reasoning (no hallucination)  
- Incident history retrieval  
- Procedure-aware (RAG)  
- Free-text AI copilot interface  
- Streamlit UI  

---

## 🏗️ Architecture

1. Data Layer → SQLite (telemetry, events, incidents, documents)  
2. Retrieval Layer → fetch relevant data  
3. Reasoning Layer → structured analysis  
4. RAG Layer → build grounded context  
5. Copilot Layer → UI + AI  

---

## 🔁 End-to-End Flow

1. User asks a question  
2. System detects intent  
3. Retrieves data  
4. Applies reasoning  
5. Builds RAG context  
6. Generates answer  

---

## 📊 Example Scenario

Feeder F-12 outage:
- rising current → overload  
- voltage drop  
- relay pickup  
- breaker trip  

---

## 🖥️ Run the project

### 1. Install dependencies

    pip install -r requirements.txt

### 2. Create database

    python -m scripts.setup_db

### 3. Seed data

    python -m app.seed_data

### 4. Run UI

    streamlit run app/main.py

---

## 📁 Project Structure

    app/
    ├── ui.py
    ├── router.py
    ├── retrieval.py
    ├── reasoning.py
    ├── rag.py
    ├── llm.py
    ├── db.py
    ├── seed_data.py

    scripts/
    └── setup_db.py

    data/
    └── grid.db

---

## 💡 Why this project matters

Traditional EMS tools:
- what happened  
- what will happen  

This copilot:
- why it happened  
- what evidence supports it  
- what to do next  
- has it happened before  

---

## 🧭 System Architecture

The GridOps AI Copilot follows a layered architecture that combines structured data processing, deterministic reasoning, and AI-driven explanation.

---

### 🔹 Architecture Overview

The system is designed in 5 logical layers:

1. **Data Layer**
   - Stores telemetry, events, incidents, and documents
   - Implemented using SQLite

2. **Retrieval Layer**
   - Fetches relevant data based on incident time and feeder
   - Includes:
     - telemetry window extraction
     - event timeline reconstruction
     - similar incident retrieval
     - document lookup

3. **Reasoning Layer**
   - Converts raw data into structured findings
   - Detects:
     - overload patterns
     - voltage drops
     - protection events
     - historical patterns

4. **RAG Layer (Retrieval-Augmented Generation)**
   - Combines all findings into a grounded context
   - Prepares structured prompt for AI model

5. **Copilot Layer (UI + AI)**
   - Accepts free-text user questions
   - Detects intent (why / evidence / actions / history)
   - Generates structured + AI-assisted answers

---

### 🔄 End-to-End Data Flow

```mermaid
flowchart TD
    A[User Question (Streamlit UI)] --> B[Intent Detection]
    B --> C[Retrieval Layer]

    C --> C1[Telemetry Data]
    C --> C2[Event Logs]
    C --> C3[Incident History]
    C --> C4[Documents]

    C1 --> D[Reasoning Layer]
    C2 --> D
    C3 --> D
    C4 --> D

    D --> E[Structured Findings]

    E --> F[RAG Context Builder]
    F --> G[LLM Prompt]

    G --> H[LLM / Fallback Answer]
    H --> I[UI Display]

    J[(SQLite Database)] --> C



## 🔮 Future Improvements

- vector DB (FAISS / Chroma)  
- real SCADA integration  
- anomaly detection  
- cloud deployment  

---

## 👨‍💻 Author

Ahmed Tantawy  
Data Engineer | Avionics | SCADA Systems