import os, hashlib, shutil, tempfile, json, base64, subprocess, re
from core.safe import esc

_WARN = "AVERTISSEMENT: Chiffrement XOR basique - NE CONVIENT PAS pour donnees sensibles"

def chiffrer_fichier(chemin):
    if not os.path.isfile(chemin):
        return "Fichier introuvable"
    try:
        with open(chemin, "rb") as f:
            data = f.read()
        key = hashlib.sha256(os.urandom(32)).digest()
        encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
        nom_sortie = chemin + ".sentry"
        with open(nom_sortie, "wb") as f:
            f.write(key[:16])
            f.write(encrypted)
        os.remove(chemin)
        return f"{_WARN}\nChiffre: {os.path.basename(chemin)} -> {os.path.basename(nom_sortie)}"
    except:
        return "Erreur chiffrement"

def dechiffrer_fichier(chemin):
    if not os.path.isfile(chemin) or not chemin.endswith(".sentry"):
        return "Fichier .sentry introuvable"
    try:
        with open(chemin, "rb") as f:
            key = f.read(16)
            encrypted = f.read()
        key = key * (len(encrypted) // 16 + 1)
        key = key[:len(encrypted)]
        decrypted = bytes([encrypted[i] ^ key[i] for i in range(len(encrypted))])
        nom_sortie = chemin.replace(".sentry", "")
        with open(nom_sortie, "wb") as f:
            f.write(decrypted)
        os.remove(chemin)
        return f"{_WARN}\nDechiffre: {os.path.basename(chemin)} -> {os.path.basename(nom_sortie)}"
    except:
        return "Erreur dechiffrement"

def effacer_fichier(chemin, passes=3):
    if not os.path.isfile(chemin):
        return "Fichier introuvable"
    try:
        taille = os.path.getsize(chemin)
        for p in range(passes):
            with open(chemin, "wb") as f:
                pattern = bytes([0xFF if p % 2 == 0 else 0x00] * 1024)
                written = 0
                while written < taille:
                    f.write(pattern[:min(1024, taille - written)])
                    written += 1024
        os.remove(chemin)
        return f"Efface: {os.path.basename(chemin)} ({passes} passes)"
    except:
        return "Erreur effacement"

def verifier_permissions(chemin):
    if not os.path.exists(chemin):
        return "Chemin introuvable"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-Acl '{esc(chemin)}' | Select -ExpandProperty Access | Select IdentityReference,FileSystemRights | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Permissions: {os.path.basename(chemin)}"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('IdentityReference','?')} - {d.get('FileSystemRights','?')}")
            return "\n".join(lignes)
        return "Aucune permission"
    except:
        return "Erreur permissions"
