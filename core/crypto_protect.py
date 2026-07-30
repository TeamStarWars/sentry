import subprocess, json, os, time

PROCESSUS_CRYPTO = [
    "xmrig", "minerd", "ccminer", "ethminer", "claymore", "phoenixminer",
    "t-rex", "nbminer", "gminer", "lolminer", "teamredminer", "sgminer",
    "bfgminer", "cgminer", "cpuminer", "cpuminer-multi", "cryptonight",
    "xmr-stak", "xmr-stak-rx", "nanominer", "wildrig", "rigel",
    "srbminer", "trex", "excavator", "ewbf", "zm", "dstm",
    "kawpowminer", "bzminer", "ethlargement"
]

SITES_CONNUS = [
    "coin-hive.com", "coinhive.com", "crypto-loot.com", "coin-have.com",
    "jsecoin.com", "minero.cc", "statdynamic.com", "load.speedshiftcdn.com",
    "coinnebula.com", "coinblind.com", "afminer.com", "rexmas.com",
    "smartminers.org", "tiker.net", "ppoi.org", "dunfl.com"
]

def analyser_processus():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Select Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for p in data:
            if isinstance(p, dict):
                nom = p.get("Name", "").lower().replace(".exe", "")
                if nom in PROCESSUS_CRYPTO or any(k in nom for k in ["miner", "crypto", "coin", "xmr", "eth"]):
                    resultats.append(f"{p.get('Name','?')}.exe PID {p.get('Id')} CPU:{p.get('CPU',0):.1f}s RAM:{p.get('RAM_MB',0)}MB")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Sort CPU -Descending | Select -First 3 Name,Id,CPU | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for p in data:
            if isinstance(p, dict) and p.get("CPU", 0) > 500:
                resultats.append(f"CPU eleve suspect: {p.get('Name','?')}.exe CPU:{p.get('CPU',0):.1f}s")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_NetworkAdapterConfiguration | Where IPEnabled -eq True | Select Description,ServiceName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "netstat -bn 2>&1 | Select-String -Pattern 'pool','mine','xmr','eth','crypto','stratum'"],
            capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=10)
        if r.stdout.strip():
            resultats.append(f"Connexions minage detectees:\n{r.stdout.strip()[:500]}")
    except:
        pass

    if not resultats:
        return "Aucun processus de minage detecte"
    return "Crypto minage detecte:\n" + "\n".join(resultats)

def verifier_hosts():
    try:
        hosts = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
        with open(hosts, "r", encoding="utf-8", errors="replace") as f:
            contenu = f.read().lower()
        bloques = [s for s in SITES_CONNUS if s in contenu and "127.0.0.1" in contenu.split(s)[0][-20:] if s in contenu]
        if bloques:
            return f"Sites minage bloques dans hosts ({len(bloques)}): OK"
        return "Aucun blocage site minage dans hosts"
    except:
        return "Erreur lecture hosts"

def proteger_hosts():
    try:
        hosts = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
        with open(hosts, "r", encoding="utf-8") as f:
            lignes = f.readlines()
        deja = {l.strip().split()[-1] for l in lignes if l.strip() and not l.startswith("#") and len(l.strip().split()) > 1}
        nouvelles = []
        for s in SITES_CONNUS:
            if s not in deja:
                nouvelles.append(f"127.0.0.1 {s}")
        if nouvelles:
            with open(hosts, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(nouvelles))
            return f"{len(nouvelles)} sites minage bloques dans hosts"
        return "Tous les sites deja bloques"
    except PermissionError:
        return "Erreur: permission administrateur requise"
    except Exception as e:
        return f"Erreur: {e}"
