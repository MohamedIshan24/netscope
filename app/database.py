import sqlite3
from contextlib import contextmanager


DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS packets (
    packet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    source_ip TEXT NOT NULL,
    destination_ip TEXT NOT NULL,
    protocol TEXT NOT NULL,
    source_port INTEGER,
    destination_port INTEGER,
    packet_size INTEGER NOT NULL,
    packet_summary TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS packet_time_index ON packets(captured_at);
CREATE INDEX IF NOT EXISTS packet_source_index ON packets(source_ip);
CREATE INDEX IF NOT EXISTS packet_destination_index ON packets(destination_ip);
CREATE INDEX IF NOT EXISTS packet_protocol_index ON packets(protocol);
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    severity TEXT NOT NULL,
    alert_message TEXT NOT NULL,
    observed_value REAL NOT NULL,
    threshold_value REAL NOT NULL
);
"""


def initialize_database(database_path):
    with sqlite3.connect(database_path) as connection:
        connection.executescript(DATABASE_SCHEMA)


@contextmanager
def open_database(database_path):
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()

