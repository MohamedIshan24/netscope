from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


project_directory = Path(__file__).resolve().parent
output_directory = project_directory / "output" / "pdf"
output_directory.mkdir(parents=True, exist_ok=True)
output_path = output_directory / "NetScope_Project_Report.pdf"

pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="DejaVuSans-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#16324F"), alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="ReportSubtitle", parent=styles["Normal"], fontName="DejaVuSans", fontSize=11, leading=16, textColor=colors.HexColor("#547087"), alignment=TA_CENTER, spaceAfter=20))
styles.add(ParagraphStyle(name="SectionTitle", parent=styles["Heading1"], fontName="DejaVuSans-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#16324F"), spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle(name="BodyTextCustom", parent=styles["BodyText"], fontName="DejaVuSans", fontSize=9.5, leading=14, textColor=colors.HexColor("#263746"), spaceAfter=7))
styles.add(ParagraphStyle(name="FooterText", parent=styles["Normal"], fontName="DejaVuSans", fontSize=8, textColor=colors.HexColor("#6B7C8D")))


def page_decoration(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor("#16324F"))
    canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D6E0E8"))
    canvas.line(16 * mm, 13 * mm, width - 16 * mm, 13 * mm)
    canvas.setFont("DejaVuSans", 8)
    canvas.setFillColor(colors.HexColor("#6B7C8D"))
    canvas.drawString(16 * mm, 8 * mm, "NetScope Network Monitoring Dashboard")
    canvas.drawRightString(width - 16 * mm, 8 * mm, f"Page {document.page}")
    canvas.restoreState()


def paragraph(text):
    return Paragraph(text, styles["BodyTextCustom"])


document = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm, topMargin=18 * mm, bottomMargin=18 * mm, title="NetScope Project Report")
story = [Spacer(1, 18 * mm), Paragraph("Network Monitoring and<br/>Traffic Analysis Dashboard", styles["ReportTitle"]), Paragraph("Project Design, Implementation, Testing, and User Guide", styles["ReportSubtitle"]), Spacer(1, 8 * mm)]
overview_table = Table([
    ["Project name", "NetScope"], ["Application type", "Local PC dashboard"], ["Backend", "Python, Flask, Scapy, SQLite"], ["Frontend", "HTML, CSS, JavaScript, Canvas charts"], ["Report format", "A4 portrait PDF"],
], colWidths=[48 * mm, 108 * mm])
overview_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E9F1F6")), ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#16324F")), ("FONTNAME", (0, 0), (0, -1), "DejaVuSans-Bold"), ("FONTNAME", (1, 0), (1, -1), "DejaVuSans"), ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#B9C9D5")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
story.extend([overview_table, PageBreak(), Paragraph("1. Project Overview", styles["SectionTitle"]), paragraph("NetScope is a PC-oriented network monitoring dashboard that captures and analyzes network traffic in near real time. It provides a Wireshark-like packet list and details panel together with protocol charts, traffic volume, bandwidth statistics, host rankings, filters, alerts, and report export."), paragraph("The application works in live-interface mode for authorized traffic capture and in sample mode for safe demonstration without capture permissions. Captured information remains on the computer by default."), Paragraph("2. System Architecture", styles["SectionTitle"]), paragraph("The project separates capture, analysis, persistence, routes, reporting, presentation, and testing. A background worker captures traffic while the Flask application serves dashboard data. SQLite stores a bounded set of packet metadata. The browser requests updated data once per second and renders charts locally."), Paragraph("3. Functional Requirements Coverage", styles["SectionTitle"])])
requirements = [
    ["Requirement", "Implementation"], ["Live capture", "Scapy capture from a selected interface"], ["Packet parsing", "IP addresses, protocol, ports, size, time, summary"], ["Traffic metrics", "Packets, bytes, packet rate, per-second timeline"], ["Protocol breakdown", "TCP, UDP, DNS, ICMP, and other"], ["Host analysis", "Sent/received totals, top talkers and listeners"], ["Charts", "Canvas traffic line chart and protocol doughnut chart"], ["Filtering", "IP, protocol, port, and time range"], ["Alerts", "Configurable byte-rate threshold"], ["Exports", "Filtered CSV and A4 PDF"],
]
requirements_table = Table(requirements, colWidths=[48 * mm, 108 * mm], repeatRows=1)
requirements_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"), ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"), ("FONTSIZE", (0, 0), (-1, -1), 8.5), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#C6D2DC")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F7FA")]), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
story.extend([requirements_table, PageBreak(), Paragraph("4. Data and Privacy", styles["SectionTitle"]), paragraph("The database stores packet metadata only. Payload content is not retained. Records remain in a local SQLite file and older rows are removed when the configured history limit is reached. The operator can clear all records from the dashboard."), Paragraph("5. Error Handling and Performance", styles["SectionTitle"]), paragraph("Malformed packets are skipped and reported without terminating the complete application. Permission, interface, or driver errors appear in the capture status area. Capture runs in a daemon thread, while database indexes support common time, address, and protocol queries. API responses limit the displayed packet list so continuous capture does not freeze the interface."), Paragraph("6. Testing", styles["SectionTitle"]), paragraph("Automated tests verify packet normalization, known metric totals, and successful dashboard loading with a temporary database. Manual tests cover sample capture, live capture, start and stop behavior, filter combinations, packet selection, host rankings, clearing stored records, threshold alerts, and CSV/PDF downloads."), Paragraph("7. Installation and Operation", styles["SectionTitle"]), paragraph("Create a Python virtual environment, install requirements.txt, and run run.py. Open http://127.0.0.1:5000 in a PC browser. Sample mode runs without special access. Live capture needs administrator/root privileges and may require Npcap on Windows."), Paragraph("8. Recommended PDF Format", styles["SectionTitle"]), paragraph("A4 portrait is the recommended submission format. It prints reliably, fits standard university report requirements, and is comfortable to review on a laptop. The live PDF export uses 16 mm margins, compact summary tables, repeating column headings, and page breaks handled automatically for larger traffic reports."), Paragraph("9. Future Development", styles["SectionTitle"]), paragraph("The modular design can be extended with PCAP input and output, saved filter profiles, IPv6-specific reporting, multiple alert rules, DNS query analysis, flow reconstruction, long-term aggregation, and user-configurable charts without redesigning the complete system.")])
document.build(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(output_path)
