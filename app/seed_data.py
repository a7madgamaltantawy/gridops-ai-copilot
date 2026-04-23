import random
from datetime import datetime, timedelta

from app.db import get_connection


def seed_assets(cur):
    assets = [
        ("SUB_1", "substation", "Primary Substation", "SUB_1", "F_12", None, "Zone A"),
        ("BRK_1", "breaker", "Feeder Breaker F-12", "SUB_1", "F_12", "SUB_1", "Zone A"),
        ("TR_1", "transformer", "Transformer T-1", "SUB_1", "F_12", "BRK_1", "Zone A"),
        ("LINE_1", "line_segment", "Line Segment 1", "SUB_1", "F_12", "TR_1", "Zone A"),
        ("RELAY_1", "relay", "Protection Relay 1", "SUB_1", "F_12", "BRK_1", "Zone A"),
        ("LOAD_1", "load_block", "Industrial Load Block 1", "SUB_1", "F_12", "LINE_1", "Zone A"),
        ("BRK_2", "breaker", "Feeder Breaker F-13", "SUB_1", "F_13", "SUB_1", "Zone B"),
        ("TR_2", "transformer", "Transformer T-2", "SUB_1", "F_13", "BRK_2", "Zone B"),
        ("LINE_2", "line_segment", "Line Segment 2", "SUB_1", "F_13", "TR_2", "Zone B"),
    ]

    cur.executemany("""
        INSERT INTO assets (
            asset_id, asset_type, asset_name, substation_id, feeder_id,
            upstream_asset_id, location
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, assets)


def generate_f12_telemetry():
    rows = []
    base_time = datetime(2026, 4, 1, 13, 30)

    for i in range(60):
        ts = base_time + timedelta(minutes=i)

        voltage = 11.0 + random.uniform(-0.06, 0.06)
        current = 102.0 + random.uniform(-4.0, 4.0)
        temperature = 42.0 + random.uniform(-1.5, 1.5)
        breaker_status = "CLOSED"

        # build overload pattern before trip
        if 31 <= i <= 36:
            ramp = i - 30
            current += ramp * 10
            voltage -= ramp * 0.08
            temperature += ramp * 0.9

        if i >= 37:
            breaker_status = "OPEN"
            current = 0.0
            voltage = 0.0

        rows.append((
            ts.isoformat(),
            "LINE_1",
            "F_12",
            round(voltage, 2),
            round(current, 2),
            round(temperature, 2),
            breaker_status,
        ))

    return rows


def generate_f13_telemetry():
    rows = []
    base_time = datetime(2026, 4, 1, 13, 30)

    for i in range(60):
        ts = base_time + timedelta(minutes=i)

        voltage = 11.0 + random.uniform(-0.05, 0.05)
        current = 88.0 + random.uniform(-3.0, 3.0)
        temperature = 39.0 + random.uniform(-1.0, 1.0)
        breaker_status = "CLOSED"

        rows.append((
            ts.isoformat(),
            "LINE_2",
            "F_13",
            round(voltage, 2),
            round(current, 2),
            round(temperature, 2),
            breaker_status,
        ))

    return rows


def seed_telemetry(cur):
    telemetry_rows = generate_f12_telemetry() + generate_f13_telemetry()

    cur.executemany("""
        INSERT INTO telemetry (
            timestamp, asset_id, feeder_id, voltage, current, temperature, breaker_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, telemetry_rows)


def seed_events(cur):
    events = [
        ("2026-04-01T14:05:00", "LINE_1", "F_12", "overcurrent_alarm", "HIGH", "Current exceeded feeder threshold."),
        ("2026-04-01T14:06:30", "LINE_1", "F_12", "undervoltage_alarm", "MEDIUM", "Voltage dropped below configured limit."),
        ("2026-04-01T14:07:00", "RELAY_1", "F_12", "relay_pickup", "HIGH", "Relay pickup detected on feeder F-12."),
        ("2026-04-01T14:07:00", "BRK_1", "F_12", "breaker_trip", "CRITICAL", "Breaker opened due to protection trip."),
    ]

    cur.executemany("""
        INSERT INTO events (
            event_time, asset_id, feeder_id, event_type, severity, message
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, events)


def seed_incidents(cur):
    incidents = [
        (
            "INC_001",
            "F_12",
            "2026-03-15T13:00:00",
            "Overload due to peak industrial demand.",
            "Load redistribution and temporary feeder rebalancing.",
            "Operator observed sustained current increase before trip."
        ),
        (
            "INC_002",
            "F_12",
            "2026-02-10T12:30:00",
            "Cable overheating on feeder section.",
            "Reduced feeder loading and field inspection.",
            "Repeated thermal stress suspected on same feeder corridor."
        ),
        (
            "INC_003",
            "F_13",
            "2026-03-01T10:20:00",
            "Short voltage dip due to switching operation.",
            "No outage. Monitoring only.",
            "Not considered related to overload behavior."
        ),
    ]

    cur.executemany("""
        INSERT INTO incidents (
            incident_id, feeder_id, start_time, root_cause, resolution, operator_notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, incidents)


def seed_documents(cur):
    documents = [
        (
            "DOC_001",
            "Breaker Trip Investigation Procedure",
            (
                "When a feeder breaker trips, review the alarm timeline, confirm whether "
                "overcurrent or undervoltage conditions were present, inspect relay events, "
                "and compare with recent incident history before restoration."
            ),
            "procedure",
        ),
        (
            "DOC_002",
            "Feeder Overload Handling Guide",
            (
                "Sustained overcurrent combined with declining voltage usually indicates feeder "
                "overload or downstream stress. Recommended actions include load redistribution, "
                "thermal inspection, and comparison with previous overload incidents."
            ),
            "guide",
        ),
        (
            "DOC_003",
            "Relay Event Review Note",
            (
                "Relay pickup followed immediately by breaker opening is consistent with a genuine "
                "protection response when supported by abnormal feeder measurements."
            ),
            "knowledge_note",
        ),
    ]

    cur.executemany("""
        INSERT INTO documents (
            doc_id, title, content, doc_type
        )
        VALUES (?, ?, ?, ?)
    """, documents)


def seed_all():
    conn = get_connection()
    cur = conn.cursor()

    seed_assets(cur)
    seed_telemetry(cur)
    seed_events(cur)
    seed_incidents(cur)
    seed_documents(cur)

    conn.commit()
    conn.close()
    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed_all()