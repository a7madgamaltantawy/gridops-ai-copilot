# Architecture

## Objective
Build an AI copilot for grid operations that can explain incidents using both structured and unstructured data.

## Data sources
- Telemetry
- Alarm / event logs
- Incident history
- Procedures / manuals

## Core pipeline
1. Retrieve telemetry around incident time
2. Retrieve related events
3. Retrieve historical incidents
4. Retrieve relevant documents
5. Build LLM prompt
6. Generate explanation with evidence

## Key value
This project does not replace EMS analytical tools such as state estimation or contingency analysis.
Instead, it adds an operational reasoning and knowledge layer on top of them.




## 🧭 Architecture Diagram

```mermaid
flowchart TD
    A[User asks free-text question in Streamlit UI] --> B[Intent Detection]
    B --> C[Retrieval Layer]

    C --> C1[Telemetry Window]
    C --> C2[Event Timeline]
    C --> C3[Similar Incidents]
    C --> C4[Relevant Documents]

    C1 --> D[Reasoning Layer]
    C2 --> D
    C3 --> D
    C4 --> D

    D --> D1[Telemetry Analysis]
    D --> D2[Event Analysis]
    D --> D3[Incident History Analysis]
    D --> D4[Document Analysis]

    D1 --> E[Structured Incident Assessment]
    D2 --> E
    D3 --> E
    D4 --> E

    E --> F[RAG Context Builder]
    F --> G[LLM Prompt Builder]
    G --> H[LLM or Fallback Answer Generator]
    H --> I[Streamlit UI Response]

    J[(SQLite Database)] --> C