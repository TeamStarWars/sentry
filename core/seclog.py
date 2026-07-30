import os, datetime, json

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "vindex_alerts.json")

def ajouter_entree(categorie, message):
    entree = {
        "timestamp": str(datetime.datetime.now()),
        "categorie": categorie,
        "message": message
    }
    entrees = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                entrees = json.load(f)
        except:
            entrees = []
    entrees.append(entree)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entrees[-500:], f, indent=2, ensure_ascii=False)

def afficher(nb=20):
    if not os.path.exists(LOG_FILE):
        return "Aucune alerte enregistree"
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            entrees = json.load(f)
        if not entrees:
            return "Aucune alerte"
        lignes = []
        for e in entrees[-nb:]:
            t = str(e.get("timestamp", "?"))[:19]
            cat = e.get("categorie", "?")
            msg = str(e.get("message", ""))[:80]
            lignes.append(f"[{t}] {cat}: {msg}")
        return f"Alertes ({len(entrees)} totales):\n" + "\n".join(lignes)
    except:
        return "Erreur lecture journal"

def vider():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return "Journal vide"
