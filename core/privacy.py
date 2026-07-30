import subprocess, json, os, ctypes

def webcam_check():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_PnPEntity | Where {$_.PNPClass -eq 'Camera' -or $_.PNPClass -eq 'Image'} | Select Name,Status,PNPClass | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Peripheriques video ({len(data)}):"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('Name','?')} - {d.get('Status','?')}")
            return "\n".join(lignes)
        return "Aucune camera detectee"
    except Exception as e:
        return f"Erreur: {e}"

def microphone_check():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_PnPEntity | Where {$_.PNPClass -eq 'AudioEndpoint' -or $_.PNPClass -eq 'Media'} | Select Name,Status | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Peripheriques audio ({len(data)}):"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('Name','?')} - {d.get('Status','?')}")
            return "\n".join(lignes)
        return "Aucun microphone detecte"
    except Exception as e:
        return f"Erreur: {e}"

def processus_camera():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Where Name -match 'camera|webcam|video|droidcam|obs|zoom|skype|teams|discord|slack|whatsapp' | Select Name,Id | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = ["Processus utilisant camera/audio:"]
            for p in data:
                if isinstance(p, dict):
                    lignes.append(f"  {p.get('Name','?')}.exe PID {p.get('Id')}")
            return "\n".join(lignes)
        return "Aucun processus camera detecte"
    except:
        return "Erreur analyse processus"

def tracker_check():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem \"$env:APPDATA\\..\\Local\\Google\\Chrome\\User Data\\Default\\Cookies\" -ErrorAction SilentlyContinue | Select Length | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        taille = data.get("Length", 0) if isinstance(data, dict) else 0
        if taille and int(taille) > 100000:
            resultats.append(f"Cookies Chrome: {round(int(taille)/1024)}KB")
    except:
        pass

    try:
        hosts = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
        if os.path.isfile(hosts):
            with open(hosts, "r", encoding="utf-8", errors="replace") as f:
                contenu = f.read()
            trackers = ["doubleclick", "google-analytics", "facebook.com/tr", "amazon-adsystem",
                        "scorecardresearch", "quantserve", "adzerk", "bluekai", "exelator", "outbrain"]
            bloques = [t for t in trackers if t in contenu.lower()]
            if bloques:
                resultats.append(f"Trackers bloques dans hosts: {len(bloques)}")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name Enabled -ErrorAction SilentlyContinue | Select Enabled | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(data, dict) and data.get("Enabled"):
            resultats.append("Publicite personnalisee: ACTIVEE")
    except:
        pass

    if not resultats:
        return "Aucun tracker majeur detecte"
    return "Analyse traqueurs:\n" + "\n".join(resultats)

def desactiver_pub():
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name Enabled -Value 0 -Type DWord -ErrorAction SilentlyContinue"],
            capture_output=True, text=True, timeout=10)
        return "Publicite personnalisee desactivee"
    except Exception as e:
        return f"Erreur: {e}"
