import io
import sqlite3
from datetime import datetime, timezone
from flask import Blueprint, Response, current_app, jsonify, render_template, request, send_file
from .analyzer import calculate_metrics, normalize_packet
from .capture import CaptureManager
from .database import open_database
from .reporting import create_csv, create_pdf


dashboard_blueprint = Blueprint("dashboard", __name__)
capture_manager = None
capture_error_message = ""
alert_threshold_bytes_per_second = 250000


def store_packet(packet_data):
    packet = normalize_packet(packet_data)
    database_path = current_app.config["DATABASE_PATH"]
    with open_database(database_path) as connection:
        connection.execute("""INSERT INTO packets (captured_at, source_ip, destination_ip, protocol, source_port, destination_port, packet_size, packet_summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", tuple(packet.values()))
        maximum_rows = current_app.config["MAX_PACKET_ROWS"]
        connection.execute("DELETE FROM packets WHERE packet_id NOT IN (SELECT packet_id FROM packets ORDER BY packet_id DESC LIMIT ?)", (maximum_rows,))


def record_capture_error(message):
    global capture_error_message
    capture_error_message = message


def get_capture_manager():
    global capture_manager
    if capture_manager is None:
        application = current_app._get_current_object()

        def store_packet_with_context(packet_data):
            with application.app_context():
                store_packet(packet_data)

        capture_manager = CaptureManager(store_packet_with_context, record_capture_error)
    return capture_manager


def query_packets():
    clauses = []
    values = []
    ip_filter = request.args.get("ip", "").strip()
    protocol_filter = request.args.get("protocol", "").strip().upper()
    port_filter = request.args.get("port", "").strip()
    time_range = request.args.get("time_range", "all")
    if ip_filter:
        clauses.append("(source_ip = ? OR destination_ip = ?)")
        values.extend([ip_filter, ip_filter])
    if protocol_filter and protocol_filter != "ALL":
        clauses.append("protocol = ?")
        values.append(protocol_filter)
    if port_filter.isdigit():
        clauses.append("(source_port = ? OR destination_port = ?)")
        values.extend([int(port_filter), int(port_filter)])
    if time_range in {"1", "5", "15", "60"}:
        clauses.append("datetime(captured_at) >= datetime('now', ?)")
        values.append(f"-{time_range} minutes")
    where_clause = " WHERE " + " AND ".join(clauses) if clauses else ""
    limit = min(max(request.args.get("limit", 500, type=int), 1), 5000)
    with open_database(current_app.config["DATABASE_PATH"]) as connection:
        return connection.execute(f"SELECT * FROM packets{where_clause} ORDER BY packet_id DESC LIMIT ?", (*values, limit)).fetchall()


@dashboard_blueprint.get("/")
def dashboard():
    return render_template("dashboard.html")


@dashboard_blueprint.get("/api/interfaces")
def interfaces():
    try:
        import psutil
        names = sorted(psutil.net_if_addrs().keys())
    except Exception:
        names = []
    return jsonify({"interfaces": names})


@dashboard_blueprint.post("/api/capture/start")
def start_capture():
    payload = request.get_json(silent=True) or {}
    mode = payload.get("mode", "sample")
    if mode not in {"sample", "live"}:
        return jsonify({"error": "Invalid capture mode"}), 400
    started = get_capture_manager().start(mode, payload.get("interface"))
    return jsonify({"started": started, "status": get_capture_manager().status()})


@dashboard_blueprint.post("/api/capture/stop")
def stop_capture():
    get_capture_manager().stop()
    return jsonify({"stopped": True})


@dashboard_blueprint.get("/api/dashboard")
def dashboard_data():
    packet_rows = query_packets()
    packets = [dict(row) for row in packet_rows]
    metrics = calculate_metrics(packets)
    recent_rate = sum(point["bytes"] for point in metrics["timeline"][-2:]) / max(len(metrics["timeline"][-2:]), 1)
    alerts = []
    if recent_rate > alert_threshold_bytes_per_second:
        alerts.append({"severity": "warning", "message": "Traffic rate is above the configured threshold", "value": recent_rate, "threshold": alert_threshold_bytes_per_second})
    return jsonify({"packets": packets[:300], "metrics": metrics, "alerts": alerts, "capture": get_capture_manager().status(), "capture_error": capture_error_message})


@dashboard_blueprint.post("/api/settings/threshold")
def update_threshold():
    global alert_threshold_bytes_per_second
    payload = request.get_json(silent=True) or {}
    try:
        threshold = int(payload.get("bytes_per_second", 0))
        if threshold <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "Threshold must be a positive number"}), 400
    alert_threshold_bytes_per_second = threshold
    return jsonify({"bytes_per_second": threshold})


@dashboard_blueprint.post("/api/packets/clear")
def clear_packets():
    with open_database(current_app.config["DATABASE_PATH"]) as connection:
        connection.execute("DELETE FROM packets")
    return jsonify({"cleared": True})


@dashboard_blueprint.get("/export/traffic-summary.csv")
def export_csv():
    content = create_csv(query_packets())
    return Response(content, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=traffic-summary.csv"})


@dashboard_blueprint.get("/export/traffic-report.pdf")
def export_pdf():
    rows = [dict(row) for row in query_packets()]
    pdf_bytes = create_pdf(rows, calculate_metrics(rows))
    return send_file(io.BytesIO(pdf_bytes), mimetype="application/pdf", as_attachment=True, download_name="traffic-analysis-report.pdf")
