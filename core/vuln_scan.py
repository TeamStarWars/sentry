import subprocess, json

def scanner():
    resultats = []

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance -ClassName Win32_QuickFixEngineering | Measure-Object | Select Count | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        nb = data.get("Count", 0) if isinstance(data, dict) else 0
        resultats.append(f"Correctifs installes: {nb}")
        if nb < 50:
            resultats.append("  ATTENTION: moins de 50 correctifs, systeme risque")
        elif nb < 100:
            resultats.append("  Correctif: nombre moyen")
        else:
            resultats.append("  Correctif: bonne couverture")
    except:
        resultats.append("Correctifs: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Service | Where Status -eq Running | Select Name,DisplayName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        services_risques = []
        for s in data:
            if isinstance(s, dict):
                nom = (s.get("Name", "") + " " + s.get("DisplayName", "")).lower()
                if any(r in nom for r in ["telnet", "ftp", "sshd", "rlogin", "rsh"]):
                    services_risques.append(s.get("Name", "?"))
        if services_risques:
            resultats.append(f"Services a risque actifs: {', '.join(services_risques)}")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetFirewallProfile | Select Name,Enabled | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for p in data:
            if isinstance(p, dict) and not p.get("Enabled"):
                resultats.append(f"FW {p.get('Name','?')}: DESACTIVE")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_OperatingSystem | Select BuildNumber,Version | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        os_info = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(os_info, dict):
            build = os_info.get("BuildNumber", "")
            try:
                if int(build) < 19045:
                    resultats.append(f"Build {build}: version anterieure a Windows 10 22H2")
            except:
                pass
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WindowsOptionalFeature -Online -ErrorAction SilentlyContinue | Where State -eq Enabled | Select FeatureName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        features_risques = ["SMB1Protocol", "TelnetClient", "TFTP", "SimpleTCP"]
        for f in data:
            if isinstance(f, dict) and f.get("FeatureName") in features_risques:
                resultats.append(f"Fonctionnalite risque activee: {f.get('FeatureName')}")
    except:
        pass

    if len(resultats) <= 1:
        resultats.append("Aucune vulnerabilite majeure detectee")

    return "Scan vulnerabilites:\n" + "\n".join(resultats)
