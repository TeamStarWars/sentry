import subprocess, json, os, winreg

def scanner():
    points = []

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_StartupCommand | Select Name,Command,Location | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for d in data:
            if isinstance(d, dict):
                points.append(f"Demarrage: {d.get('Name','?')} -> {d.get('Command','?')} [{d.get('Location','?')}]")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ScheduledTask | Where State -eq Ready | Select TaskName,TaskPath,TasksPath | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for d in data:
            if isinstance(d, dict):
                points.append(f"Tache planifiee: {d.get('TaskName','?')}")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Service | Where StartType -eq Auto | Select Name,DisplayName,Status | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        services_anormaux = [d for d in data if isinstance(d, dict) and not d.get('DisplayName','').startswith('Windows')]
        for s in services_anormaux:
            points.append(f"Service auto: {s.get('Name','?')} ({s.get('DisplayName','?')})")
    except:
        pass

    try:
        regs = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs"),
        ]
        for hkey, chemin in regs:
            try:
                key = winreg.OpenKey(hkey, chemin)
                i = 0
                while True:
                    try:
                        nom, valeur, _ = winreg.EnumValue(key, i)
                        points.append(f"Registre: {chemin} -> {nom} = {valeur}")
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except:
                pass
    except:
        pass

    if not points:
        return "Aucun point de persistence detecte"
    return f"Points de persistence ({len(points)}):\n" + "\n".join(points[:30])
