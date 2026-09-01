from app import create_app
from app.analyzer import calculate_metrics, normalize_packet


def test_packet_normalization():
    packet = normalize_packet({"source_ip": "10.0.0.1", "destination_ip": "10.0.0.2", "protocol": "tcp", "packet_size": 100})
    assert packet["protocol"] == "TCP"
    assert packet["packet_size"] == 100


def test_metric_calculation():
    packets = [
        {"captured_at": "2026-08-30T10:00:00", "source_ip": "10.0.0.1", "destination_ip": "10.0.0.2", "protocol": "TCP", "packet_size": 100},
        {"captured_at": "2026-08-30T10:00:01", "source_ip": "10.0.0.2", "destination_ip": "10.0.0.1", "protocol": "DNS", "packet_size": 60},
    ]
    metrics = calculate_metrics(packets)
    assert metrics["total_packets"] == 2
    assert metrics["total_bytes"] == 160
    assert metrics["protocols"] == {"TCP": 1, "DNS": 1}


def test_dashboard_page(tmp_path):
    application = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.db")})
    response = application.test_client().get("/")
    assert response.status_code == 200
    assert b"Network Monitoring Dashboard" in response.data

