import hashlib, json, urllib.request, os

API_KEY = ""

def configurer_cle(cle):
    global API_KEY
    API_KEY = cle
    return "Cle API VirusTotal configuree"

def analyser(chemin):
    if not os.path.isfile(chemin):
        return "Fichier introuvable"
    try:
        h = hashlib.sha256()
        with open(chemin, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        sha256 = h.hexdigest()
        nom = os.path.basename(chemin)

        if not API_KEY:
            return f"{nom} (SHA256: {sha256})\n[Aucune cle API - utilisez 'vt-cle <cle>' pour activer]"

        req = urllib.request.Request(
            f"https://www.virustotal.com/api/v3/files/{sha256}",
            headers={"x-apikey": API_KEY}
        )
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read().decode())
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        if stats:
            mal = stats.get("malicious", 0)
            total = sum(stats.values())
            return f"{nom}: {mal}/{total} detecteurs malveillants"
        return f"{nom}: aucun resultat"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"{nom}: fichier inconnu sur VirusTotal"
        return f"Erreur API: {e.code}"
    except Exception as e:
        return f"Erreur: {e}"
