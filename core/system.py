import subprocess, json, os, platform


def diagnostic():
    try:
        infos = []
        infos.append(f"OS: {platform.system()} {platform.release()}")
        infos.append(f"Machine: {platform.node()}")
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_Processor | Select Name,NumberOfCores,MaxClockSpeed | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        cpu = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(cpu, dict):
            infos.append(f"CPU: {str(cpu.get('Name', '?'))[:50]} ({cpu.get('NumberOfCores', '?')} coeurs)")
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_ComputerSystem | Select TotalPhysicalMemory | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        ram = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(ram, dict):
            total_gb = round(int(ram.get('TotalPhysicalMemory', 0)) / (1024**3), 1)
            infos.append(f"RAM totale: {total_gb} Go")
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select DeviceID,Size,FreeSpace | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        disks = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(disks, dict): disks = [disks]
        for d in disks:
            if isinstance(d, dict):
                total = round(int(d.get('Size', 0)) / (1024**3), 1)
                free = round(int(d.get('FreeSpace', 0)) / (1024**3), 1)
                pct = round((free / total) * 100, 1) if total > 0 else 0
                infos.append(f"Disque {d.get('DeviceID', '?')}: {free}/{total} Go ({pct}% libre)")
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Select Days,Hours,Minutes | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        uptime = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(uptime, dict):
            infos.append(f"Uptime: {uptime.get('Days',0)}j {uptime.get('Hours',0)}h {uptime.get('Minutes',0)}m")
        return "\n".join(infos)
    except Exception as e:
        return f"Erreur diagnostic: {e}"

def disque(lecteur="C"):
    import re
    if not re.match(r"^[a-zA-Z]$", str(lecteur)):
        return "Lettre de lecteur invalide (ex: C)"
    try:
        path_expr = '{[math]::Round($_.FreeSpace/$_.Size*100,1)}'
        cmd = f"Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\"{lecteur.upper()}:\"' | Select DeviceID,Size,FreeSpace,@{'{'}N='PctFree';E={path_expr}{'}'} | ConvertTo-Json"
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=10)
        d = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(d, dict):
            total = round(int(d.get('Size', 0)) / (1024**3), 1)
            free = round(int(d.get('FreeSpace', 0)) / (1024**3), 1)
            pct = d.get('PctFree', 0)
            return f"Disque {lecteur}: {free}/{total} Go libre ({pct}%)"
        return f"Disque {lecteur}: introuvable"
    except Exception as e:
        return f"Erreur: {e}"

def memoire():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        m = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(m, dict):
            total = round(int(m.get('TotalVisibleMemorySize', 0)) / (1024*1024), 2)
            free = round(int(m.get('FreePhysicalMemory', 0)) / (1024*1024), 2)
            used = round(total - free, 2)
            pct = round((used / total) * 100, 1) if total > 0 else 0
            return f"RAM: {free}/{total} Go libre ({pct}% utilise)"
        return "Memoire: inconnue"
    except Exception as e:
        return f"Erreur: {e}"

def demarrage():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_StartupCommand | Select Name,Command,Location | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        items = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(items, dict): items = [items]
        if items:
            lignes = [f"{i.get('Name','?')}" for i in items if isinstance(i, dict)]
            return f"Programmes au demarrage ({len(lignes)}):\n" + "\n".join(lignes[:10])
        return "Aucun programme au demarrage"
    except Exception as e:
        return f"Erreur: {e}"

def services():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Service | Where Status -eq Running | Select Name,DisplayName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        items = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(items, dict): items = [items]
        return f"Services actifs: {len(items)}"
    except Exception as e:
        return f"Erreur: {e}"

def ip_publique():
    import urllib.request
    try:
        r = urllib.request.urlopen("https://api.ipify.org?format=json", timeout=10)
        data = json.loads(r.read().decode())
        return f"IP publique: {data.get('ip', '?')}"
    except:
        try:
            r = urllib.request.urlopen("https://httpbin.org/ip", timeout=10)
            data = json.loads(r.read().decode())
            return f"IP publique: {data.get('origin', '?')}"
        except:
            return "Erreur IP publique"

def ip_locale():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"IP locale: {ip}"
    except:
        return "IP locale: inconnue"