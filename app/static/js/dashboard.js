const dashboardState = { packets: [], refreshTimer: null };
const chartColors = { TCP: "#4ea1ff", UDP: "#2dd4bf", DNS: "#a78bfa", ICMP: "#f59e0b", OTHER: "#8fa3ba" };

document.addEventListener("DOMContentLoaded", () => {
    bindDashboardActions();
    loadNetworkInterfaces();
    refreshDashboard();
    dashboardState.refreshTimer = window.setInterval(refreshDashboard, 1000);
});

function bindDashboardActions() {
    document.getElementById("startCaptureButton").addEventListener("click", startCapture);
    document.getElementById("stopCaptureButton").addEventListener("click", () => sendJson("/api/capture/stop", {}).then(refreshDashboard));
    document.getElementById("applyFiltersButton").addEventListener("click", refreshDashboard);
    document.getElementById("clearPacketsButton").addEventListener("click", clearPackets);
    document.querySelectorAll(".navigation-item").forEach(button => button.addEventListener("click", () => {
        document.querySelectorAll(".navigation-item").forEach(item => item.classList.remove("navigation-item-active"));
        button.classList.add("navigation-item-active");
        document.getElementById(button.dataset.target).scrollIntoView({ behavior: "smooth" });
    }));
}

async function loadNetworkInterfaces() {
    const response = await fetch("/api/interfaces");
    const data = await response.json();
    const select = document.getElementById("networkInterfaceSelect");
    data.interfaces.forEach(interfaceName => select.add(new Option(interfaceName, interfaceName)));
}

async function startCapture() {
    await sendJson("/api/capture/start", { mode: document.getElementById("captureModeSelect").value, interface: document.getElementById("networkInterfaceSelect").value });
    refreshDashboard();
}

async function clearPackets() {
    if (window.confirm("Clear all locally captured packet records?")) {
        await sendJson("/api/packets/clear", {});
        refreshDashboard();
    }
}

async function sendJson(url, payload) {
    const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    return response.json();
}

function filterQuery() {
    const query = new URLSearchParams({ ip: document.getElementById("ipAddressFilter").value, protocol: document.getElementById("protocolFilter").value, port: document.getElementById("portFilter").value, time_range: document.getElementById("timeRangeFilter").value });
    return query.toString();
}

async function refreshDashboard() {
    try {
        const query = filterQuery();
        const response = await fetch(`/api/dashboard?${query}`);
        const data = await response.json();
        dashboardState.packets = data.packets;
        updateMetrics(data.metrics);
        updateCaptureStatus(data.capture, data.capture_error);
        renderPacketTable(data.packets);
        renderHostTable(data.metrics.hosts);
        drawTrafficChart(data.metrics.timeline);
        drawProtocolChart(data.metrics.protocols);
        renderAlerts(data.alerts);
        document.getElementById("csvExportLink").href = `/export/traffic-summary.csv?${query}`;
        document.getElementById("pdfExportLink").href = `/export/traffic-report.pdf?${query}`;
    } catch (error) {
        renderAlerts([{ message: `Dashboard update failed: ${error.message}` }]);
    }
}

function updateMetrics(metrics) {
    document.getElementById("totalPacketsValue").textContent = metrics.total_packets.toLocaleString();
    document.getElementById("totalBytesValue").textContent = formatBytes(metrics.total_bytes);
    document.getElementById("activeHostsValue").textContent = metrics.hosts.length.toLocaleString();
    const latestPoint = metrics.timeline.at(-1);
    document.getElementById("packetRateValue").textContent = `${latestPoint ? latestPoint.packets : 0} pps`;
}

function updateCaptureStatus(capture, errorMessage) {
    document.getElementById("captureStatusIndicator").classList.toggle("running", capture.running);
    document.getElementById("captureStatusText").textContent = capture.running ? "Capture running" : "Capture stopped";
    document.getElementById("captureModeText").textContent = errorMessage || (capture.mode ? `${capture.mode} mode${capture.interface ? ` - ${capture.interface}` : ""}` : "Select a mode");
}

function renderPacketTable(packets) {
    const body = document.getElementById("packetListBody");
    body.innerHTML = packets.map((packet, index) => `<tr data-packet-index="${index}"><td>${escapeHtml(packet.captured_at.slice(11, 23))}</td><td>${escapeHtml(packet.source_ip)}</td><td>${escapeHtml(packet.destination_ip)}</td><td><span class="protocol-badge">${escapeHtml(packet.protocol)}</span></td><td>${packet.source_port ?? "-"}</td><td>${packet.destination_port ?? "-"}</td><td>${packet.packet_size}</td></tr>`).join("");
    body.querySelectorAll("tr").forEach(row => row.addEventListener("click", () => renderPacketDetails(packets[Number(row.dataset.packetIndex)])));
}

