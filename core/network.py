import subprocess, os, socket, re, json, concurrent.futures, urllib.request
from core.safe import esc, valider_port, valider_ip, sanitize_html
ENC = "cp1252"

def ping(hote):
    hote_safe = hote.strip().split()[0] if hote.strip() else "8.8.8.8"
    if not valider_ip(hote_safe) and not re.match(r"^[a-zA-Z0-9.-]+$", hote_safe):
        return "Ping: cible invalide"
    try:
        r = subprocess.run(["ping", "-n", "4", hote_safe], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=30)
        lignes = r.stdout.split("\n")
        stats = [l for l in lignes if "ms" in l and ("min" in l or "moyen" in l or "Average" in l)]
        if stats:
            return f"Ping {sanitize_html(hote_safe)}: {stats[0].strip()}"
        perte = [l for l in lignes if "perte" in l or "loss" in l]
        if perte:
            return f"Ping {sanitize_html(hote_safe)}: {perte[0].strip()}"
        return f"Ping {sanitize_html(hote_safe)}: ok"
    except subprocess.TimeoutExpired:
        return f"Ping {sanitize_html(hote_safe)}: timeout"
    except Exception as e:
        return f"Erreur ping: {e}"

def traceroute(cible):
    cible_safe = cible.strip().split()[0] if cible.strip() else "8.8.8.8"
    if not valider_ip(cible_safe) and not re.match(r"^[a-zA-Z0-9.-]+$", cible_safe):
        return "Traceroute: cible invalide"
    try:
        r = subprocess.run(["tracert", "-h", "15", cible_safe], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=60)
        lignes = [l for l in r.stdout.split("\n") if l.strip() and "Traceroute" not in l and "trace" not in l.lower()]
        return "\n".join(lignes[:10]) if lignes else f"Traceroute {sanitize_html(cible_safe)}: aucun saut"
    except subprocess.TimeoutExpired:
        return f"Traceroute {sanitize_html(cible_safe)}: timeout"
    except Exception as e:
        return f"Erreur traceroute: {e}"

def _scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        return port if s.connect_ex((ip, port)) == 0 else None
    finally:
        s.close()

def ports(ip="127.0.0.1", debut=1, fin=1024):
    if not valider_ip(ip):
        return "IP invalide"
    p_debut = max(1, min(65535, debut))
    p_fin = max(p_debut, min(65535, fin))
    plage = list(range(p_debut, p_fin + 1))
    ouverts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futurs = {executor.submit(_scan_port, ip, p): p for p in plage}
        for futur in concurrent.futures.as_completed(futurs):
            r = futur.result()
            if r: ouverts.append(r)
    ouverts.sort()
    if ouverts:
        return f"Ports ouverts sur {sanitize_html(ip)}: {', '.join(map(str, ouverts))}"
    return f"Aucun port ouvert ({p_debut}-{p_fin})"

def connexions(max_lignes=50):
    try:
        r = subprocess.run(["netstat", "-n"], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=10)
        lignes = [l.strip() for l in r.stdout.split("\n") if "ESTABLISHED" in l or "CLOSE_WAIT" in l]
        if lignes:
            limite = min(len(lignes), max_lignes)
            reste = len(lignes) - limite
            res = f"Connexions: {len(lignes)}\n" + "\n".join(lignes[:limite])
            if reste > 0:
                res += f"\n... +{reste} (connexions all pour tout voir)"
            return res
        return "Aucune connexion etablie"
    except:
        return "Erreur netstat"

def arp_scan():
    try:
        r = subprocess.run(["arp", "-a"], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=10)
        lignes = [l.strip() for l in r.stdout.split("\n") if l.strip() and "." in l[:20] and "interface" not in l.lower()]
        resultats = []
        for l in lignes:
            parts = l.split()
            if len(parts) >= 3 and parts[0].count(".") == 3:
                resultats.append(f"{parts[0]:20} {parts[1]:20}")
        return f"Peripheriques ({len(resultats)}):\n" + "\n".join(resultats) if resultats else "Aucun peripherique"
    except:
        return "Erreur scan LAN"

