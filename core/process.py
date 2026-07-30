import subprocess, os, json
from core.safe import valider_pid, esc

def liste_processus(tri="cpu"):
    try:
        prop = "CPU" if tri == "cpu" else "WorkingSet"
        cmd = f"Get-Process | Sort {prop} -Descending | Select -First 20 Name,Id,CPU,@{'{'}N='RAM_MB';E={'{[math]::Round($_.WorkingSet/1MB)}'}{'}'} | ConvertTo-Json"
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if not isinstance(data, list): data = [data]
        lignes = [f"{p['Name']}.exe (PID {p['Id']})" for p in data if isinstance(p, dict)]
        return "Processus:\n" + "\n".join(lignes)
    except:
        return "Erreur processus"

def killer(nom):
    import re
    pid_valide = valider_pid(nom)
    if pid_valide:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(pid_valide)], capture_output=True, text=True, timeout=10)
            return f"Processus PID {pid_valide} tue"
        except:
            return "Erreur kill"
    if re.match(r"^[a-zA-Z0-9_.-]+$", nom):
        try:
            subprocess.run(["taskkill", "/F", "/IM", nom.split(".")[0]], capture_output=True, text=True, timeout=10)
            return f"Processus {nom} tue"
        except:
            return "Erreur kill"
    return "Nom de processus invalide"

def analyse_processus(pid=None):
    try:
        if pid is not None:
            pid_val = valider_pid(pid)
            if not pid_val:
                return "PID invalide"
            cmd = f"Get-Process -Id {pid_val} | Select *,@{'{'}N='Path';E={'{try{$_.Path}catch{''}}'}{'}'},@{'{'}N='CPU_Total';E={'{[math]::Round($_.CPU,2)}'}{'}'},@{'{'}N='RAM_MB';E={'{[math]::Round($_.WorkingSet/1MB)}'}{'}'} | ConvertTo-Json"
        else:
            cmd = "Get-Process | Sort CPU -Descending | Select -First 1 Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(data, dict) and data.get("Name"):
            return f"{data['Name']}.exe (PID {data.get('Id','?')}) - RAM: {data.get('RAM_MB','?')}MB, CPU: {data.get('CPU_Total',data.get('CPU','?'))}s"
        return "Aucun processus trouve"
    except:
        return "Erreur analyse"

processus_suspects = []

def ajouter_suspect(nom):
    processus_suspects.append(nom)
    return f"{nom} ajoute a la liste de surveillance"

def lister_suspects():
    if not processus_suspects:
        return "Aucun processus surveille"
    return "Processus surveilles:\n" + "\n".join(processus_suspects)

def verifier_suspects():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Select -ExpandProperty Name"], capture_output=True, text=True, timeout=10)
        actifs = [p.lower().replace(".exe","") for p in r.stdout.split("\n") if p.strip()]
        trouves = [p for p in processus_suspects if p.lower().replace(".exe","") in actifs]
        return f"Suspects: {', '.join(trouves)}" if trouves else "Aucun suspect actif"
    except:
        return "Erreur verif"
