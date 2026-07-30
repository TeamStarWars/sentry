"""Panel Createur â€” Console centralisee de toutes les machines connectees"""

import json, datetime, threading, os, socket, platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from core import cloud_phare as phare, seclog
from core.safe import sanitize_html as esc_html

PANEL_HTTP = None
PANEL_THREAD = None
PANEL_PORT = 9090
PANEL_ACTIF = False

def _page_creator():
    clients = phare.CLIENTS
    lignes = []
    lignes.append("""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Sentry Createur</title>
<meta http-equiv="refresh" content="10">
<style>
body{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:20px}
h1{color:#58a6ff;text-align:center;font-size:28px}
h2{color:#58a6ff;font-size:18px;margin:0 0 10px 0}
.box{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:18px;margin:14px 0}
table{width:100%;border-collapse:collapse}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid #30363d;font-size:13px}
th{color:#58a6ff}
.on{color:#3fb950}.off{color:#f85149}.warn{color:#f0883e}
pre{background:#0d1117;padding:12px;border-radius:6px;font-size:13px;overflow-x:auto}
.nav{text-align:center;margin:16px 0}
.nav a{color:#58a6ff;text-decoration:none;margin:0 10px;padding:6px 14px;border:1px solid #30363d;border-radius:6px}
.nav a:hover{background:#21262d}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;margin:2px}
.badge.on{background:#0d3d1a;color:#3fb950;border:1px solid #3fb950}
.badge.off{background:#3d0d0d;color:#f85149;border:1px solid #f85149}
</style></head>
<body>
<h1>Sentry Panel Createur</h1>
<div class="nav">
<a href="/">Dashboard</a>
<a href="/api/export">Export JSON</a>
</div>
""")
    if not clients:
        lignes.append('<div class="box"><h2>Aucune machine connectee</h2><p>Lancez phare start, puis phare-client sur les autres machines.</p></div>')
    else:
        lignes.append(f'<div class="box"><h2>Machines connectees ({len(clients)})</h2>')
        lignes.append('<table><tr><th>Machine</th><th>IP</th><th>OS</th><th>CPU/RAM</th><th>Modules</th><th>Alertes</th><th>Vu</th></tr>')
        for cid, info in sorted(clients.items()):
            host = esc_html(info.get("host","?"))
            ip = esc_html(info.get("ip","?"))
            os_info = esc_html(info.get("os","?"))
            cpu = esc_html(info.get("cpu","?"))
            ram_pct = info.get("ram_pct", "?")
            ram = f"{ram_pct}%" if ram_pct != "?" else "?"
            mods = info.get("modules", {})
            mods_html = ""
            for m, active in sorted(mods.items()):
                cls = "on" if active else "off"
                mods_html += f'<span class="badge {cls}">{esc_html(m)}</span>'
            alerts = info.get("alerts_count", 0)
            alerts_color = "on" if alerts == 0 else "warn" if alerts < 5 else "off"
            last_seen = esc_html(info.get("last_seen","?"))
            lignes.append(f"<tr><td><strong>{host}</strong></td><td>{ip}</td><td>{os_info}</td><td>{cpu}<br>RAM {ram}</td><td>{mods_html}</td><td class='{alerts_color}'>{alerts}</td><td>{last_seen}</td></tr>")
        lignes.append("</table></div>")
    lignes.append("""
<div class="box"><h2>Resume global</h2>
""")
    total = len(clients)
    total_mods = sum(1 for c in clients.values() for m, a in c.get("modules",{}).items() if a)
    lignes.append(f"<pre>Machines: {total} | Modules actifs: {total_mods} | Phare: {phare.BIND_ADDR}:{phare.PORT_HTTP}</pre>")
    lignes.append("</div></body></html>")
    return "\n".join(lignes)

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_page_creator().encode("utf-8"))
        elif self.path == "/api/export":
            data = json.dumps({
                "timestamp": str(datetime.datetime.now()),
                "machines": phare.CLIENTS,
                "phare": {"bind": phare.BIND_ADDR, "port": phare.PORT_HTTP}
            }, indent=2)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Disposition", "attachment; filename=creator_export.json")
            self.end_headers()
            self.wfile.write(data.encode())
        else:
            self.send_error(404)
    def log_message(self, fmt, *args):
        pass

def start(port=9090):
    global PANEL_HTTP, PANEL_THREAD, PANEL_PORT, PANEL_ACTIF
    if PANEL_ACTIF:
        return f"Panel deja actif sur http://127.0.0.1:{PANEL_PORT}"
    PANEL_PORT = port
    try:
        PANEL_HTTP = HTTPServer(("127.0.0.1", PANEL_PORT), _Handler)
        PANEL_THREAD = threading.Thread(target=PANEL_HTTP.serve_forever, daemon=True)
        PANEL_THREAD.start()
        PANEL_ACTIF = True
        seclog.ajouter_entree("CREATEUR", f"Panel sur http://127.0.0.1:{PANEL_PORT}")
        return f"Panel createur: http://127.0.0.1:{PANEL_PORT}"
    except Exception as e:
        return f"Erreur panel: {e}"

def stop():
    global PANEL_HTTP, PANEL_ACTIF
    if not PANEL_ACTIF:
        return "Panel inactif"
    PANEL_ACTIF = False
    PANEL_HTTP.shutdown()
    seclog.ajouter_entree("CREATEUR", "Arrete")
    return "Panel arrete"

def status():
    if PANEL_ACTIF:
        return f"Panel: ACTIF sur http://127.0.0.1:{PANEL_PORT} ({len(phare.CLIENTS)} machines)"
    return "Panel: INACTIF"

def display():
    """Affiche le resume en console"""
    clients = phare.CLIENTS
    if not clients:
        return "Aucune machine connectee au Phare."
    lignes = [f"Panel Createur â€” {len(clients)} machine(s) connectee(s)", "=" * 60]
    for cid, info in sorted(clients.items()):
        mods = info.get("modules", {})
        actifs = [m for m, a in mods.items() if a]
        lignes.append(f"\n  {info.get('host','?')} ({info.get('ip','?')})")
        lignes.append(f"  OS: {info.get('os','?')} | CPU: {info.get('cpu','?')} | RAM: {info.get('ram_pct','?')}%")
        lignes.append(f"  Modules actifs: {', '.join(actifs) if actifs else 'aucun'}")
        lignes.append(f"  Alertes: {info.get('alerts_count',0)} | Vu: {info.get('last_seen','?')}")
        lignes.append("  " + "-" * 56)
    return "\n".join(lignes)
