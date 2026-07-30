import subprocess, json

def lister():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WmiObject -Class Win32_QuickFixEngineering | Select HotFixID,InstalledOn,Description | Sort InstalledOn -Descending | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Total: {len(data)} mises a jour\n"]
            for d in data[:20]:
                if isinstance(d, dict):
                    lignes.append(f"{d.get('HotFixID','?')} - {d.get('InstalledOn','?')} - {str(d.get('Description',''))[:50]}")
            return "\n".join(lignes)
        return "Aucune mise a jour trouvee"
    except Exception as e:
        return f"Erreur: {e}"

def rechercher():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WinEvent -LogName Setup -MaxEvents 20 -ErrorAction SilentlyContinue | Where Id -eq 1 | Select TimeCreated,Message | ConvertTo-Json"],
            capture_output=True, text=True, timeout=20)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = ["Dernieres installations Windows:"]
            for d in data[:10]:
                if isinstance(d, dict):
                    msg = str(d.get("Message", ""))[:80]
                    lignes.append(f"  {str(d.get('TimeCreated','?'))[:19]} - {msg}")
            return "\n".join(lignes)
        return "Aucun evenement d'installation"
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WindowsUpdate -ErrorAction SilentlyContinue | Select Title,KBArticleID | ConvertTo-Json"],
            capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Mises a jour en attente: {len(data)}"]
            for d in data[:10]:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('Title','?')[:80]}")
            return "\n".join(lignes)
        return "Systeme a jour"
    except:
        return "Module WindowsUpdate non disponible"
