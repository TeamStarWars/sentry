import subprocess, os, json
from core.safe import esc

def shadow_copies():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance -ClassName Win32_ShadowCopy | Select ID,InstallDate,Volume | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Copies shadow disponibles ({len(data)}):"]
            for s in data[:10]:
                if isinstance(s, dict):
                    lignes.append(f"  Volume: {s.get('Volume','?')} - {str(s.get('InstallDate','?'))[:19]}")
            return "\n".join(lignes)
        return "Aucune copie shadow"
    except Exception as e:
        return f"Erreur: {e}"

def restaurer_shadow():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance -ClassName Win32_ShadowCopy | Sort InstallDate -Descending | Select -First 1 | ForEach-Object { $_.DeviceObject + ' -> ' + $_.ID }"],
            capture_output=True, text=True, timeout=15)
        shadow = r.stdout.strip()
        if shadow:
            return f"Derniere copie shadow: {shadow}\nUtilisez 'vssadmin list shadows' pour plus de details"
        return "Aucune copie shadow disponible"
    except Exception as e:
        return f"Erreur: {e}"

def activer_protection():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Enable-ComputerRestore -Drive 'C:\\' -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=10)
        return "Protection restauration activee sur C:"
    except Exception as e:
        return f"Erreur: {e}"

def fs_scan_extensions(path="C:\\Users"):
    extensions_ransom = [".lockbit", ".encrypted", ".crypted", ".locked", ".onion", ".ezz"]
    total = 0
    for ext in extensions_ransom:
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                f"Get-ChildItem '{esc(path)}' -Recurse -ErrorAction SilentlyContinue -Filter '*{ext}' | Measure-Object | Select Count | ConvertTo-Json"],
                capture_output=True, text=True, timeout=30)
            data = json.loads(r.stdout) if r.stdout.strip() else {}
            c = data.get("Count", 0) if isinstance(data, dict) else 0
            total += c
        except:
            pass
    if total > 0:
        return f"ALERTE: {total} fichiers avec extensions rancon trouvees"
    return "Aucun fichier rancon dans le systeme"
