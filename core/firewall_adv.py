import subprocess, json, re
from core.safe import esc

def statut_profils():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetFirewallProfile | Select Name,Enabled,DefaultInboundAction,DefaultOutboundAction,LogFileName | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        lignes = ["Pare-feu:"]
        for p in data:
            if isinstance(p, dict):
                lignes.append(f"  {p.get('Name','?')}: {'ACTIF' if p.get('Enabled') else 'INACTIF'} (IN: {p.get('DefaultInboundAction','?')} OUT: {p.get('DefaultOutboundAction','?')})")
        return "\n".join(lignes)
    except:
        return "Erreur pare-feu"

def regles_applicatives():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetFirewallRule -Direction Outbound -Action Block -Enabled True -ErrorAction SilentlyContinue | Select DisplayName,Program | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data and any(d.get("Program") for d in data if isinstance(d, dict)):
            lignes = [f"Regles bloquantes ({len(data)}):"]
            for d in data[:15]:
                if isinstance(d, dict) and d.get("Program"):
                    lignes.append(f"  {d.get('Program','?')}")
            return "\n".join(lignes)
        return "Aucune regle bloquante"
    except:
        return "Erreur regles"

def bloquer_app(nom_app):
    if not re.match(r"^[a-zA-Z0-9_ .\\-:]+$", str(nom_app)):
        return "Nom d'application invalide"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"New-NetFirewallRule -DisplayName 'Vindex Block {esc(nom_app)}' -Direction Outbound -Program '{esc(nom_app)}' -Action Block -ErrorAction SilentlyContinue | Out-Null; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=10)
        return f"Application bloquee: {nom_app}"
    except:
        return "Erreur blocage"

def mode_strict():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Set-NetFirewallProfile -All -DefaultInboundAction Block -DefaultOutboundAction Block -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        r2 = subprocess.run(["powershell", "-NoProfile", "-Command",
            "New-NetFirewallRule -DisplayName 'Vindex DNS' -Direction Outbound -Protocol UDP -RemotePort 53 -Action Allow -ErrorAction SilentlyContinue | Out-Null; New-NetFirewallRule -DisplayName 'Vindex HTTP' -Direction Outbound -Protocol TCP -RemotePort 80,443 -Action Allow -ErrorAction SilentlyContinue | Out-Null; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return "Mode strict: tout bloque sauf DNS, HTTP, HTTPS"
    except:
        return "Erreur mode strict"

def mode_normal():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Set-NetFirewallProfile -All -DefaultInboundAction Block -DefaultOutboundAction Allow -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return "Mode normal: entrant bloque, sortant autorise"
    except:
        return "Erreur mode normal"
