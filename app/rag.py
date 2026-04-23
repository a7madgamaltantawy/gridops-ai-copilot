def format_telemetry_section(telemetry_analysis):
    lines = []
    lines.append("Telemetry Analysis:")
    lines.append(f"Summary: {telemetry_analysis['summary']}")
    lines.append("Metrics:")

    metrics = telemetry_analysis.get("metrics", {})
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")

    lines.append("Findings:")
    for finding in telemetry_analysis.get("findings", []):
        lines.append(f"- {finding}")

    return "\n".join(lines)


def format_event_section(event_analysis):
    lines = []
    lines.append("Event Analysis:")
    lines.append(f"Summary: {event_analysis['summary']}")
    lines.append("Findings:")
    for finding in event_analysis.get("findings", []):
        lines.append(f"- {finding}")

    lines.append("Timeline:")
    for item in event_analysis.get("timeline", []):
        lines.append(
            f"- {item['event_time']} | {item['event_type']} | {item['severity']} | {item['message']}"
        )

    return "\n".join(lines)


def format_history_section(history_analysis):
    lines = []
    lines.append("Incident History Analysis:")
    lines.append(f"Summary: {history_analysis['summary']}")
    lines.append("Findings:")
    for finding in history_analysis.get("findings", []):
        lines.append(f"- {finding}")

    lines.append("Similar Cases:")
    for case in history_analysis.get("similar_cases", []):
        lines.append(
            f"- {case['incident_id']} | {case['start_time']} | root cause: {case['root_cause']} | resolution: {case['resolution']}"
        )

    return "\n".join(lines)


def format_document_section(document_analysis):
    lines = []
    lines.append("Document Analysis:")
    lines.append(f"Summary: {document_analysis['summary']}")
    lines.append("Findings:")
    for finding in document_analysis.get("findings", []):
        lines.append(f"- {finding}")

    lines.append("References:")
    for ref in document_analysis.get("references", []):
        lines.append(
            f"- {ref['doc_id']} | {ref['title']} | type: {ref['doc_type']}"
        )

    return "\n".join(lines)


def format_structured_assessment(assessment):
    lines = []
    lines.append("Structured Incident Assessment:")
    lines.append(f"Likely cause: {assessment['likely_cause']}")
    lines.append(f"Confidence: {assessment['confidence']}")
    lines.append("Evidence:")
    for item in assessment.get("evidence", []):
        lines.append(f"- {item}")

    lines.append("Recommended actions:")
    for action in assessment.get("recommended_actions", []):
        lines.append(f"- {action}")

    return "\n".join(lines)


def build_rag_context(
    feeder_id,
    incident_time,
    telemetry_analysis,
    event_analysis,
    history_analysis,
    document_analysis,
    assessment,
):
    """
    Build one grounded context block for the LLM.
    """

    parts = [
        f"Feeder ID: {feeder_id}",
        f"Incident Time: {incident_time}",
        "",
        format_telemetry_section(telemetry_analysis),
        "",
        format_event_section(event_analysis),
        "",
        format_history_section(history_analysis),
        "",
        format_document_section(document_analysis),
        "",
        format_structured_assessment(assessment),
    ]

    return "\n".join(parts)


def build_user_question(feeder_id, incident_time):
    return (
        f"Explain the outage on feeder {feeder_id} at {incident_time}. "
        f"Identify the most likely root cause, summarize the supporting evidence, "
        f"mention similar past incidents, and recommend the next operator actions."
    )


def build_llm_prompt(rag_context, user_question):
    """
    Final prompt sent to the LLM.
    """

    return f"""
You are an AI copilot for grid and EMS/SCADA-style operations.

Your job is to answer operational incident questions using ONLY the grounded evidence provided below.
Do not invent measurements, incidents, alarms, or procedures that are not in the context.
If evidence is limited, say so clearly.
Be concise but technically clear.

Required answer structure:
1. Incident summary
2. Most likely root cause
3. Supporting evidence
4. Similar past incidents
5. Recommended next operator actions
6. Confidence level

Grounded context:
{rag_context}

User question:
{user_question}
""".strip()