import os, re, json

REGLE_SPAM = [
    (r"\b(congratulation|winner|won|lottery|prize|jackpot)\b", 10, "Lotterie/prize"),
    (r"\b(bitcoin|btc|crypto|wallet|investment|profit|earn money)\b", 8, "Crypto/investissement"),
    (r"\b(urgent|immediate action|act now|limited time|expires today)\b", 7, "Urgence"),
    (r"\b(password|verify|confirm|account.*suspend|security.*alert)\b", 9, "Phishing"),
    (r"\b(viagra|cialis|pharmacy|medication|prescription)\b", 8, "Pharma/spam"),
    (r"\b(click here|free|subscribe|unsubscribe|click below)\b", 5, "Marketing"),
    (r"\b(inheritance|funds|transfer|western union|money gram)\b", 10, "Arnaque financiere"),
    (r"\b(doctor|diagnosis|cure|treatment|miracle|guaranteed)\b", 6, "Spam sante"),
]

def analyser_texte(texte):
    score = 0
    raisons = []
    texte_lower = texte.lower()
    for pattern, pts, raison in REGLE_SPAM:
        if re.search(pattern, texte_lower):
            score += pts
            raisons.append(f"{raison} (+{pts})")
    return score, raisons

def analyser_email(eml_path):
    if not os.path.isfile(eml_path):
        return "Fichier introuvable"
    try:
        with open(eml_path, "r", encoding="utf-8", errors="replace") as f:
            contenu = f.read()
        sujet = ""
        for line in contenu.split("\n"):
            if line.lower().startswith("subject:"):
                sujet = line[8:].strip()
                break
        score, raisons = analyser_texte(sujet + " " + contenu[:2000])
        verdict = "SPAM" if score >= 20 else ("SUSPECT" if score >= 10 else "SAIN")
        lignes = [f"Analyse: {os.path.basename(eml_path)}",
                  f"Sujet: {sujet}",
                  f"Score: {score}/100 - {verdict}"]
        if raisons:
            lignes.append(f"Raisons: {', '.join(raisons)}")
        return "\n".join(lignes)
    except Exception as e:
        return f"Erreur: {e}"

def analyser_texte_libre(texte):
    score, raisons = analyser_texte(texte)
    verdict = "SPAM" if score >= 20 else ("SUSPECT" if score >= 10 else "SAIN")
    lignes = [f"Score: {score}/100 - {verdict}"]
    if raisons:
        lignes.append(f"Raisons: {', '.join(raisons)}")
    return "\n".join(lignes)
