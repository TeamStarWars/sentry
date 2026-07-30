import os, subprocess, json, datetime

def timeline(chemin=".", profondeur=3):
    if not os.path.exists(chemin):
        return f"Chemin introuvable: {chemin}"
    resultats = []
    maintenant = datetime.datetime.now()
    try:
        fichiers = []
        for root, dirs, files in os.walk(chemin):
            niveau = root.replace(chemin, "").count(os.sep)
            if niveau > profondeur:
                dirs.clear()
                continue
            for f in files:
                fp = os.path.join(root, f)
                try:
                    mod = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
                    diff = (maintenant - mod).days
                    if diff <= 7:
                        fichiers.append((mod, fp, "modifie"))
                except:
                    pass
        fichiers.sort(reverse=True)
        resultats.append(f"Fichiers modifies (7 derniers jours): {len(fichiers)}")
        for mod, fp, action in fichiers[:20]:
            resultats.append(f"  [{mod.strftime('%Y-%m-%d %H:%M')}] {action}: {fp}")
    except:
        resultats.append("Erreur parcours")

    return "\n".join(resultats) if len(resultats) > 1 else "Aucun fichier recemment modifie"

def prefetch():
    try:
        prefetch_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Prefetch")
        if not os.path.isdir(prefetch_dir):
            return "Dossier Prefetch introuvable"
        fichiers = [f for f in os.listdir(prefetch_dir) if f.endswith(".pf") and not f.startswith(".")]
        fichiers.sort(key=lambda f: os.path.getmtime(os.path.join(prefetch_dir, f)), reverse=True)
        lignes = [f"Fichiers Prefetch: {len(fichiers)}"]
        for f in fichiers[:15]:
            fp = os.path.join(prefetch_dir, f)
            try:
                mod = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
                lignes.append(f"  {f} ({mod.strftime('%Y-%m-%d %H:%M')})")
            except:
                lignes.append(f"  {f}")
        return "\n".join(lignes)
    except Exception as e:
        return f"Erreur: {e}"

def recents():
    try:
        recent_dir = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Recent")
        if not os.path.isdir(recent_dir):
            return "Dossier Recent introuvable"
        fichiers = []
        for f in os.listdir(recent_dir):
            fp = os.path.join(recent_dir, f)
            try:
                mod = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
                fichiers.append((mod, f))
            except:
                pass
        fichiers.sort(reverse=True)
        lignes = [f"Fichiers recents: {len(fichiers)}"]
        for mod, f in fichiers[:15]:
            lignes.append(f"  [{mod.strftime('%Y-%m-%d %H:%M')}] {f.split('.lnk')[0]}")
        return "\n".join(lignes)
    except Exception as e:
        return f"Erreur: {e}"
