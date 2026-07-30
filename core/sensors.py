import subprocess, json

def temperatures():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_PerfFormattedData_Counters_ThermalZoneInformation -ErrorAction SilentlyContinue | Select Name,Temperature | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for d in data:
            if isinstance(d, dict):
                temp = d.get("Temperature", 0)
                if temp:
                    temp_c = temp / 10.0
                    resultats.append(f"{d.get('Name','?')}: {temp_c:.1f}C")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace root/wmi -ErrorAction SilentlyContinue | Select InstanceName,Temperature | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for d in data:
            if isinstance(d, dict):
                temp = d.get("Temperature", 0)
                if temp:
                    temp_c = (temp - 2732) / 10.0
                    resultats.append(f"{d.get('InstanceName','?')}: {temp_c:.1f}C")
    except:
        pass

    if not resultats:
        return "Capteurs de temperature non disponibles"
    return "Temperatures:\n" + "\n".join(resultats)

def ventilateurs():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_Fan -ErrorAction SilentlyContinue | Select Name,DesiredSpeed | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = ["Ventilateurs:"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('Name','?')}: {d.get('DesiredSpeed','?')} RPM")
            return "\n".join(lignes)
        return "Aucun ventilateur detecte"
    except:
        return "Erreur ventilateurs"
