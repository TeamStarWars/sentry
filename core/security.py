import json, os
from core.safe import esc, valider_port

def analyser_signe(chemin):
    import subprocess
    if not os.path.isfile(chemin):
        return "Fichier introuvable"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-AuthenticodeSignature -FilePath '{esc(chemin)}' | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        if isinstance(data, dict):
            status = data.get("Status", "Inconnu")
            cert = data.get("SignerCertificate", {})
            subject = cert.get("Subject", "Non signe") if isinstance(cert, dict) else "Non signe"
            return f"Signature: {status}\nSignataire: {subject}"
        return "Aucune signature"
    except:
        return "Erreur signature"

def ports_ecoute():
    import subprocess
    try:
        r = subprocess.run(["netstat", "-an"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=10)
        lignes = [l.strip() for l in r.stdout.split("\n") if "LISTENING" in l or "LISTEN" in l]
        ports = []
        for l in lignes[:20]:
            parts = l.split()
            if len(parts) >= 4:
                pid = parts[-1] if parts[-1].isdigit() else "?"
                ports.append(f"{parts[1]} (PID {pid})")
        return f"Ports ecoute ({len(lignes)}):\n" + "\n".join(ports) if ports else "Aucun"
    except:
        return "Erreur ports"

def regle_firewall():
    import subprocess
    try:
        r = subprocess.run(["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
            capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=30)
        lignes = [l.strip() for l in r.stdout.split("\n") if "Rule Name:" in l]
        return f"Regles FW: {len(lignes)}\n" + "\n".join(lignes[:10]) if lignes else "Aucune regle"
    except:
        return "Erreur firewall"

def verifier_port(port):
    import socket
    p = valider_port(port)
    if not p:
        return "Port invalide (1-65535)"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        r = s.connect_ex(("127.0.0.1", p))
        s.close()
        return f"Port {p}: {'OUVERT' if r == 0 else 'FERME'}"
    except:
        return "Erreur verification"

def whitelist_ajouter(chemin):
    import subprocess
    if not os.path.exists(chemin):
        return "Chemin introuvable"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Add-MpPreference -ExclusionPath '{esc(chemin)}'"],
            capture_output=True, text=True, timeout=10)
        return f"{os.path.basename(chemin)} ajoute aux exclusions"
    except:
        return "Erreur whitelist"

def whitelist_liste():
    import subprocess
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-MpPreference | Select -ExpandProperty ExclusionPath"],
            capture_output=True, text=True, timeout=10)
        chemins = [l.strip() for l in r.stdout.split("\n") if l.strip() and l.strip() != "[]"]
        return "Exclusions:\n" + "\n".join(chemins) if chemins else "Aucune exclusion"
    except:
        return "Erreur whitelist"
