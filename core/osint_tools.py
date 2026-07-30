import urllib.request, json, socket, re

def geoip(ip=None):
    if not ip:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "8.8.8.8"
    try:
        req = urllib.request.Request(f"https://ipapi.co/{ip}/json/", headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read().decode())
        if isinstance(data, dict) and "error" not in data:
            lignes = [f"GeoIP: {ip}"]
            for k in ["ip", "city", "region", "country_name", "org", "postal", "latitude", "longitude", "timezone"]:
                if data.get(k):
                    lignes.append(f"  {k}: {data[k]}")
            return "\n".join(lignes)
        return f"GeoIP: aucune info pour {ip}"
    except Exception as e:
        return f"Erreur GeoIP: {e}"

def email_lookup(email):
    try:
        domaine = email.split("@")[1] if "@" in email else email
        ip = socket.gethostbyname(domaine)
        mx = []
        try:
            r = urllib.request.urlopen(f"https://dns.google/resolve?name={domaine}&type=MX", timeout=10)
            data = json.loads(r.read().decode())
            for a in data.get("Answer", []):
                if a.get("type") == 15:
                    mx.append(a.get("data", ""))
        except:
            pass
        lignes = [f"OSINT Email: {email}"]
        lignes.append(f"  Domaine: {domaine}")
        lignes.append(f"  IP: {ip}")
        if mx:
            lignes.append(f"  MX: {', '.join(mx[:3])}")
        try:
            r = urllib.request.urlopen(f"https://isitari.email/api/{domaine}", timeout=10)
            data = json.loads(r.read().decode())
            if isinstance(data, dict):
                lignes.append(f"  Email valide: {data.get('valid', '?')}")
        except:
            pass
        return "\n".join(lignes)
    except Exception as e:
        return f"Erreur OSINT: {e}"

def tor_check():
    try:
        r = urllib.request.urlopen("https://check.torproject.org/api/ip", timeout=10)
        data = json.loads(r.read().decode())
        if isinstance(data, dict):
            if data.get("IsTor"):
                return "CONNEXION TOR DETECTEE"
            return "Pas de connexion Tor detectee"
        return "Verification Tor impossible"
    except:
        return "Erreur verification Tor"
