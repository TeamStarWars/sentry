import socket, threading, json, os, datetime, platform, secrets, hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
from core import system as sysinfo, process as proc, network as net, seclog
from core import snapshot as snap_mod
from core.safe import sanitize_html as esc_html

AUTH_TOKEN = None
SERVEUR_HTTP = None
THREAD_HTTP = None
THREAD_UDP = None
PORT_HTTP = 8089
PORT_UDP = 8090
BIND_ADDR = "127.0.0.1"
SERVEUR_ACTIF = False
CLIENTS = {}
PEERS = []

def _auth_ok(headers):
    if AUTH_TOKEN is None:
        return True
    return hmac.compare_digest(headers.get("X-Auth-Token", ""), AUTH_TOKEN)

def _collecter_status_local():
    """Collecte le status local pour l'envoyer au Phare"""
    import subprocess, json
    modules = {}
    try:
        from core import protector, honeypot
        modules["protecteur"] = protector.ACTIF
        modules["honeypot"] = honeypot.ACTIF
    except:
        pass
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_ComputerSystem | Select TotalPhysicalMemory | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5)
        m = json.loads(r.stdout) if r.stdout.strip() else {}
        ram_total = round(int(m.get("TotalPhysicalMemory", 0)) / (1024**3), 1) if isinstance(m, dict) else 0
    except:
        ram_total = 0
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5)
        m2 = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(m2, dict):
            total = int(m2.get("TotalVisibleMemorySize", 1))
            free = int(m2.get("FreePhysicalMemory", 0))
            ram_pct = round((1 - free/total) * 100, 1) if total > 0 else 0
        else:
            ram_pct = 0
    except:
        ram_pct = 0
    return {
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor() or "?",
        "ram_gb": ram_total,
        "ram_pct": ram_pct,
        "modules": modules,
        "alerts_count": len(seclog.afficher(9999).split("\n")) if seclog.afficher(9999) != "Aucune alerte" else 0,
    }

def _page_dashboard():
    diag = esc_html(sysinfo.diagnostic().replace("\n", "<br>"))
    memo = esc_html(sysinfo.memoire())
    try:
        proc_list = esc_html(proc.liste_processus("cpu").replace("\n", "<br>"))
    except:
        proc_list = "N/A"
    try:
        logs = esc_html(seclog.afficher(10).replace("\n", "<br>"))
    except:
        logs = "Aucune"
    clients_html = ""
    for cid, info in CLIENTS.items():
        host = esc_html(info.get("host","?"))
        ip = esc_html(info.get("ip","?"))
        last = esc_html(info.get("last_seen","?"))
        clients_html += f"<tr><td>{esc_html(cid)}</td><td>{host}</td><td>{ip}</td><td>{last}</td></tr>"
    bind_info = "local" if BIND_ADDR == "127.0.0.1" else f"LAN ({BIND_ADDR})"
    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Vindex Phare</title>
