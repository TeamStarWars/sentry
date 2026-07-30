import json, os, datetime, subprocess

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "snapshots")

def _assurer_dossier():
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def sauvegarder(nom=None):
    _assurer_dossier()
    if not nom:
        nom = f"snapshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    chemin = os.path.join(SNAPSHOT_DIR, f"{nom}.json")

    etat = {
        "date": str(datetime.datetime.now()),
        "nom": nom,
        "processus": _capture_processus(),
        "services": _capture_services(),
        "connexions": _capture_connexions(),
        "demarrage": _capture_demarrage(),
    }

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(etat, f, indent=2, ensure_ascii=False)
    return f"Snapshot '{nom}' sauvegarde ({len(etat['processus'])} processus)"

def _capture_processus():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Select Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        return data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    except:
        return []

def _capture_services():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Service | Where Status -eq Running | Select Name | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        return [s.get("Name", "?") for s in (data if isinstance(data, list) else [data]) if isinstance(s, dict)]
    except:
        return []

def _capture_connexions():
    try:
        r = subprocess.run(["netstat", "-n"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=5)
        return [l.strip() for l in r.stdout.split("\n") if "ESTABLISHED" in l]
    except:
        return []

def _capture_demarrage():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_StartupCommand | Select Name | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        return [s.get("Name", "?") for s in (data if isinstance(data, list) else [data]) if isinstance(s, dict)]
    except:
        return []

def lister():
    _assurer_dossier()
    fichiers = [f.replace(".json", "") for f in os.listdir(SNAPSHOT_DIR) if f.endswith(".json")]
    if not fichiers:
        return "Aucun snapshot disponible"
    return f"Snapshots disponibles:\n" + "\n".join(sorted(fichiers))

def comparer(nom1, nom2):
    _assurer_dossier()
    try:
        with open(os.path.join(SNAPSHOT_DIR, f"{nom1}.json"), encoding="utf-8") as f:
            s1 = json.load(f)
        with open(os.path.join(SNAPSHOT_DIR, f"{nom2}.json"), encoding="utf-8") as f:
            s2 = json.load(f)
    except FileNotFoundError:
        return "Snapshot introuvable"

    diffs = []

    pids1 = {p.get("Id") for p in s1.get("processus", []) if isinstance(p, dict)}
    pids2 = {p.get("Id") for p in s2.get("processus", []) if isinstance(p, dict)}
    nouveaux = pids2 - pids1
    termines = pids1 - pids2
    if nouveaux:
        noms = [p.get("Name", "?") for p in s2["processus"] if isinstance(p, dict) and p.get("Id") in nouveaux]
        diffs.append(f"Nouveaux processus: {', '.join(noms)}")
    if termines:
        noms = [p.get("Name", "?") for p in s1["processus"] if isinstance(p, dict) and p.get("Id") in termines]
        diffs.append(f"Processus termines: {', '.join(noms)}")

    svc1, svc2 = set(s1.get("services", [])), set(s2.get("services", []))
    if svc2 - svc1:
        diffs.append(f"Nouveaux services: {', '.join(svc2 - svc1)}")
    if svc1 - svc2:
        diffs.append(f"Services arretes: {', '.join(svc1 - svc2)}")

    conn1, conn2 = set(s1.get("connexions", [])), set(s2.get("connexions", []))
    if conn2 - conn1:
        diffs.append(f"Nouvelles connexions: {len(conn2 - conn1)}")

    if not diffs:
        return f"Aucune difference entre '{nom1}' et '{nom2}'"
    return f"Differences:\n" + "\n".join(diffs)
