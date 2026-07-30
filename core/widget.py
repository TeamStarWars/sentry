"""Widget desktop — Overlay stats PC et alertes securite en temps reel"""
import subprocess, json, os, threading, time, datetime, re
try:
    import tkinter as tk
    from tkinter import font as tkfont
    _TK_OK = True
except ImportError:
    _TK_OK = False

from core import seclog, system as sysinfo

WIDGET_ACTIF = False
WIDGET_THREAD = None
WIDGET_ROOT = None

def _ps(cmd, timeout=8):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, timeout=timeout)
        raw = r.stdout.decode("utf-8", errors="replace")
        return raw.encode("cp1252", errors="replace").decode("cp1252")
    except:
        return ""

def _collecter_stats():
    cpu = ram = disk = up = conns = "?"
    r = _ps("Get-CimInstance Win32_Processor | Select -ExpandProperty LoadPercentage -ErrorAction SilentlyContinue")
    if r.strip(): cpu = r.strip().split("\n")[0][:10]
    r = _ps("$os=Get-CimInstance Win32_OperatingSystem; '{0},{1}' -f [math]::Round($os.TotalVisibleMemorySize/1MB,1), [math]::Round(($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/$os.TotalVisibleMemorySize*100,1)")
    parts = r.strip().split(",")
    if len(parts) == 2: ram = f"{parts[0]}GB ({parts[1]}%)"
    r = _ps("Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\"C:\"' | Select @{N='F';E={[math]::Round($_.FreeSpace/1GB,1)}},@{N='T';E={[math]::Round($_.Size/1GB,1)}},@{N='P';E={[math]::Round($_.FreeSpace/$_.Size*100,1)}} | ConvertTo-Json")
    try:
        d = json.loads(r) if r.strip() else {}
        if isinstance(d, dict) and d.get('T'):
            disk = f"{d['F']}/{d['T']}GB ({d['P']}% libre)"
    except: pass
    r = _ps("$b=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime; $d=(Get-Date)-$b; '{0},{1},{2}' -f $d.Days,$d.Hours,$d.Minutes")
    parts = r.strip().split(",")
    if len(parts) == 3: up = f"{parts[0]}j {parts[1]}h {parts[2]}m"
    r = _ps("(Get-NetTCPConnection -ErrorAction SilentlyContinue | Where State -eq Established).Count")
    if r.strip(): conns = r.strip().split("\n")[0][:10]
    return cpu, ram, disk, up, conns

def _collecter_alertes():
    alerte_count = 0
    ransomware = 0
    malware = 0
    recentes = []
    if os.path.exists(seclog.LOG_FILE):
        try:
            with open(seclog.LOG_FILE, "r", encoding="utf-8") as f:
                entrees = json.load(f)
            alerte_count = len(entrees)
            for e in entrees:
                cat = e.get("categorie", "").upper()
                if "RANSOM" in cat: ransomware += 1
                if "MALWARE" in cat or "VIRUS" in cat: malware += 1
                if len(recentes) < 4:
                    t = str(e.get("timestamp", "?"))[:16]
                    msg = str(e.get("message", ""))[:60]
                    recentes.append(f"[{t}] {msg}")
        except: pass
    return alerte_count, ransomware, malware, recentes

