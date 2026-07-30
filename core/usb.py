import subprocess, json

def historique():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-DriverFrameworks-UserMode/Operational'; ID=2003,2004,2006,2100} -MaxEvents 50 -ErrorAction SilentlyContinue | Select TimeCreated,Id,Message | ConvertTo-Json"],
            capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = []
            for e in data[:30]:
                if isinstance(e, dict):
                    t = str(e.get("TimeCreated", "?"))[:19]
                    mid = e.get("Id", "?")
                    msg = str(e.get("Message", ""))[:100]
                    if mid == 2003:
                        lignes.append(f"[{t}] CONNECTE: {msg}")
                    elif mid == 2004:
                        lignes.append(f"[{t}] DEBRANCHE: {msg}")
                    elif mid == 2100:
                        lignes.append(f"[{t}] RECONNU: {msg}")
            if lignes:
                return "Historique USB:\n" + "\n".join(lignes[:20])
        return "Aucun evenement USB trouve"
    except Exception as e:
        return f"Erreur USB: {e}"

def peripheriques():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-PnpDevice | Where {$_.Class -eq 'USB' -or $_.Class -eq 'HIDClass'} | Select FriendlyName,Class,Status,InstanceId | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = []
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"{d.get('FriendlyName','?')} [{d.get('Status','?')}]")
            return f"Peripheriques USB ({len(lignes)}):\n" + "\n".join(lignes)
        return "Aucun peripherique USB"
    except Exception as e:
        return f"Erreur: {e}"
