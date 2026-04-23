from app.db import get_connection
from app.config import DATA_DIR


def create_tables():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS assets;
    DROP TABLE IF EXISTS telemetry;
    DROP TABLE IF EXISTS events;
    DROP TABLE IF EXISTS incidents;
    DROP TABLE IF EXISTS documents;

    CREATE TABLE assets (
        asset_id TEXT PRIMARY KEY,
        asset_type TEXT NOT NULL,
        asset_name TEXT NOT NULL,
        substation_id TEXT NOT NULL,
        feeder_id TEXT NOT NULL,
        upstream_asset_id TEXT,
        location TEXT
    );

    CREATE TABLE telemetry (
        timestamp TEXT NOT NULL,
        asset_id TEXT NOT NULL,
        feeder_id TEXT NOT NULL,
        voltage REAL,
        current REAL,
        temperature REAL,
        breaker_status TEXT
    );

    CREATE TABLE events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_time TEXT NOT NULL,
        asset_id TEXT NOT NULL,
        feeder_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL
    );

    CREATE TABLE incidents (
        incident_id TEXT PRIMARY KEY,
        feeder_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        root_cause TEXT NOT NULL,
        resolution TEXT NOT NULL,
        operator_notes TEXT
    );

    CREATE TABLE documents (
        doc_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        doc_type TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("Database schema created successfully.")


if __name__ == "__main__":
    create_tables()