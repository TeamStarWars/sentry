import subprocess, json, re
from core.safe import esc
ENC = "cp1252"
ERR = "replace"

def evenements(log="System", nb=20):
    if not re.match(r"^[a-zA-Z0-9/_-]+$", str(log)):
        return "Nom de journal invalide"
    if not isinstance(nb, int) or nb < 1 or nb > 1000:
        nb = 20
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-WinEvent -LogName {esc(log)} -MaxEvents {int(nb)} | Select TimeCreated,Id,LevelDisplayName,ProviderName,Message | ConvertTo-Json"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=30)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if not isinstance(data, list): data = [data]
        if not data:
            return f"Aucun evenement dans {log}"
        lignes = []
        for e in data[:int(nb)]:
            if isinstance(e, dict):
                t = str(e.get("TimeCreated", "?"))[:19]
                lid = e.get("Id", "?")
                lvl = e.get("LevelDisplayName", "?")
                prov = str(e.get("ProviderName", "?"))[:30]
                msg = str(e.get("Message", ""))[:80]
                lignes.append(f"[{t}] #{lid} {lvl} | {prov} | {msg}")
        return f"Evenements {log} ({len(lignes)}):\n" + "\n".join(lignes)
    except:
        return "Erreur journal"

def erreurs_recentes(nb=10):
    return evenements("System", nb)

def securite(nb=10):
    return evenements("Security", nb)

def applications(nb=20):
    return evenements("Application", nb)

def logs_disponibles():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WinEvent -ListLog * | Where {$_.RecordCount -gt 0} | Select LogName,RecordCount | ConvertTo-Json"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if not isinstance(data, list): data = [data]
        logs = [f"{d.get('LogName','?')} ({d.get('RecordCount',0)})" for d in data if isinstance(d, dict)]
        return f"Journaux ({len(logs)}):\n" + "\n".join(logs[:20])
    except:
        return "Erreur journaux"
