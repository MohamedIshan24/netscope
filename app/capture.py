import random
import threading
import time
from datetime import datetime, timezone


class CaptureManager:
    def __init__(self, packet_callback, error_callback):
        self.packet_callback = packet_callback
        self.error_callback = error_callback
        self.capture_thread = None
        self.stop_event = threading.Event()
        self.capture_mode = None
        self.interface_name = None

    @property
    def is_running(self):
        return bool(self.capture_thread and self.capture_thread.is_alive())

    def start(self, mode, interface_name=None):
        if self.is_running:
            return False
        self.capture_mode = mode
        self.interface_name = interface_name
        self.stop_event.clear()
        target = self._sample_capture_loop if mode == "sample" else self._live_capture_loop
        self.capture_thread = threading.Thread(target=target, daemon=True, name="traffic-capture-worker")
        self.capture_thread.start()
        return True

    def stop(self):
        self.stop_event.set()
        return True

    def status(self):
        return {"running": self.is_running, "mode": self.capture_mode, "interface": self.interface_name}

    def _sample_capture_loop(self):
        hosts = ["192.168.1.10", "192.168.1.21", "192.168.1.35", "10.0.0.8", "8.8.8.8"]
        protocols = ["TCP", "TCP", "TCP", "UDP", "UDP", "DNS", "ICMP"]
        while not self.stop_event.is_set():
            source, destination = random.sample(hosts, 2)
            protocol = random.choice(protocols)
            port = 53 if protocol == "DNS" else random.choice([22, 80, 443, 5353, 8080])
            self.packet_callback({
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "source_ip": source,
                "destination_ip": destination,
                "protocol": protocol,
                "source_port": random.randint(1024, 65535),
                "destination_port": port,
                "packet_size": random.randint(64, 1514),
                "packet_summary": f"{protocol} {source} to {destination}",
            })
            time.sleep(0.25)

    def _live_capture_loop(self):
        try:
            from scapy.all import DNS, ICMP, IP, IPv6, TCP, UDP, sniff

            def handle_packet(packet):
                try:
                    network_layer = packet.getlayer(IP) or packet.getlayer(IPv6)
                    if network_layer is None:
                        return
                    protocol = "OTHER"
                    source_port = None
                    destination_port = None
                    if packet.haslayer(DNS):
                        protocol = "DNS"
                    elif packet.haslayer(TCP):
                        protocol = "TCP"
                        source_port = int(packet[TCP].sport)
                        destination_port = int(packet[TCP].dport)
                    elif packet.haslayer(UDP):
                        protocol = "UDP"
                        source_port = int(packet[UDP].sport)
                        destination_port = int(packet[UDP].dport)
                    elif packet.haslayer(ICMP):
                        protocol = "ICMP"
                    self.packet_callback({
                        "captured_at": datetime.now(timezone.utc).isoformat(),
                        "source_ip": network_layer.src,
                        "destination_ip": network_layer.dst,
                        "protocol": protocol,
                        "source_port": source_port,
                        "destination_port": destination_port,
                        "packet_size": len(packet),
                        "packet_summary": packet.summary(),
                    })
                except Exception as packet_error:
                    self.error_callback(f"Malformed packet skipped: {packet_error}")

            while not self.stop_event.is_set():
                sniff(iface=self.interface_name or None, prn=handle_packet, store=False, timeout=1)
        except Exception as capture_error:
            self.error_callback(f"Capture stopped: {capture_error}")
            self.stop_event.set()

