import subprocess, json, os, datetime, re
from core.safe import esc

TASKS_FILE = os.path.join(os.path.dirname(__file__), "..", "sentry_tasks.json")

def planifier_journalier(heure, commande, nom="SentryScan"):
    import re
    if not re.match(r"^\d{1,2}:\d{2}$", str(heure)):
        return "Heure invalide (ex: 14:30)"
    try:
        tasks = []
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                tasks = json.load(f)
        tasks.append({"nom": nom, "commande": commande, "heure": heure, "actif": True})
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)

        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"$action = New-ScheduledTaskAction -Execute 'py' -Argument '\"{os.path.join(os.path.dirname(__file__),'..','main.py')} {esc(commande)}\"'; "
            f"$trigger = New-ScheduledTaskTrigger -Daily -At '{esc(heure)}'; "
            f"Register-ScheduledTask -TaskName '{esc(nom)}' -Action $action -Trigger $trigger -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return f"Tache '{nom}' planifiee: {commande} a {heure}"
    except:
        return "Erreur planification"

def lister_taches():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ScheduledTask -TaskName 'Sentry*' -ErrorAction SilentlyContinue | Select TaskName,State,Triggers | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Taches ({len(data)}):"]
            for d in data:
                if isinstance(d, dict):
                    lignes.append(f"  {d.get('TaskName','?')} - {d.get('State','?')}")
            return "\n".join(lignes)
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                tasks = json.load(f)
            if tasks:
                return f"Taches locales: {len(tasks)}"
        return "Aucune tache"
    except:
        return "Erreur liste"

def supprimer_tache(nom):
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Unregister-ScheduledTask -TaskName '{esc(nom)}' -Confirm:$false -ErrorAction SilentlyContinue"],
            capture_output=True, text=True, timeout=10)
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE) as f:
                tasks = json.load(f)
            tasks = [t for t in tasks if t.get("nom") != nom]
            with open(TASKS_FILE, "w") as f:
                json.dump(tasks, f, indent=2)
        return f"Tache '{nom}' supprimee"
    except:
        return "Erreur suppression"

def backup():
    chemin = os.path.dirname(os.path.dirname(__file__))
    fichiers = ["sentry_profile.json", "sentry_alerts.json", "sentry_tasks.json"]
    try:
        import zipfile
        nom = f"sentry_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(nom, "w") as z:
            for f in fichiers:
                fp = os.path.join(chemin, f)
                if os.path.exists(fp):
                    z.write(fp, f)
        return f"Backup: {nom}"
    except:
        return "Erreur backup"
