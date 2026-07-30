import subprocess, json

def analyser(pid):
    try:
        pid = int(pid)
    except:
        return "PID invalide"

    resultats = []

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select Name,Id,Path,StartTime,@{'{'}N='RAM_MB';E={'{[math]::Round($_.WorkingSet/1MB)}'}{'}'} | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        p = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(p, dict) and p.get("Name"):
            resultats.append(f"--- {p.get('Name')}.exe (PID {p.get('Id')}) ---")
            resultats.append(f"Chemin: {p.get('Path', 'N/A')}")
            resultats.append(f"RAM: {p.get('RAM_MB', '?')}MB")
        else:
            return f"PID {pid} introuvable"
    except:
        resultats.append("Erreur infos processus")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select -ExpandProperty Modules | Select ModuleName,FileName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        modules = json.loads(r.stdout) if r.stdout.strip() else []
        if not isinstance(modules, list): modules = [modules]
        resultats.append(f"\nDLLs chargees ({len(modules)}):")
        for m in modules[:15]:
            if isinstance(m, dict):
                resultats.append(f"  {m.get('ModuleName', '?')}")
        if len(modules) > 15:
            resultats.append(f"  ... et {len(modules)-15} autres")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select -ExpandProperty StartInfo | Select EnvironmentVariables | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
    except:
        pass

    try:
        r = subprocess.run(["netstat", "-bno"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=10)
        lignes = r.stdout.split("\n")
        conns = []
        i = 0
        while i < len(lignes):
            l = lignes[i].strip()
            if f"PID={pid}" in l or l.endswith(str(pid)):
                conns.append(lignes[i-1].strip() if i > 0 else "?" + " | " + l)
            i += 1
        if conns:
            resultats.append(f"\nConnexions ({len(conns)}):")
            for c in conns[:10]:
                resultats.append(f"  {c}")
    except:
        pass

    return "\n".join(resultats)