function renderPacketDetails(packet) {
    const details = [["Captured", packet.captured_at], ["Source IP", packet.source_ip], ["Destination IP", packet.destination_ip], ["Protocol", packet.protocol], ["Source port", packet.source_port ?? "Not available"], ["Destination port", packet.destination_port ?? "Not available"], ["Packet size", `${packet.packet_size} bytes`], ["Summary", packet.packet_summary]];
    document.getElementById("packetDetailsPanel").innerHTML = `<h3>Packet details</h3>${details.map(([label, value]) => `<div class="detail-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(String(value))}</strong></div>`).join("")}`;
}

function renderHostTable(hosts) {
    document.getElementById("hostTrafficBody").innerHTML = hosts.slice(0, 50).map(host => `<tr><td>${escapeHtml(host.host)}</td><td>${host.sent_packets}</td><td>${formatBytes(host.sent_bytes)}</td><td>${host.received_packets}</td><td>${formatBytes(host.received_bytes)}</td><td>${formatBytes(host.total_bytes)}</td></tr>`).join("");
}

function renderAlerts(alerts) {
    const banner = document.getElementById("alertBanner");
    banner.classList.toggle("hidden", !alerts.length);
    banner.textContent = alerts.length ? alerts.map(alert => alert.message).join(" | ") : "";
}

function drawTrafficChart(timeline) {
    const canvas = document.getElementById("trafficVolumeChart");
    const context = prepareCanvas(canvas);
    const width = canvas.clientWidth, height = canvas.clientHeight, padding = 34;
    context.strokeStyle = "#253a52"; context.lineWidth = 1;
    for (let line = 0; line < 5; line++) { const y = padding + line * ((height - padding * 2) / 4); context.beginPath(); context.moveTo(padding, y); context.lineTo(width - 8, y); context.stroke(); }
    if (!timeline.length) return;
    const maximumBytes = Math.max(...timeline.map(point => point.bytes), 1);
    context.strokeStyle = "#2dd4bf"; context.lineWidth = 2; context.beginPath();
    timeline.forEach((point, index) => { const x = padding + index * ((width - padding - 12) / Math.max(timeline.length - 1, 1)); const y = height - padding - (point.bytes / maximumBytes) * (height - padding * 2); index ? context.lineTo(x, y) : context.moveTo(x, y); }); context.stroke();
    context.fillStyle = "#8fa3ba"; context.font = "11px Segoe UI"; context.fillText(formatBytes(maximumBytes), 3, padding); context.fillText("0 B", 8, height - padding + 4);
}

function drawProtocolChart(protocols) {
    const canvas = document.getElementById("protocolDistributionChart");
    const context = prepareCanvas(canvas);
    const entries = Object.entries(protocols); const total = entries.reduce((sum, [, count]) => sum + count, 0);
    const centerX = canvas.clientWidth / 2, centerY = canvas.clientHeight / 2, radius = Math.min(centerX, centerY) - 35;
    let angle = -Math.PI / 2;
    entries.forEach(([protocol, count]) => { const nextAngle = angle + (count / total) * Math.PI * 2; context.beginPath(); context.arc(centerX, centerY, radius, angle, nextAngle); context.arc(centerX, centerY, radius * 0.58, nextAngle, angle, true); context.closePath(); context.fillStyle = chartColors[protocol] || chartColors.OTHER; context.fill(); angle = nextAngle; });
    context.fillStyle = "#e9f0f8"; context.font = "bold 23px Segoe UI"; context.textAlign = "center"; context.fillText(total.toLocaleString(), centerX, centerY + 4); context.font = "11px Segoe UI"; context.fillStyle = "#8fa3ba"; context.fillText("packets", centerX, centerY + 21);
    document.getElementById("protocolLegend").innerHTML = entries.map(([protocol, count]) => `<span><i class="legend-color" style="background:${chartColors[protocol] || chartColors.OTHER}"></i>${escapeHtml(protocol)} ${count}</span>`).join("");
}

function prepareCanvas(canvas) { const scale = window.devicePixelRatio || 1; canvas.width = canvas.clientWidth * scale; canvas.height = canvas.clientHeight * scale; const context = canvas.getContext("2d"); context.scale(scale, scale); context.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight); return context; }
function formatBytes(bytes) { if (!bytes) return "0 B"; const units = ["B", "KB", "MB", "GB"]; const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1); return `${(bytes / (1024 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`; }
function escapeHtml(value) { return value.replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character])); }