def _creer_widget():
    global WIDGET_ROOT
    WIDGET_ROOT = tk.Tk()
    WIDGET_ROOT.title("Vindex Widget")
    WIDGET_ROOT.overrideredirect(True)
    WIDGET_ROOT.attributes("-topmost", True)
    WIDGET_ROOT.attributes("-alpha", 0.88)
    WIDGET_ROOT.configure(bg="#0d1117")

    w, h = 380, 420
    sw = WIDGET_ROOT.winfo_screenwidth()
    WIDGET_ROOT.geometry(f"{w}x{h}+{sw-w-20}+50")

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=9)
    WIDGET_ROOT.option_add("*Font", default_font)

    canvas = tk.Frame(WIDGET_ROOT, bg="#0d1117", highlightthickness=1, highlightbackground="#30363d")
    canvas.pack(fill=tk.BOTH, expand=True)

    drag_data = {"x": 0, "y": 0}
    def on_press(e):
        drag_data["x"] = e.x
        drag_data["y"] = e.y
    def on_drag(e):
        dx = e.x - drag_data["x"]
        dy = e.y - drag_data["y"]
        x = WIDGET_ROOT.winfo_x() + dx
        y = WIDGET_ROOT.winfo_y() + dy
        WIDGET_ROOT.geometry(f"+{x}+{y}")
    canvas.bind("<Button-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)

    header = tk.Label(canvas, text="VINDEX WIDGET", bg="#0d1117", fg="#58a6ff",
                      font=("Segoe UI", 10, "bold"), anchor="w", padx=10, pady=4)
    header.pack(fill=tk.X)

    lbl_cpu = tk.Label(canvas, text="CPU: ...", bg="#0d1117", fg="#c9d1d9",
                       anchor="w", padx=10, pady=1)
    lbl_ram = tk.Label(canvas, text="RAM: ...", bg="#0d1117", fg="#c9d1d9",
                       anchor="w", padx=10, pady=1)
    lbl_disk = tk.Label(canvas, text="Disque: ...", bg="#0d1117", fg="#c9d1d9",
                        anchor="w", padx=10, pady=1)
    lbl_up = tk.Label(canvas, text="Uptime: ...", bg="#0d1117", fg="#c9d1d9",
                      anchor="w", padx=10, pady=1)
    lbl_conn = tk.Label(canvas, text="Connexions: ...", bg="#0d1117", fg="#c9d1d9",
                        anchor="w", padx=10, pady=1)
    lbl_cpu.pack(fill=tk.X)
    lbl_ram.pack(fill=tk.X)
    lbl_disk.pack(fill=tk.X)
    lbl_up.pack(fill=tk.X)
    lbl_conn.pack(fill=tk.X)

    sep = tk.Frame(canvas, bg="#30363d", height=1)
    sep.pack(fill=tk.X, padx=10, pady=6)
    sep2 = tk.Frame(canvas, bg="#30363d", height=1)
    sep2.pack(fill=tk.X, padx=10, pady=6)

    lbl_alert_header = tk.Label(canvas, text="SECURITE", bg="#0d1117", fg="#f0883e",
                                font=("Segoe UI", 9, "bold"), anchor="w", padx=10, pady=2)
    lbl_alert_header.pack(fill=tk.X)

    lbl_ransom = tk.Label(canvas, text="Ransomware: ...", bg="#0d1117", fg="#f85149",
                          anchor="w", padx=10, pady=1)
    lbl_malware = tk.Label(canvas, text="Malware: ...", bg="#0d1117", fg="#f85149",
                           anchor="w", padx=10, pady=1)
    lbl_total = tk.Label(canvas, text="Alertes: ...", bg="#0d1117", fg="#f0883e",
                         anchor="w", padx=10, pady=1)
    lbl_ransom.pack(fill=tk.X)
    lbl_malware.pack(fill=tk.X)
    lbl_total.pack(fill=tk.X)

    lbl_recent = tk.Label(canvas, text="", bg="#0d1117", fg="#8b949e",
                          anchor="w", padx=10, pady=1, justify=tk.LEFT,
                          wraplength=360)
    lbl_recent.pack(fill=tk.X, expand=True)

    footer = tk.Label(canvas, text="Ctrl+Q quitter | Glisser-deplacer",
                      bg="#0d1117", fg="#30363d", font=("Segoe UI", 7), anchor="w", padx=10, pady=2)
    footer.pack(fill=tk.X, side=tk.BOTTOM)

    def _update():
        if not WIDGET_ACTIF:
            return
        try:
            cpu, ram, disk, up, conns = _collecter_stats()
            lbl_cpu.config(text=f"CPU: {cpu}%")
            lbl_ram.config(text=f"RAM: {ram}")
            lbl_disk.config(text=f"C: {disk}")
            lbl_up.config(text=f"Uptime: {up}")
            lbl_conn.config(text=f"Connexions: {conns}")

            total, rans, mal, recents = _collecter_alertes()
            lbl_ransom.config(text=f"Ransomware: {rans}")
            lbl_malware.config(text=f"Malware: {mal}")
            lbl_total.config(text=f"Alertes (total): {total}")
            if recents:
                lbl_recent.config(text="\n".join(recents))
            else:
                lbl_recent.config(text="Aucune alerte recente")
        except:
            pass
        WIDGET_ROOT.after(3000, _update)

    WIDGET_ROOT.bind("<Control-q>", lambda e: _quitter())
    WIDGET_ROOT.bind("<Control-Q>", lambda e: _quitter())
    WIDGET_ROOT.protocol("WM_DELETE_WINDOW", _quitter)
    WIDGET_ROOT.after(500, _update)
    WIDGET_ROOT.mainloop()

def _quitter():
    global WIDGET_ACTIF, WIDGET_ROOT
    WIDGET_ACTIF = False
    if WIDGET_ROOT:
        try:
            WIDGET_ROOT.quit()
            WIDGET_ROOT.destroy()
        except:
            pass
        WIDGET_ROOT = None

def demarrer():
    global WIDGET_ACTIF, WIDGET_THREAD
    if not _TK_OK:
        return "tkinter non disponible (installez python avec l'option tcl/tk)"
    if WIDGET_ACTIF:
        return "Widget deja actif"
    WIDGET_ACTIF = True
    WIDGET_THREAD = threading.Thread(target=_creer_widget, daemon=True)
    WIDGET_THREAD.start()
    return "Widget Vindex lance (Ctrl+Q pour quitter)"

def arreter():
    global WIDGET_ACTIF
    if not WIDGET_ACTIF:
        return "Widget inactif"
    WIDGET_ACTIF = False
    _quitter()
    return "Widget arrete"

def statut():
    return "Widget: ACTIF" if WIDGET_ACTIF else "Widget: INACTIF"
