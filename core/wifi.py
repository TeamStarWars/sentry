import subprocess, json, re
ENC = "cp1252"
ERR = "replace"

def wifi_reseaux():
    try:
        r = subprocess.run(["netsh", "wlan", "show", "networks", "mode=Bssid"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
        ssids = re.findall(r"SSID\s+\d+\s+:\s(.+)", r.stdout)
        signaux = re.findall(r"Signal\s+:\s(\d+)%", r.stdout)
        if not ssids:
            return "Aucun reseau WiFi trouve"
        lignes = []
        for i, ssid in enumerate(ssids):
            sig = signaux[i] if i < len(signaux) else "?"
            lignes.append(f"{ssid.strip()} ({sig}%)")
        return f"Reseaux WiFi ({len(lignes)}):\n" + "\n".join(lignes[:15])
    except Exception as e:
        return f"Erreur wifi: {e}"

def wifi_profil():
    try:
        r = subprocess.run(["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
        profils = re.findall(r"Profil Tous les utilisateurs\s+:\s(.+)", r.stdout)
        if not profils:
            return "Aucun profil WiFi"
        return f"Profils WiFi ({len(profils)}):\n" + "\n".join(p.strip() for p in profils)
    except Exception as e:
        return f"Erreur profil: {e}"

def wifi_mdp(nom=None):
    try:
        if nom:
            r = subprocess.run(["netsh", "wlan", "show", "profile", f"name={nom}", "key=clear"],
                capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
            mdp = re.search(r"Contenu de la cle\s+:\s(.+)", r.stdout)
            if mdp:
                return f"WiFi {nom}: mot de passe = {mdp.group(1).strip()}"
            return f"WiFi {nom}: mot de passe non trouve"
        r = subprocess.run(["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
        profils = re.findall(r"Profil Tous les utilisateurs\s+:\s(.+)", r.stdout)
        resultats = []
        for p in profils[:5]:
            p = p.strip()
            r2 = subprocess.run(["netsh", "wlan", "show", "profile", f"name={p}", "key=clear"],
                capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
            mdp = re.search(r"Contenu de la cle\s+:\s(.+)", r2.stdout)
            resultats.append(f"{p}: {mdp.group(1).strip() if mdp else '?'}")
        return "\n".join(resultats) if resultats else "Aucun profil"
    except Exception as e:
        return f"Erreur mdp: {e}"

def wifi_interface():
    try:
        r = subprocess.run(["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, encoding=ENC, errors=ERR, timeout=15)
        lignes = [l.strip() for l in r.stdout.split("\n") if ":" in l and l.strip()]
        infos = [l for l in lignes if any(k in l for k in ["SSID", "Etat", "Signal", "Type", "BSSID"])]
        return "\n".join(infos[:10]) if infos else "Aucune interface WiFi"
    except Exception as e:
        return f"Erreur interface: {e}"