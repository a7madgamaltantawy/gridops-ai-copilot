import requests

from app.config import USE_LLM, OLLAMA_URL, OLLAMA_MODEL


def call_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def build_fallback_answer(assessment, history_analysis, document_analysis):
    lines = []
    lines.append("1. Incident summary")
    lines.append(
        f"The feeder incident is most consistent with a protection-driven outage associated with abnormal loading conditions."
    )
    lines.append("")
    lines.append("2. Most likely root cause")
    lines.append(assessment["likely_cause"])
    lines.append("")
    lines.append("3. Supporting evidence")
    for item in assessment.get("evidence", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("4. Similar past incidents")
    similar_cases = history_analysis.get("similar_cases", [])
    if similar_cases:
        for case in similar_cases:
            lines.append(
                f"- {case['incident_id']} at {case['start_time']}: {case['root_cause']}"
            )
    else:
        lines.append("- No similar incidents found.")

    lines.append("")
    lines.append("5. Recommended next operator actions")
    for action in assessment.get("recommended_actions", []):
        lines.append(f"- {action}")

    lines.append("")
    lines.append("6. Confidence level")
    lines.append(assessment["confidence"])

    lines.append("")
    lines.append("Document references:")
    refs = document_analysis.get("references", [])
    if refs:
        for ref in refs:
            lines.append(f"- {ref['doc_id']}: {ref['title']}")
    else:
        lines.append("- No document references available.")

    return "\n".join(lines)


def generate_answer(prompt, assessment, history_analysis, document_analysis):
    if USE_LLM:
        return call_ollama(prompt)

    return build_fallback_answer(assessment, history_analysis, document_analysis)