<meta http-equiv="refresh" content="15">
<style>
body {{ font-family:'Segoe UI',sans-serif; background:#0d1117; color:#c9d1d9; margin:0; padding:20px; }}
h1 {{ color:#58a6ff; text-align:center; font-size:28px; }}
.box {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:18px; margin:14px 0; }}
.box h2 {{ color:#58a6ff; margin:0 0 10px 0; font-size:18px; }}
pre {{ background:#0d1117; padding:12px; border-radius:6px; font-size:13px; overflow-x:auto; white-space:pre-wrap; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ padding:8px 12px; text-align:left; border-bottom:1px solid #30363d; font-size:13px; }}
th {{ color:#58a6ff; }}
.nav {{ text-align:center; margin:16px 0; }}
.nav a {{ color:#58a6ff; text-decoration:none; margin:0 10px; padding:6px 14px; border:1px solid #30363d; border-radius:6px; }}
.nav a:hover {{ background:#21262d; }}
.warn {{ background:#1b1b1b; border:1px solid #f0883e; border-radius:8px; padding:12px; margin:14px 0; color:#f0883e; text-align:center; }}
</style></head>
<body>
<h1>Vindex Cloud Phare</h1>
<div class="nav">
<a href="/">Dashboard</a>
<a href="/api/status">API</a>
<a href="/api/clients">Clients</a>
</div>
<div class="box"><h2>Systeme (Phare)</h2><pre>{diag}<br>{memo}</pre></div>
<div class="box"><h2>Top Processus (Phare)</h2><pre>{proc_list}</pre></div>
<div class="box"><h2>Clients Connectes ({len(CLIENTS)})</h2>
<table><tr><th>ID</th><th>Host</th><th>IP</th><th>Dernier contact</th></tr>{clients_html}</table></div>
<div class="box"><h2>Alertes recentes</h2><pre>{logs}</pre></div>
<p style="text-align:center; color:#8b949e;">Phare ({bind_info}) port {PORT_HTTP}</p>
</body></html>"""

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not _auth_ok(self.headers):
            self.send_error(403, "Acces refuse (token invalide ou manquant)")
            return
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_page_dashboard().encode("utf-8"))
        elif self.path == "/api/status":
            self.send_json({"status":"online","clients":len(CLIENTS),"peers":len(PEERS),
                            "bind":BIND_ADDR,"time":str(datetime.datetime.now())[:19]})
        elif self.path == "/api/clients":
            cls = {k: {"host":v.get("host","?"),"ip":v.get("ip","?"),
                       "last_seen":v.get("last_seen","?")} for k,v in CLIENTS.items()}
            self.send_json({"clients":cls})
        elif self.path == "/peers":
            self.send_json({"peers":PEERS})
        elif self.path.startswith("/api/join/"):
            cid = self.path[10:].split("/")[0]
            if not cid or len(cid) > 128:
                self.send_json({"ok":False,"msg":"ID invalide"})
                return
            host = self.headers.get("X-Host", "inconnu")
            now = str(datetime.datetime.now())[:19]
            CLIENTS[cid] = {"host":host,"ip":self.client_address[0],"last_seen":now,"first_seen":now}
            self.send_json({"ok":True,"msg":f"{cid} enregistre"})
        elif self.path == "/api/export":
            data = json.dumps({"timestamp":str(datetime.datetime.now()),"clients":len(CLIENTS),
                               "alerts": seclog.afficher(50)})
            self.send_response(200, "OK")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Disposition","attachment; filename=phare_export.json")
            self.end_headers()
            self.wfile.write(data.encode())
        elif self.path == "/api/creator":
            cls = {}
            for cid, info in CLIENTS.items():
                cls[cid] = {k: v for k, v in info.items()}
            self.send_json({"machines": cls, "total": len(cls),
                            "phare": {"bind": BIND_ADDR, "port": PORT_HTTP}})
        elif self.path.startswith("/api/cmd/"):
            self.send_json({"ok":False,"msg":"Commande a distance desactivee par securite"})
        else:
            self.send_error(404)

    def do_POST(self):
        if not _auth_ok(self.headers):
            self.send_error(403, "Acces refuse")
            return
        if self.path == "/api/heartbeat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(body)
                cid = str(data.get("id", self.client_address[0]))
                if len(cid) > 128:
                    self.send_json({"ok":False})
                    return
                now = str(datetime.datetime.now())[:19]
                client = CLIENTS.get(cid, {})
                client.update({
                    "host": str(data.get("host", client.get("host","?"))),
                    "ip": self.client_address[0],
                    "last_seen": now,
                    "os": str(data.get("os", client.get("os","?"))),
                    "cpu": str(data.get("cpu", client.get("cpu","?"))),
                    "ram_gb": data.get("ram_gb", client.get("ram_gb",0)),
                    "ram_pct": data.get("ram_pct", client.get("ram_pct",0)),
                    "modules": data.get("modules", client.get("modules",{})),
                    "alerts_count": data.get("alerts_count", client.get("alerts_count",0)),
                })
                client.setdefault("first_seen", now)
                CLIENTS[cid] = client
                self.send_json({"ok":True})
            except:
                self.send_json({"ok":False})
        else:
            self.send_json({"ok":False})

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, fmt, *args):
        pass

def _udp_beacon():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind((BIND_ADDR, PORT_UDP))
    s.settimeout(1)
    while SERVEUR_ACTIF:
        try:
            data, addr = s.recvfrom(1024)
            try:
                msg = json.loads(data.decode())
                if msg.get("type") == "PHARE_DISCOVER":
                    rep = json.dumps({"type":"PHARE_HERE","port":PORT_HTTP,"host":platform.node()})
                    s.sendto(rep.encode(), addr)
                elif msg.get("type") == "PHARE_HELLO":
                    cid = str(msg.get("id", addr[0]))
                    if len(cid) <= 128 and cid not in CLIENTS:
                        CLIENTS[cid] = {"host":str(msg.get("host","?")),"ip":addr[0],
                                        "last_seen":str(datetime.datetime.now())[:19]}
                        seclog.ajouter_entree("PHARE", f"Nouveau client: {cid}")
            except:
                pass
        except socket.timeout:
            continue
    s.close()

def start(port=PORT_HTTP, bind=None, token=None):
    global SERVEUR_HTTP, THREAD_HTTP, THREAD_UDP, PORT_HTTP, BIND_ADDR, SERVEUR_ACTIF, AUTH_TOKEN
    if SERVEUR_ACTIF:
        return f"Phare deja actif sur http://{BIND_ADDR}:{PORT_HTTP}"
    PORT_HTTP = port
    if bind:
        BIND_ADDR = bind
    if token:
        AUTH_TOKEN = token
    else:
        AUTH_TOKEN = secrets.token_hex(16)
        seclog.ajouter_entree("PHARE", f"Token d'auth genere: {AUTH_TOKEN}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except:
        ip_local = "127.0.0.1"
    SERVEUR_HTTP = HTTPServer((BIND_ADDR, PORT_HTTP), _Handler)
    THREAD_HTTP = threading.Thread(target=SERVEUR_HTTP.serve_forever, daemon=True)
    THREAD_HTTP.start()
    if BIND_ADDR in ("0.0.0.0", "127.0.0.1"):
        THREAD_UDP = threading.Thread(target=_udp_beacon, daemon=True)
        THREAD_UDP.start()
    SERVEUR_ACTIF = True
    addr_display = ip_local if BIND_ADDR == "0.0.0.0" else BIND_ADDR
    seclog.ajouter_entree("PHARE", f"Demarre http://{addr_display}:{PORT_HTTP}")
    msg = f"Phare actif: http://{addr_display}:{PORT_HTTP}\nToken: {AUTH_TOKEN[:8]}... (X-Auth-Token header)"
    if BIND_ADDR != "0.0.0.0":
        msg += "\nUtilisez start(..., bind='0.0.0.0') pour l'acces LAN"
    return msg

def stop():
    global SERVEUR_HTTP, SERVEUR_ACTIF
    if not SERVEUR_ACTIF:
        return "Phare inactif"
    SERVEUR_ACTIF = False
    SERVEUR_HTTP.shutdown()
    seclog.ajouter_entree("PHARE", "Arrete")
    return "Phare arrete"

def status():
    if SERVEUR_ACTIF:
        return f"Phare: ACTIF ({len(CLIENTS)} clients, {len(PEERS)} pairs) sur {BIND_ADDR}:{PORT_HTTP}"
    return "Phare: INACTIF"

def join(hote, port=PORT_HTTP, token=None):
    try:
        import urllib.request
        r = urllib.request.Request(f"http://{hote}:{port}/api/join/{platform.node()}",
                                   headers={"X-Host": platform.node()})
        if token:
            r.add_header("X-Auth-Token", token)
        urllib.request.urlopen(r, timeout=10)
        return f"Connecte au Phare: {hote}:{port}"
    except Exception as e:
        return f"Erreur connexion: {e}"

def _heartbeat_loop(hote, port, token):
    import urllib.request, time
    while SERVEUR_ACTIF:
        try:
            status = _collecter_status_local()
            payload = {"id": platform.node(), "host": platform.node()}
            payload.update(status)
            data = json.dumps(payload).encode()
            req = urllib.request.Request(f"http://{hote}:{port}/api/heartbeat", data=data,
                                         headers={"Content-Type":"application/json"}, method="POST")
            if token:
                req.add_header("X-Auth-Token", token)
            urllib.request.urlopen(req, timeout=5)
        except:
            pass
        time.sleep(30)

def start_client(hote, port=PORT_HTTP, token=None):
    global THREAD_HTTP, SERVEUR_ACTIF
    if SERVEUR_ACTIF:
        return "Deja en mode serveur. Arretez le phare d'abord."
    SERVEUR_ACTIF = True
    THREAD_HTTP = threading.Thread(target=_heartbeat_loop, args=(hote, port, token), daemon=True)
    THREAD_HTTP.start()
    seclog.ajouter_entree("PHARE", f"Mode client: {hote}:{port}")
    return f"Client Phare: {hote}:{port} (heartbeat 30s)"
