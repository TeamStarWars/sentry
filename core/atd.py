import subprocess, json, os, datetime

class ThreatScorer:
    def __init__(self):
        self.score = 0
        self.details = []

    def ajouter(self, points, raison):
        self.score += points
        self.details.append(f"+{points}: {raison}")

    def evaluer(self):
        self.ajouter(10, "Analyse de base lancee")
        self._check_processus_anormaux()
        self._check_ports_suspects()
        self._check_connexions_sortantes()
        self._check_services_anormaux()
        return self._rapport()

    def _check_processus_anormaux(self):
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                "Get-Process | Select Name,Id,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout) if r.stdout.strip() else []
            if isinstance(data, dict): data = [data]
            noms_suspects = ["powershell", "cmd", "wscript", "cscript", "rundll32"]
            noms_inconnus = [p for p in data if isinstance(p, dict) and
                             p.get("Name", "").lower() in noms_suspects and
                             p.get("RAM_MB", 0) > 100]
            for p in noms_inconnus[:5]:
                self.ajouter(15, f"Processus suspect: {p.get('Name','?')}.exe RAM:{p.get('RAM_MB',0)}MB")
        except:
            pass

    def _check_ports_suspects(self):
        try:
            r = subprocess.run(["netstat", "-an"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=5)
            ports_ecoute = []
            for l in r.stdout.split("\n"):
                if "LISTENING" in l:
                    parts = l.split()
                    if len(parts) >= 2:
                        port = parts[1].rsplit(":", 1)[-1]
                        ports_ecoute.append(port)
            ports_dangereux = [p for p in ports_ecoute if p in ["4444", "5555", "6666", "1337", "31337", "12345", "54321"]]
            if ports_dangereux:
                self.ajouter(25, f"Ports suspects en ecoute: {', '.join(ports_dangereux)}")
        except:
            pass

    def _check_connexions_sortantes(self):
        try:
            r = subprocess.run(["netstat", "-n"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=5)
            etablies = [l for l in r.stdout.split("\n") if "ESTABLISHED" in l]
            pays_suspects = []
            for l in etablies:
                parts = l.split()
                if len(parts) >= 3:
                    ip = parts[2].split(":")[0]
                    if ip.startswith(("185.", "91.", "5.", "31.", "46.", "89.", "195.", "212.")):
                        pays_suspects.append(ip)
            if len(pays_suspects) > 5:
                self.ajouter(20, f"Connexions vers IP suspectes: {len(pays_suspects)}")
        except:
            pass

    def _check_services_anormaux(self):
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                "Get-Service | Where Status -eq Running | Select Name,DisplayName | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout) if r.stdout.strip() else []
            if isinstance(data, dict): data = [data]
            for s in data:
                if isinstance(s, dict) and (not s.get("DisplayName", "") or s.get("Name", "").startswith("_")):
                    self.ajouter(30, f"Service anonyme: {s.get('Name','?')}")
        except:
            pass

    def _rapport(self):
        niveau = "FAIBLE" if self.score < 30 else ("MOYEN" if self.score < 60 else ("ELEVE" if self.score < 100 else "CRITIQUE"))
        lignes = [
            f"=== ADVANCED THREAT DEFENSE ===",
            f"Score de menace: {self.score}/100 - {niveau}",
            f""
        ]
        lignes.extend(self.details)
        if self.score > 50:
            lignes.append("")
            lignes.append("RECOMMANDATIONS:")
            if self.score > 80:
                lignes.append("- Executez un scan antivirus complet")
                lignes.append("- Verifiez les processus anormaux")
            if any("Ports" in d for d in self.details):
                lignes.append("- Verifiez les ports en ecoute")
            lignes.append("- Analysez les connexions reseau sortantes")
        return "\n".join(lignes)

def analyser():
    scorer = ThreatScorer()
    return scorer.evaluer()
