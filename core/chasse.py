import subprocess, json, os, glob

def ransomware_check(chemin="."):
    if not os.path.exists(chemin):
        return f"Chemin introuvable: {chemin}"
    resultats = []

    extensions_ransom = [
        ".lockbit", ".encrypted", ".enc", ".crypted", ".locked", ".onion",
        ".ezz", ".exx", ".xyz", ".abc", ".zzz", ".aaa",
        ".pay", ".money", ".btc", ".bitcoin", ".wannacry", ".petya",
        ".cry", ".cryp", ".crypt", ".cryptolocker", ".torrent", ".leaks"
    ]
    fichiers_ransom = []
    for ext in extensions_ransom:
        fichiers_ransom.extend(glob.glob(os.path.join(chemin, f"**/*{ext}"), recursive=True))

    if fichiers_ransom:
        resultats.append(f"Extensions rancon detectees ({len(fichiers_ransom)})!")
        for f in fichiers_ransom[:10]:
            resultats.append(f"  {f}")
        if len(fichiers_ransom) > 10:
            resultats.append(f"  ... et {len(fichiers_ransom)-10} autres")

    notes_rclami = []
    for p in [os.path.join(chemin, "**/README*.txt"),
              os.path.join(chemin, "**/DECRYPT*.txt"),
              os.path.join(chemin, "**/HOW_TO_DECRYPT*")]:
        notes_rclami.extend(glob.glob(p, recursive=True))
    for note in notes_rclami[:5]:
        try:
            with open(note, "r", errors="replace") as f:
                contenu = f.read(200).lower()
            if any(w in contenu for w in ["bitcoin", "decrypt", "ransom", "pay", "btc", "wallet"]):
                resultats.append(f"NOTE DE RANCON: {note}")
        except:
            pass

    if not resultats:
        return "Aucune signature ransomware detectee"
    return "Analyse ransomware:\n" + "\n".join(resultats)

def keylogger_check():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Select Name,Id | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5)
        procs = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(procs, dict): procs = [procs]
        noms_keylog = ["keylog", "keylogger", "hook", "spy", "sniffer",
                       "klog", "type", "capture", "keystroke", "keydroid"]
        for p in procs:
            if isinstance(p, dict):
                nom = p.get("Name", "").lower()
                if any(k in nom for k in noms_keylog):
                    resultats.append(f"KEYLOGGER: {nom}.exe (PID {p.get('Id')})")
    except:
        pass
    if not resultats:
        return "Aucun keylogger detecte"
    return "\n".join(resultats)

def rootkit_check():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_SystemDriver | Where State -eq Running | Select Name,DisplayName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        drivers = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(drivers, dict): drivers = [drivers]
        noms_suspects = ["hook", "hide", "rootkit", "kav", "tdi", "npf", "catch"]
        for d in drivers:
            if isinstance(d, dict):
                nom = (d.get("Name", "") + " " + d.get("DisplayName", "")).lower()
                if any(s in nom for s in noms_suspects):
                    resultats.append(f"Driver suspect: {d.get('DisplayName', d.get('Name','?'))}")
    except:
        pass
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-WmiObject Win32_Process | Where Name -like '*svchost*' | Measure-Object | Select Count | ConvertTo-Json"],
            capture_output=True, text=True, timeout=5)
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        n = data.get("Count", 0) if isinstance(data, dict) else 0
        if n > 20:
            resultats.append(f"Svchost anormal: {n} instances")
    except:
        pass
    if not resultats:
        return "Aucun rootkit evident detecte"
    return "Analyse rootkit:\n" + "\n".join(resultats)
