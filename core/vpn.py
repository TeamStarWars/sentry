import subprocess, json, os, urllib.request

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "vpn_configs")

def ip_actuelle():
    try:
        r = urllib.request.urlopen("https://api.ipify.org?format=json", timeout=10)
        data = json.loads(r.read().decode())
        return f"IP publique: {data.get('ip','?')}"
    except:
        try:
            r = urllib.request.urlopen("https://httpbin.org/ip", timeout=10)
            data = json.loads(r.read().decode())
            return f"IP publique: {data.get('origin','?')}"
        except:
            return "Impossible de determiner l'IP"

def detecter_vpn():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_NetworkAdapter | Where {$_.Name -match 'VPN|Tunnel|OpenVPN|WireGuard|Nord|Express|Proton|Surfshark|Private|CyberGhost|PIA|Mullvad|Windscribe'} | Select Name,NetEnabled,NetConnectionStatus | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for d in data:
            if isinstance(d, dict) and d.get("NetEnabled"):
                resultats.append(f"Interface VPN: {d.get('Name','?')}")
    except:
        pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-Process | Where Name -match 'openvpn|wireguard|nordvpn|expressvpn|protonvpn|surfshark|pia|mullvad|windscribe|cyberghost|private' | Select Name,Id | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        for p in data:
            if isinstance(p, dict):
                resultats.append(f"Processus VPN: {p.get('Name','?')}.exe")
    except:
        pass

    if not resultats:
        return "Aucun VPN detecte"
    return "\n".join(resultats)

def kill_switch():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetFirewallRule -DisplayName 'Vindex*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; New-NetFirewallRule -DisplayName 'Vindex KillSwitch' -Direction Outbound -Action Block -Profile Any -ErrorAction SilentlyContinue | Out-Null; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return "Kill switch active: tout le trafic sortant bloque"
    except Exception as e:
        return f"Erreur: {e}"

def kill_switch_desactiver():
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-NetFirewallRule -DisplayName 'Vindex*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue"],
            capture_output=True, text=True, timeout=10)
        return "Kill switch desactive"
    except Exception as e:
        return f"Erreur: {e}"

def detecter_fuite_dns():
    try:
        r = urllib.request.urlopen("https://ipleak.net/json/", timeout=15)
        data = json.loads(r.read().decode())
        ips = data.get("ips", [])
        if len(ips) > 1:
            return f"Fuite DNS detectee: {len(ips)} IPs differentes"
        return f"DNS: {len(ips)} adresse(s) - OK"
    except:
        return "Test fuite DNS impossible"
