import subprocess, json, os, datetime
from core.safe import esc

def capturer(duree=10, fichier=None):
    try:
        d = int(duree)
        d = max(1, min(300, d))
    except:
        d = 10
    if not fichier:
        fichier = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            f"$t=Get-Date; while($(Get-Date)-$t -lt [TimeSpan]::FromSeconds({d})){{Get-NetTCPConnection -ErrorAction SilentlyContinue | Select LocalAddress,LocalPort,RemoteAddress,RemotePort,State,OwningProcess | Export-Csv '{esc(fichier)}' -NoTypeInformation; Start-Sleep 1}}"
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=d + 10)
        if os.path.exists(fichier):
            return f"Capture ({d}s): {fichier} ({os.path.getsize(fichier)} octets)"
        return "Capture: aucun fichier"
    except:
        return "Erreur capture"

def analyser_connexions():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetTCPConnection -ErrorAction SilentlyContinue | Group State | Select Name,Count | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = ["Etat TCP:"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('Name','?')}: {d.get('Count',0)}")
            return "\n".join(lignes)
        return "Aucune connexion"
    except:
        return "Erreur analyse"
