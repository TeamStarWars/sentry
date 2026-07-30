import re, hashlib, urllib.request

def analyser(mot_de_passe):
    score = 0
    details = []

    if len(mot_de_passe) >= 8: score += 15; details.append("Longueur >= 8 (+15)")
    if len(mot_de_passe) >= 12: score += 10; details.append("Longueur >= 12 (+10)")
    if len(mot_de_passe) >= 16: score += 10; details.append("Longueur >= 16 (+10)")
    if re.search(r"[a-z]", mot_de_passe): score += 10; details.append("Minuscule (+10)")
    if re.search(r"[A-Z]", mot_de_passe): score += 15; details.append("Majuscule (+15)")
    if re.search(r"\d", mot_de_passe): score += 10; details.append("Chiffre (+10)")
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",./<>?\\|`~]", mot_de_passe): score += 15; details.append("Special (+15)")
    if re.search(r"(.)\1{2,}", mot_de_passe): score -= 10; details.append("Repetition (-10)")
    if re.search(r"(123|abc|qwerty|password|admin|letmein)", mot_de_passe.lower()): score -= 20; details.append("Motif commun (-20)")
    if len(set(mot_de_passe)) < len(mot_de_passe) * 0.6: score -= 5; details.append("Peu de caracteres uniques (-5)")

    score = max(0, min(100, score))
    if score >= 80: force = "FORT"
    elif score >= 50: force = "MOYEN"
    else: force = "FAIBLE"

    return f"Mot de passe: {'*' * len(mot_de_passe)}\nScore: {score}/100 - {force}\n" + "\n".join(details)

def verifier_compromis(mot_de_passe):
    try:
        h = hashlib.sha1(mot_de_passe.encode()).hexdigest().upper()
        prefix, suffix = h[:5], h[5:]
        req = urllib.request.Request(f"https://api.pwnedpasswords.com/range/{prefix}")
        r = urllib.request.urlopen(req, timeout=10)
        hashes = r.read().decode().split("\r\n")
        for line in hashes:
            if line.startswith(suffix):
                count = int(line.split(":")[1])
                return f"COMPROMIS: trouve {count} fois dans les fuites de donnees!"
        return "Non trouve dans les bases de fuites (HaveIBeenPwned)"
    except:
        return "Verification compromis impossible (pas d'internet)"
