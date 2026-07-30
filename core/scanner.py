import os

EXT_SUSPECTES = [".exe", ".ps1", ".vbs", ".bat", ".cmd", ".jar", ".dll", ".scr", ".com", ".pif", ".js", ".wsf", ".vbe", ".msi"]

def fichiers_suspects(chemin, profondeur=2):
    if not os.path.exists(chemin):
        return f"Chemin introuvable: {chemin}"
    try:
        trouves = []
        for root, dirs, files in os.walk(chemin):
            niveau = root.replace(chemin, "").count(os.sep)
            if niveau > profondeur:
                dirs.clear()
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in EXT_SUSPECTES:
                    trouves.append(os.path.join(root, f))
        if trouves:
            return f"Fichiers suspects ({len(trouves)}):\n" + "\n".join(trouves[:30])
        return "Aucun fichier suspect trouve"
    except Exception as e:
        return f"Erreur: {e}"

def extensible_par_type():
    return "Extensions surveillees: " + ", ".join(EXT_SUSPECTES)
