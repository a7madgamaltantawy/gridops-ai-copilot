import streamlit as st

from app.retrieval import (
    get_latest_breaker_trip,
    get_telemetry_window,
    get_event_timeline,
    get_similar_incidents,
    get_relevant_documents,
)
from app.reasoning import (
    analyze_telemetry,
    analyze_events,
    analyze_incident_history,
    analyze_documents,
    build_structured_incident_assessment,
)
from app.rag import (
    build_rag_context,
    build_llm_prompt,
)
from app.llm import generate_answer


def detect_intent(question: str) -> str:
    q = (question or "").strip().lower()

    if not q:
        return "incident_explanation"

    if any(word in q for word in ["why", "cause", "reason", "trip", "outage", "fault"]):
        return "incident_explanation"

    if any(word in q for word in ["evidence", "support", "prove", "show data", "timeline"]):
        return "evidence_summary"

    if any(word in q for word in ["similar", "before", "history", "happened before", "past incident"]):
        return "similar_incidents"

    if any(word in q for word in ["action", "next", "what should", "recommend", "check next"]):
        return "recommended_actions"

    if any(word in q for word in ["procedure", "manual", "document", "guide", "runbook"]):
        return "document_guidance"

    return "incident_explanation"


def build_intent_focused_answer(
    intent: str,
    assessment: dict,
    telemetry_analysis: dict,
    event_analysis: dict,
    history_analysis: dict,
    document_analysis: dict,
) -> str:
    if intent == "evidence_summary":
        lines = ["Evidence summary:"]
        for item in assessment.get("evidence", []):
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Key telemetry metrics:")
        for k, v in telemetry_analysis.get("metrics", {}).items():
            lines.append(f"- {k}: {v}")

        lines.append("")
        lines.append("Event timeline indicators:")
        for item in event_analysis.get("findings", []):
            lines.append(f"- {item}")

        return "\n".join(lines)

    if intent == "similar_incidents":
        lines = ["Similar past incidents:"]
        cases = history_analysis.get("similar_cases", [])
        if not cases:
            lines.append("- No similar incidents found.")
        else:
            for case in cases:
                lines.append(
                    f"- {case['incident_id']} at {case['start_time']}: "
                    f"{case['root_cause']} | resolution: {case['resolution']}"
                )
        return "\n".join(lines)

    if intent == "recommended_actions":
        lines = ["Recommended next operator actions:"]
        for action in assessment.get("recommended_actions", []):
            lines.append(f"- {action}")
        return "\n".join(lines)

    if intent == "document_guidance":
        lines = ["Relevant procedures and knowledge references:"]
        refs = document_analysis.get("references", [])
        if not refs:
            lines.append("- No relevant documents found.")
        else:
            for ref in refs:
                lines.append(f"- {ref['doc_id']}: {ref['title']} ({ref['doc_type']})")
        return "\n".join(lines)

    lines = [
        "Incident summary:",
        f"The most likely cause is: {assessment.get('likely_cause', 'Unknown')}.",
        f"Confidence: {assessment.get('confidence', 'unknown')}.",
        "",
        "Supporting evidence:",
    ]
    for item in assessment.get("evidence", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Recommended actions:")
    for action in assessment.get("recommended_actions", []):
        lines.append(f"- {action}")

    return "\n".join(lines)


def run_copilot(feeder_id: str, question: str) -> dict:
    trip_event = get_latest_breaker_trip(feeder_id)
    if not trip_event:
        return {"error": f"No breaker trip found for feeder {feeder_id}."}

    incident_time = trip_event["event_time"]

    telemetry = get_telemetry_window(feeder_id, incident_time)
    events = get_event_timeline(feeder_id, incident_time)
    incidents = get_similar_incidents(feeder_id)
    docs = get_relevant_documents(["breaker", "overcurrent", "overload", "relay", "procedure"])

    telemetry_analysis = analyze_telemetry(telemetry)
    event_analysis = analyze_events(events)
    history_analysis = analyze_incident_history(incidents)
    document_analysis = analyze_documents(docs)

    assessment = build_structured_incident_assessment(
        telemetry_analysis,
        event_analysis,
        history_analysis,
        document_analysis,
    )

    intent = detect_intent(question)
    intent_answer = build_intent_focused_answer(
        intent=intent,
        assessment=assessment,
        telemetry_analysis=telemetry_analysis,
        event_analysis=event_analysis,
        history_analysis=history_analysis,
        document_analysis=document_analysis,
    )

    rag_context = build_rag_context(
        feeder_id=feeder_id,
        incident_time=incident_time,
        telemetry_analysis=telemetry_analysis,
        event_analysis=event_analysis,
        history_analysis=history_analysis,
        document_analysis=document_analysis,
        assessment=assessment,
    )

    prompt = build_llm_prompt(rag_context, question)

    llm_answer = generate_answer(
        prompt=prompt,
        assessment=assessment,
        history_analysis=history_analysis,
        document_analysis=document_analysis,
    )

    return {
        "feeder_id": feeder_id,
        "incident_time": incident_time,
        "intent": intent,
        "question": question,
        "intent_answer": intent_answer,
        "llm_answer": llm_answer,
        "assessment": assessment,
        "telemetry_analysis": telemetry_analysis,
        "event_analysis": event_analysis,
        "history_analysis": history_analysis,
        "document_analysis": document_analysis,
        "rag_context": rag_context,
    }


def render_app():
    st.set_page_config(
        page_title="GridOps AI Copilot",
        page_icon="⚡",
        layout="wide",
    )

    st.title("⚡ GridOps AI Copilot")
    st.caption(
        "AI copilot for grid / EMS / SCADA-style incident explanation using telemetry, "
        "events, incident history, procedures, structured reasoning, and grounded AI output."
    )

    with st.form("question_form"):
        col1, col2 = st.columns([1, 2])

        with col1:
            feeder_id = st.text_input("Feeder ID", value="F_12")

        with col2:
            question = st.text_area(
                "Ask an operational question",
                value="Why did feeder F-12 trip, what evidence supports it, and what should the operator check next?",
                height=120,
                placeholder="Example: Has something similar happened before on feeder F-12?",
            )

        submitted = st.form_submit_button("Analyze Incident")

    if not submitted:
        st.info("Enter a feeder and ask a free-text question to start the copilot.")
        return

    result = run_copilot(feeder_id.strip(), question.strip())

    if result.get("error"):
        st.error(result["error"])
        return

    top1, top2, top3 = st.columns(3)
    top1.metric("Feeder", result["feeder_id"])
    top2.metric("Incident Time", result["incident_time"])
    top3.metric("Detected Intent", result["intent"])

    st.subheader("Copilot Answer")
    st.write(result["llm_answer"])

    with st.expander("Intent-focused answer", expanded=True):
        st.text(result["intent_answer"])

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Likely Cause")
        st.write(result["assessment"]["likely_cause"])
        st.write(f"**Confidence:** {result['assessment']['confidence']}")

        st.subheader("Telemetry Metrics")
        st.json(result["telemetry_analysis"]["metrics"])

        st.subheader("Recommended Actions")
        for item in result["assessment"]["recommended_actions"]:
            st.write(f"- {item}")

    with c2:
        st.subheader("Evidence")
        for item in result["assessment"]["evidence"]:
            st.write(f"- {item}")

    with st.expander("Event Timeline"):
        for item in result["event_analysis"]["timeline"]:
            st.write(
                f"- {item['event_time']} | {item['event_type']} | "
                f"{item['severity']} | {item['message']}"
            )

    with st.expander("Similar Incidents"):
        cases = result["history_analysis"]["similar_cases"]
        if not cases:
            st.write("No similar incidents found.")
        else:
            for case in cases:
                st.write(
                    f"- {case['incident_id']} | {case['start_time']} | "
                    f"{case['root_cause']} | {case['resolution']}"
                )

    with st.expander("Document References"):
        refs = result["document_analysis"]["references"]
        if not refs:
            st.write("No relevant documents found.")
        else:
            for ref in refs:
                st.write(f"- {ref['doc_id']} | {ref['title']} | {ref['doc_type']}")

    with st.expander("Grounded RAG Context"):
        st.text(result["rag_context"])