import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def create_csv(packet_rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Time", "Source IP", "Destination IP", "Protocol", "Source Port", "Destination Port", "Size (bytes)", "Summary"])
    for row in packet_rows:
        writer.writerow([row["captured_at"], row["source_ip"], row["destination_ip"], row["protocol"], row["source_port"], row["destination_port"], row["packet_size"], row["packet_summary"]])
    return output.getvalue()


def create_pdf(packet_rows, metrics):
    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
    styles = getSampleStyleSheet()
    content = [Paragraph("Network Traffic Analysis Report", styles["Title"]), Spacer(1, 6 * mm)]
    summary_data = [
        ["Metric", "Value"],
        ["Total packets", f"{metrics['total_packets']:,}"],
        ["Total bytes", f"{metrics['total_bytes']:,}"],
        ["Active hosts", str(len(metrics["hosts"]))],
        ["Protocols", ", ".join(f"{name}: {count}" for name, count in metrics["protocols"].items()) or "None"],
    ]
    summary_table = Table(summary_data, colWidths=[55 * mm, 105 * mm])
    summary_table.setStyle(_table_style())
    content.extend([summary_table, Spacer(1, 7 * mm), Paragraph("Top Hosts", styles["Heading2"])])
    host_data = [["Host", "Sent bytes", "Received bytes", "Total bytes"]]
    host_data.extend([[host["host"], f"{host['sent_bytes']:,}", f"{host['received_bytes']:,}", f"{host['total_bytes']:,}"] for host in metrics["hosts"][:10]])
    host_table = Table(host_data, colWidths=[55 * mm, 35 * mm, 35 * mm, 35 * mm], repeatRows=1)
    host_table.setStyle(_table_style())
    content.extend([host_table, Spacer(1, 7 * mm), Paragraph("Recent Packets", styles["Heading2"])])
    packet_data = [["Time", "Source", "Destination", "Protocol", "Bytes"]]
    packet_data.extend([[row["captured_at"][11:19], row["source_ip"], row["destination_ip"], row["protocol"], str(row["packet_size"])] for row in packet_rows[:50]])
    packet_table = Table(packet_data, colWidths=[25 * mm, 43 * mm, 43 * mm, 25 * mm, 24 * mm], repeatRows=1)
    packet_table.setStyle(_table_style(font_size=7))
    content.append(packet_table)
    document.build(content)
    output.seek(0)
    return output.getvalue()


def _table_style(font_size=9):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CAD5E2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F7FA")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])

