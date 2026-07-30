"""Module de securite central — sanitization, validation, hardening"""

import re, os, html as _html

def esc(valeur):
    """Echappe une valeur pour PowerShell (doublage des quotes)"""
    if not isinstance(valeur, str):
        valeur = str(valeur)
    return valeur.replace("'", "''")

def valider_port(port):
    """Valide et retourne un port valide (1-65535)"""
    try:
        p = int(port)
        if 1 <= p <= 65535:
            return p
    except (ValueError, TypeError):
        pass
    return None

def valider_pid(pid):
    """Valide et retourne un PID valide (>0)"""
    try:
        p = int(pid)
        if p > 0:
            return p
    except (ValueError, TypeError):
        pass
    return None

def valider_ip(ip):
    """Valide une adresse IP v4"""
    pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(p) <= 255 for p in parts)

def valider_chemin(chemin):
    """Valide et securise un chemin (interdit .. et caracteres nuls)"""
    if not isinstance(chemin, str):
        return None
    if "\0" in chemin:
        return None
    if ".." in chemin.split(os.sep):
        return None
    return os.path.normpath(chemin)

def sanitize_html(texte):
    """Echappe les caracteres HTML pour empecher XSS"""
    if not isinstance(texte, str):
        texte = str(texte)
    return _html.escape(texte, quote=True)

def masquer_chemin(chemin):
    """Masque les chemins sensibles dans les logs"""
    sensibles = ["password", "token", "secret", "key", "mdp", "motdepasse"]
    for s in sensibles:
        if s in chemin.lower():
            return "***MASQUE***"
    return chemin

def coffre_fort(chemin):
    """Verifie que le fichier est dans une zone autorisee"""
    zones_autorisees = [
        os.path.expandvars("%TEMP%"),
        os.path.expandvars("%USERPROFILE%"),
        os.path.expandvars("%PUBLIC%"),
        "C:\\Users",
        "D:\\",
    ]
    try:
        chemin_abs = os.path.abspath(chemin)
        for zone in zones_autorisees:
            zone_abs = os.path.abspath(os.path.expandvars(zone))
            if chemin_abs.lower().startswith(zone_abs.lower()):
                return True
    except:
        pass
    return False

def generateur_motdepasse(longueur=20):
    """Genere un mot de passe securise"""
    import secrets, string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(chars) for _ in range(longueur))

def verifier_integrite_fichier(chemin):
    """Verifie l'integrite SHA-256 d'un fichier"""
    import hashlib
    try:
        h = hashlib.sha256()
        with open(chemin, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None
