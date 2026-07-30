import subprocess, os, hashlib, json
from core.safe import esc, valider_chemin

def scanner_chemin(chemin):
    chemin_valide = valider_chemin(chemin)
    if not chemin_valide or not os.path.exists(chemin_valide):
        return "Chemin invalide ou introuvable"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Start-MpScan -ScanType CustomScan -ScanPath '{esc(chemin_valide)}'"],
            capture_output=True, text=True, timeout=300)
        out = r.stdout + r.stderr
        if "Threat" in out or "menace" in out.lower():
            return f"Menace detectee dans {os.path.basename(chemin_valide)}"
        return f"Scan termine: {os.path.basename(chemin_valide)}"
    except subprocess.TimeoutExpired:
        return "Scan interrompu (trop long)"
    except:
        return "Erreur scan"

def analyser_processus():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Where { $_.CPU -gt 50 -or $_.WorkingSet -gt 500MB } | Select Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if not isinstance(data, list): data = [data]
        if data:
            lignes = []
            for p in data:
                if isinstance(p, dict):
                    lignes.append(f"{p['Name']} (PID {p['Id']}) - CPU: {p.get('CPU',0):.1f}s, RAM: {p.get('RAM_MB',0)}MB")
            return "Processus consommateurs:\n" + "\n".join(lignes[:10])
        return "Aucun processus suspect"
    except:
        return "Erreur analyse"

def hash_fichier(chemin):
    chemin_valide = valider_chemin(chemin)
    if not chemin_valide or not os.path.isfile(chemin_valide):
        return "Fichier introuvable"
    try:
        h_md5 = hashlib.md5()
        h_sha1 = hashlib.sha1()
        h_sha256 = hashlib.sha256()
        with open(chemin_valide, "rb") as f:
            while chunk := f.read(8192):
                h_md5.update(chunk)
                h_sha1.update(chunk)
                h_sha256.update(chunk)
        nom = os.path.basename(chemin_valide)
        return f"Hash {nom}:\nMD5: {h_md5.hexdigest()}\nSHA1: {h_sha1.hexdigest()[:40]}\nSHA256: {h_sha256.hexdigest()[:64]}"
    except:
        return "Erreur hash"

def demarrer_defenseur():
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            "Start-MpWDOScan"], capture_output=True, text=True, timeout=10)
        return "Scan Defender hors-ligne lance (au prochain demarrage)"
    except:
        pass
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Start-MpScan -ScanType FullScan"], capture_output=True, text=True, timeout=10)
        return "Scan complet Defender lance"
    except:
        return "Erreur Defender"

def statut_defenseur():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-MpComputerStatus | Select AMProductVersion,AMServiceEnabled,AntispywareEnabled,RealTimeProtectionEnabled | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        if data:
            etat = "ACTIF" if data.get("RealTimeProtectionEnabled") else "INACTIF"
            return f"Windows Defender: {etat} (v{data.get('AMProductVersion','?')})"
        return "Windows Defender: inconnu"
    except:
        return "Erreur Defender"