def netstat_b(max_lignes=30):
    try:
        r = subprocess.run(["netstat", "-bno"], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=15)
        lignes = r.stdout.split("\n")
        resultats = []
        i = 0
        while i < len(lignes):
            l = lignes[i].strip()
            if any(p in l for p in ["LISTENING", "ESTABLISHED", "TIME_WAIT"]):
                prog = lignes[i-1].strip() if i > 0 else "?"
                parts = l.split()
                if len(parts) >= 4:
                    resultats.append(f"{prog:30} {parts[1]:25} {parts[3]:15} PID:{parts[-1] if parts[-1].isdigit() else '?'}")
            i += 1
        return f"Connexions:\n" + "\n".join(resultats[:max_lignes]) if resultats else "Aucune (admin ?)"
    except:
        return "Erreur netstat"

def dns(cible):
    cible_safe = cible.strip().split()[0] if cible.strip() else "google.com"
    if not re.match(r"^[a-zA-Z0-9.-]+$", cible_safe):
        return "DNS: cible invalide"
    try:
        r = subprocess.run(["nslookup", cible_safe], capture_output=True, text=True, encoding=ENC, errors="replace", timeout=15)
        lignes = [l.strip() for l in r.stdout.split("\n") if l.strip() and ":" in l]
        return "\n".join(lignes[:6]) if lignes else f"DNS {sanitize_html(cible_safe)}: aucune resolution"
    except:
        return "Erreur DNS"

def whois(domaine):
    from urllib.parse import quote
    domaine_safe = domaine.strip().split()[0]
    if not re.match(r"^[a-zA-Z0-9.-]+$", domaine_safe):
        return "WHOIS: domaine invalide"
    try:
        req = urllib.request.Request(
            f"https://whois.cymru.com/cgi-bin/whois.cgi?action=lookup&query={quote(domaine_safe)}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        r = urllib.request.urlopen(req, timeout=15)
        body = r.read().decode("utf-8", errors="replace")
        lignes = [l.strip() for l in body.split("\n") if l.strip() and ":" in l and "nslookup" not in l.lower()]
        return "\n".join(lignes[:15]) if lignes else "Aucune info WHOIS"
    except Exception as e:
        return f"Erreur WHOIS: {e}"

def netdiscover(plage="192.168.1.0/24"):
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$", plage):
        return "Plage invalide (ex: 192.168.1.0/24)"
    base_ip = plage.split("/")[0].rsplit(".", 1)[0]
    ps_cmd = f"1..254 | ForEach-Object {{ $ip='{esc(base_ip)}.' + $_; if(Test-Connection $ip -Count 1 -Quiet -ErrorAction SilentlyContinue){{$ip}} }}"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=120)
        ips = [l.strip() for l in r.stdout.split("\n") if l.strip().count(".") == 3]
        return f"Hotels ({len(ips)}):\n" + "\n".join(ips[:30]) if ips else "Aucun"
    except:
        return "Erreur netdiscover"

def mac_spoof(interface="Wi-Fi", adresse=None):
    if not adresse:
        import random, secrets
        adresse = "02:%02x:%02x:%02x:%02x:%02x" % tuple(secrets.randbits(8) for _ in range(5))
    iface_safe = esc(interface)
    mac_safe = esc(adresse)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Set-NetAdapter -Name '{iface_safe}' -MacAddress '{mac_safe}' -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return f"MAC {interface} -> {adresse}"
    except:
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                f"Get-NetAdapter -Name '{iface_safe}' -ErrorAction SilentlyContinue | Select MacAddress | ConvertTo-Json"],
                capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout) if r.stdout.strip() else {}
            mac = data.get("MacAddress", "?") if isinstance(data, dict) else "?"
            return f"MAC actuelle {interface}: {mac}"
        except:
            return "Erreur MAC"
