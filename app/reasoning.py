from statistics import mean


def safe_mean(values):
    return mean(values) if values else None


def analyze_telemetry(telemetry_rows):
    """
    Turn telemetry rows into structured findings.
    """
    if not telemetry_rows:
        return {
            "summary": "No telemetry data found.",
            "findings": [],
            "metrics": {},
        }

    currents = [row["current"] for row in telemetry_rows if row["current"] is not None]
    voltages = [row["voltage"] for row in telemetry_rows if row["voltage"] is not None]
    temperatures = [row["temperature"] for row in telemetry_rows if row["temperature"] is not None]

    findings = []
    metrics = {}

    avg_current = safe_mean(currents)
    max_current = max(currents) if currents else None
    min_voltage = min(voltages) if voltages else None
    max_temp = max(temperatures) if temperatures else None

    metrics["avg_current"] = round(avg_current, 2) if avg_current is not None else None
    metrics["max_current"] = round(max_current, 2) if max_current is not None else None
    metrics["min_voltage"] = round(min_voltage, 2) if min_voltage is not None else None
    metrics["max_temperature"] = round(max_temp, 2) if max_temp is not None else None

    if max_current is not None and avg_current is not None and max_current > avg_current * 1.25:
        findings.append("Current increased significantly above the local average before the trip.")

    if max_current is not None and max_current >= 150:
        findings.append("Peak current crossed a high-load threshold, consistent with overload conditions.")

    if min_voltage is not None and min_voltage < 10.5:
        findings.append("Voltage dropped below expected operating range before the incident.")

    if max_temp is not None and max_temp > 45:
        findings.append("Temperature rose during the same period, which may indicate thermal stress.")

    breaker_states = [row["breaker_status"] for row in telemetry_rows if row["breaker_status"]]
    if "OPEN" in breaker_states:
        findings.append("Breaker status changed to OPEN after the disturbance window.")

    if not findings:
        findings.append("Telemetry did not show a strong abnormal pattern in the selected time window.")

    summary = "Telemetry suggests abnormal loading and pre-trip degradation." if len(findings) >= 2 else "Telemetry evidence is limited."

    return {
        "summary": summary,
        "findings": findings,
        "metrics": metrics,
    }


def analyze_events(event_rows):
    """
    Turn event rows into a timeline-based interpretation.
    """
    if not event_rows:
        return {
            "summary": "No event data found.",
            "findings": [],
            "timeline": [],
        }

    findings = []
    timeline = []

    event_types = []

    for row in event_rows:
        timeline.append({
            "event_time": row["event_time"],
            "event_type": row["event_type"],
            "severity": row["severity"],
            "message": row["message"],
        })
        event_types.append(row["event_type"])

    if "overcurrent_alarm" in event_types:
        findings.append("Overcurrent alarm occurred before the trip.")

    if "undervoltage_alarm" in event_types:
        findings.append("Undervoltage alarm occurred before breaker operation.")

    if "relay_pickup" in event_types:
        findings.append("Relay pickup indicates the protection system detected an abnormal condition.")

    if "breaker_trip" in event_types:
        findings.append("Breaker trip confirms the disturbance resulted in feeder disconnection.")

    if (
        "overcurrent_alarm" in event_types
        and "undervoltage_alarm" in event_types
        and "breaker_trip" in event_types
    ):
        findings.append("The event sequence is consistent with overload progression followed by protection trip.")

    summary = "Event timeline supports a protection-driven feeder trip." if findings else "Event evidence is limited."

    return {
        "summary": summary,
        "findings": findings,
        "timeline": timeline,
    }


def analyze_incident_history(incident_rows):
    """
    Extract useful patterns from past incidents.
    """
    if not incident_rows:
        return {
            "summary": "No similar incidents found.",
            "findings": [],
            "similar_cases": [],
        }

    findings = []
    similar_cases = []

    overload_count = 0
    thermal_count = 0

    for row in incident_rows:
        root_cause = row["root_cause"]
        similar_cases.append({
            "incident_id": row["incident_id"],
            "start_time": row["start_time"],
            "root_cause": root_cause,
            "resolution": row["resolution"],
        })

        text = root_cause.lower()
        if "overload" in text:
            overload_count += 1
        if "heat" in text or "thermal" in text or "overheating" in text:
            thermal_count += 1

    if overload_count > 0:
        findings.append(f"{overload_count} past incident(s) on this feeder involved overload-related causes.")

    if thermal_count > 0:
        findings.append(f"{thermal_count} past incident(s) mentioned thermal or overheating behavior.")

    if not findings:
        findings.append("Past incidents exist, but no strong repeated pattern was detected yet.")

    summary = "Incident history suggests repeat behavior on the same feeder." if overload_count or thermal_count else "Incident history provides weak similarity."

    return {
        "summary": summary,
        "findings": findings,
        "similar_cases": similar_cases,
    }


def analyze_documents(document_rows):
    """
    Summarize the operational guidance found in documents.
    """
    if not document_rows:
        return {
            "summary": "No relevant documents found.",
            "findings": [],
            "references": [],
        }

    findings = []
    references = []

    for row in document_rows:
        references.append({
            "doc_id": row["doc_id"],
            "title": row["title"],
            "doc_type": row["doc_type"],
        })

        text = row["content"].lower()
        if "overcurrent" in text or "overload" in text:
            findings.append(f"{row['title']} contains overload-related troubleshooting guidance.")
        if "breaker" in text and "trip" in text:
            findings.append(f"{row['title']} contains breaker-trip investigation guidance.")
        if "relay" in text:
            findings.append(f"{row['title']} mentions relay-event interpretation.")

    # deduplicate while preserving order
    findings = list(dict.fromkeys(findings))

    summary = "Relevant procedures and knowledge notes were found." if findings else "Documents were retrieved but yielded limited guidance."

    return {
        "summary": summary,
        "findings": findings,
        "references": references,
    }


def build_structured_incident_assessment(telemetry_analysis, event_analysis, history_analysis, document_analysis):
    """
    Combine all partial analyses into a single structured assessment.
    """
    evidence = []
    evidence.extend(telemetry_analysis["findings"])
    evidence.extend(event_analysis["findings"])
    evidence.extend(history_analysis["findings"])
    evidence.extend(document_analysis["findings"])

    likely_cause = "Likely feeder overload leading to protection trip"
    confidence = "medium"

    telemetry_text = " ".join(telemetry_analysis["findings"]).lower()
    events_text = " ".join(event_analysis["findings"]).lower()
    history_text = " ".join(history_analysis["findings"]).lower()

    if "overload" in telemetry_text and "protection" in events_text:
        confidence = "high"

    if "thermal" in history_text and confidence == "high":
        likely_cause = "Likely recurring overload / thermal stress leading to protection trip"

    recommended_actions = [
        "Review the alarm and breaker event sequence around the incident.",
        "Inspect the affected feeder section for overload or thermal stress indicators.",
        "Compare current and voltage behavior with previous similar incidents.",
        "Consult the breaker-trip and feeder-overload procedures before restoration.",
    ]

    return {
        "likely_cause": likely_cause,
        "confidence": confidence,
        "evidence": evidence,
        "recommended_actions": recommended_actions,
    }