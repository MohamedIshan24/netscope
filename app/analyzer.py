from collections import Counter, defaultdict
from datetime import datetime, timezone


def normalize_packet(packet_data):
    required_fields = ("source_ip", "destination_ip", "protocol", "packet_size")
    if any(field not in packet_data for field in required_fields):
        raise ValueError("Packet metadata is incomplete")
    packet_size = max(0, int(packet_data["packet_size"]))
    return {
        "captured_at": packet_data.get("captured_at") or datetime.now(timezone.utc).isoformat(),
        "source_ip": str(packet_data["source_ip"]),
        "destination_ip": str(packet_data["destination_ip"]),
        "protocol": str(packet_data["protocol"]).upper(),
        "source_port": packet_data.get("source_port"),
        "destination_port": packet_data.get("destination_port"),
        "packet_size": packet_size,
        "packet_summary": str(packet_data.get("packet_summary", "Captured packet"))[:500],
    }


def calculate_metrics(packet_rows):
    protocols = Counter()
    hosts = defaultdict(lambda: {"sent_bytes": 0, "received_bytes": 0, "sent_packets": 0, "received_packets": 0})
    timeline = defaultdict(lambda: {"bytes": 0, "packets": 0})
    total_bytes = 0
    for row in packet_rows:
        size = row["packet_size"]
        total_bytes += size
        protocols[row["protocol"]] += 1
        hosts[row["source_ip"]]["sent_bytes"] += size
        hosts[row["source_ip"]]["sent_packets"] += 1
        hosts[row["destination_ip"]]["received_bytes"] += size
        hosts[row["destination_ip"]]["received_packets"] += 1
        second = row["captured_at"][:19]
        timeline[second]["bytes"] += size
        timeline[second]["packets"] += 1
    host_rows = [{"host": host, **values, "total_bytes": values["sent_bytes"] + values["received_bytes"]} for host, values in hosts.items()]
    host_rows.sort(key=lambda item: item["total_bytes"], reverse=True)
    timeline_rows = [{"time": second, **values} for second, values in sorted(timeline.items())]
    return {
        "total_packets": len(packet_rows),
        "total_bytes": total_bytes,
        "protocols": dict(protocols),
        "hosts": host_rows,
        "timeline": timeline_rows[-60:],
    }

