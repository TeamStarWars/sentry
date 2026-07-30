import threading, time, subprocess, json, os, datetime
from core import process as proc, network as net, alerte
from core.seclog import ajouter_entree

ACTIF = False
THREAD = None
SUSPECTS_TROUVES = []

def _analyser():
    global SUSPECTS_TROUVES
    while ACTIF:
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                "Get-Process | Select Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
                capture_output=True, text=True, timeout=5)
            data = json.loads(r.stdout) if r.stdout.strip() else []
            if not isinstance(data, list): data = [data]

            for p in data:
                if not isinstance(p, dict): continue
                nom = p.get("Name", "").lower()
                ram = p.get("RAM_MB", 0) or 0
                pid = p.get("Id", 0)

                if ram > 500 and nom not in SUSPECTS_TROUVES:
                    msg = f"RAM elevee: {nom}.exe PID {pid} = {ram}MB"
                    SUSPECTS_TROUVES.append(nom)
                    ajouter_entree("PROTECT", msg)
                    alerte.envoyer(msg, "Sentry - Alerte RAM")

            r2 = subprocess.run(["netstat", "-n"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=3)
            etablies = len([l for l in r2.stdout.split("\n") if "ESTABLISHED" in l])
            if etablies > 100:
                ajouter_entree("PROTECT", f"Connexions anormales: {etablies}")

            proc.verifier_suspects()

        except:
            pass
        time.sleep(10)

def demarrer():
    global ACTIF, THREAD
    if ACTIF:
        return "Protecteur deja actif"
    ACTIF = True
    THREAD = threading.Thread(target=_analyser, daemon=True)
    THREAD.start()
    ajouter_entree("PROTECT", "Protecteur demarre")
    return "Protecteur demarre (cycle 10s)"

def arreter():
    global ACTIF, THREAD
    if not ACTIF:
        return "Protecteur inactif"
    ACTIF = False
    THREAD = None
    ajouter_entree("PROTECT", "Protecteur arrete")
    return "Protecteur arrete"

def statut():
    if ACTIF:
        return f"Protecteur: ACTIF ({len(SUSPECTS_TROUVES)} alertes)"
    return "Protecteur: INACTIF"
