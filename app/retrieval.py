from datetime import datetime, timedelta

from app.db import get_connection


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def get_telemetry_window(feeder_id: str, incident_time: str, minutes_before: int = 15, minutes_after: int = 5):
    """
    Retrieve telemetry around the incident time window.
    """
    incident_dt = parse_iso(incident_time)
    start_dt = incident_dt - timedelta(minutes=minutes_before)
    end_dt = incident_dt + timedelta(minutes=minutes_after)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM telemetry
        WHERE feeder_id = ?
          AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp ASC
    """, (feeder_id, start_dt.isoformat(), end_dt.isoformat()))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_event_timeline(feeder_id: str, incident_time: str, minutes_before: int = 20, minutes_after: int = 5):
    """
    Retrieve event timeline around the incident.
    """
    incident_dt = parse_iso(incident_time)
    start_dt = incident_dt - timedelta(minutes=minutes_before)
    end_dt = incident_dt + timedelta(minutes=minutes_after)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM events
        WHERE feeder_id = ?
          AND event_time BETWEEN ? AND ?
        ORDER BY event_time ASC
    """, (feeder_id, start_dt.isoformat(), end_dt.isoformat()))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_similar_incidents(feeder_id: str, limit: int = 5):
    """
    Start simple: retrieve incidents from the same feeder, newest first.
    Later we can improve this with keyword or embedding similarity.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM incidents
        WHERE feeder_id = ?
        ORDER BY start_time DESC
        LIMIT ?
    """, (feeder_id, limit))

    rows = cur.fetchall()
    conn.close()
    return rows


def get_relevant_documents(keywords=None, limit: int = 5):
    """
    Simple keyword-based document retrieval.
    Later we can replace this with embeddings / vector search.
    """
    keywords = keywords or []

    conn = get_connection()
    cur = conn.cursor()

    if not keywords:
        cur.execute("""
            SELECT *
            FROM documents
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows

    clauses = []
    params = []

    for kw in keywords:
        clauses.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)")
        like_kw = f"%{kw.lower()}%"
        params.extend([like_kw, like_kw])

    sql = f"""
        SELECT *
        FROM documents
        WHERE {' OR '.join(clauses)}
        LIMIT ?
    """
    params.append(limit)

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_latest_breaker_trip(feeder_id: str):
    """
    Useful helper to identify the main incident anchor time automatically.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM events
        WHERE feeder_id = ?
          AND event_type = 'breaker_trip'
        ORDER BY event_time DESC
        LIMIT 1
    """, (feeder_id,))

    row = cur.fetchone()
    conn.close()
    return row