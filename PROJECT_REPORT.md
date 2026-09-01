# Network Monitoring and Traffic Analysis Dashboard

## Project overview

NetScope is a PC-oriented network monitoring dashboard designed to provide an understandable view of live network activity. It follows a packet-inspector layout with a navigation sidebar, control toolbar, metric cards, traffic charts, packet table, packet details panel, and per-host traffic table. There is no landing page or mobile-style interface.

## Design decisions

The application uses a modular Flask structure. Capture, packet analysis, database access, reporting, routes, presentation, and testing are separated so that each part can evolve independently. SQLite keeps traffic metadata local and requires no external server. Scapy provides cross-platform packet parsing. The frontend requests summarized data once per second, which keeps the interface responsive while capture continues in a background thread.

Only packet metadata is retained: time, addresses, protocol, ports, packet size, and a short packet summary. Packet payload content is not saved. The database keeps a bounded recent history to prevent unlimited growth.

## Functional coverage

The capture manager supports live network interfaces and a generated sample stream. Packet metadata is normalized before storage. Analysis calculates total packets, total bytes, protocol counts, per-second traffic, sent and received traffic per host, top talkers, and top listeners. The filter API accepts IP address, protocol, port, and recent time ranges. A threshold rule produces a visible warning when the recent byte rate exceeds its setting. Current filtered results can be exported to CSV or a professional A4 PDF.

## Interface design

The dashboard targets standard PC screens with a fixed sidebar and a wide workspace. Dark colors reduce glare during longer monitoring sessions. Controls use direct labels such as Start capture, Stop, Apply filters, Export CSV, and Export PDF. Charts are drawn with the browser canvas and do not send captured data to external services.

## Error handling

Malformed packets are skipped without ending the capture loop. Capture permission, driver, and interface errors are returned to the dashboard status area. API validation rejects invalid capture modes and threshold values. The sample mode allows the interface, calculations, filters, and exports to be tested without capture privileges.

## Testing approach

Unit tests verify metadata normalization and known traffic totals. A Flask test verifies that the main dashboard route loads successfully with a temporary database. Manual testing should cover sample capture start and stop, filter combinations, row selection, host rankings, clearing data, both exports, and a live capture attempt on the target operating system.

## Recommended PDF format

The best report format is A4 portrait with 16 mm margins, a clear title, a two-column summary table, a top-host table, and a recent-packet table. Repeating table headings make multi-page exports easier to read. A4 is suitable for university submission, printing, email, and portfolio review.

## Future improvements

Future versions can add PCAP import and export, IPv6-specific charts, configurable alert rules, flow reconstruction, DNS query details, packet search, user-defined dashboards, and long-term aggregation without changing the current module boundaries.
