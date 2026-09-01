# NetScope Network Monitoring Dashboard

NetScope is a local PC traffic-analysis dashboard. It captures traffic from a selected interface, stores packet metadata in SQLite, calculates traffic metrics, displays live charts, identifies top talkers and listeners, supports filters and threshold alerts, and exports CSV or A4 PDF reports.

## Main features

- Live capture from a selected network interface using Scapy
- Safe sample-traffic mode for demonstrations
- Source IP, destination IP, protocol, ports, size, time, and summary parsing
- Total packets, total bytes, packet rate, and host counts
- TCP, UDP, DNS, ICMP, and other protocol distribution
- Per-host sent and received traffic
- Live traffic-volume and protocol charts without external chart services
- Filters for IP address, protocol, port, and time range
- Configurable traffic threshold endpoint
- CSV and A4 PDF report export
- Local SQLite storage with a bounded packet history
- Graceful malformed-packet and capture-error handling
- Automated tests for parsing, metrics, and the dashboard page

## Requirements

- Python 3.10 or newer
- Administrator/root access only when performing live packet capture
- Npcap on Windows when using live capture

## Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
sudo .venv/bin/python run.py
```

Open `http://127.0.0.1:5000` in a desktop browser. Choose **Sample traffic** for a permission-free demonstration. Choose **Live interface**, select an interface, and start the application with the required capture privileges for real traffic.

## Testing

```bash
pytest -q
```

## Project structure

```text
network_monitor_dashboard/
  app/
    analyzer.py
    capture.py
    database.py
    reporting.py
    routes.py
    static/
    templates/
  tests/
  requirements.txt
  run.py
```

## Privacy and safety

Captured metadata stays in the local `network_monitor.db` file. Only capture traffic on systems and networks you own or are authorized to inspect. Packet payloads are not stored. Use **Clear captured data** to remove locally stored packet records.

