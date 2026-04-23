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

## 🔮 Future Improvements

- vector DB (FAISS / Chroma)  
- real SCADA integration  
- anomaly detection  
- cloud deployment  

---

## 👨‍💻 Author

Ahmed Tantawy  
Data Engineer | Avionics | SCADA Systems