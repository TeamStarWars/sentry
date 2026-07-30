import subprocess, json, os, datetime, socket, urllib.request

def localiser():
    resultats = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_locale = s.getsockname()[0]
        s.close()
        resultats.append(f"IP locale: {ip_locale}")
    except:
        resultats.append("IP locale: inconnue")

    try:
        r = urllib.request.urlopen("https://ipapi.co/json/", timeout=10)
        data = json.loads(r.read().decode())
        if isinstance(data, dict):
            resultats.append(f"IP publique: {data.get('ip','?')}")
            resultats.append(f"Fai: {data.get('org','?')}")
            resultats.append(f"Ville: {data.get('city','?')}, {data.get('country_name','?')}")
            lat = data.get("latitude")
            lon = data.get("longitude")
            if lat and lon:
                resultats.append(f"Geo: {lat}, {lon}")
                resultats.append(f"https://www.google.com/maps?q={lat},{lon}")
    except:
        try:
            r = urllib.request.urlopen("https://httpbin.org/ip", timeout=10)
            data = json.loads(r.read().decode())
            resultats.append(f"IP publique: {data.get('origin','?')}")
        except:
            resultats.append("IP publique: inconnue")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_ComputerSystem | Select Name,Manufacturer,Model | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        sysinfo = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(sysinfo, dict):
            resultats.append(f"Machine: {sysinfo.get('Manufacturer','?')} {sysinfo.get('Model','?')}")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_BIOS | Select SerialNumber | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        bios = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(bios, dict) and bios.get("SerialNumber"):
            resultats.append(f"SN: {bios.get('SerialNumber')}")
    except:
        pass

    return "Localisation:\n" + "\n".join(resultats)

def verrouiller():
    try:
        r = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"],
            capture_output=True, text=True, timeout=5)
        return "Poste verrouille"
    except Exception as e:
        return f"Erreur: {e}"

def alerte_sonore():
    for _ in range(3):
        try:
            import ctypes
            ctypes.windll.kernel32.Beep(800, 300)
        except:
            pass
    return "Alerte sonore declenchee"
