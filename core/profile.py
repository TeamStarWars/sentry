import json, os, datetime

PROFILE_FILE = os.path.join(os.path.dirname(__file__), "..", "sentry_profile.json")

def sauvegarder(nom="default"):
    profile = {
        "nom": nom,
        "date": str(datetime.datetime.now()),
        "version": "2.0",
        "protecteur": False,
        "firewall_mode": "normal",
        "dns_securise": False,
        "minage_bloque": False,
        "safe_pay": False
    }
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    return f"Profil '{nom}' sauvegarde"

def charger(nom="default"):
    if not os.path.exists(PROFILE_FILE):
        return "Aucun profil trouve"
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        if profile.get("nom") == nom or nom == "default":
            lignes = ["Profil actuel:"]
            for k, v in profile.items():
                lignes.append(f"  {k}: {v}")
            return "\n".join(lignes)
        return f"Profil '{nom}' introuvable"
    except Exception as e:
        return f"Erreur: {e}"

def appliquer_securite_max():
    from core import firewall_adv, protector, crypto_protect, web_protect, seclog
    resultats = []
    resultats.append(firewall_adv.mode_strict())
    resultats.append(protector.demarrer())
    resultats.append(crypto_protect.proteger_hosts())
    resultats.append(web_protect.proteger_dns())
    seclog.ajouter_entree("PROFILE", "Profil securite max applique")
    return "\n".join(resultats)

def appliquer_privacy():
    from core import privacy, firewall_adv, web_protect, protector
    resultats = []
    resultats.append(privacy.desactiver_pub())
    resultats.append(web_protect.proteger_dns())
    resultats.append(firewall_adv.mode_strict())
    return "Mode prive:\n" + "\n".join(resultats)
