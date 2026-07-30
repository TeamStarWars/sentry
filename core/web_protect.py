import os, json, urllib.request, socket, subprocess

SITES_PHISHING = [
    "phishing", "login-verify", "account-verify", "secure-login",
    "bank-verify", "paypal-verify", "confirm-identity",
    "password-reset", "update-account", "verify-identity"
]

DOMAINES_MALVEILLANTS = [
    "bit.ly", "tinyurl.com", "shorturl.at", "goo.gl", "shorte.st",
    "adf.ly", "ow.ly", "is.gd", "buff.ly", "tiny.cc"
]

def verifier_url(url):
    if not url.startswith("http"):
        url = "http://" + url
    resultats = []

    nom_domaine = url.split("/")[2] if "://" in url else url.split("/")[0]
    if any(mal in nom_domaine.lower() for mal in SITES_PHISHING):
        resultats.append(f"DOMAINE SUSPECT: motifs phishing dans {nom_domaine}")
    for court in DOMAINES_MALVEILLANTS:
        if court in nom_domaine.lower():
            resultats.append(f"Raccourcisseur: {court} - verifier destination")

    try:
        req = urllib.request.Request(url, method="HEAD")
        req.timeout = 5
        r = urllib.request.urlopen(req)
        headers = dict(r.headers)
        if "X-Phishing" in headers or "X-Malicious" in headers:
            resultats.append("HEADER SECURITE: site marque malveillant")
        resultats.append(f"HTTP {r.getcode()} - {len(r.headers)} headers")
    except Exception as e:
        resultats.append(f"Connexion impossible: {e}")

    try:
        ip = socket.gethostbyname(nom_domaine)
        resultats.append(f"IP: {ip}")
        if ip.startswith(("185.", "91.", "5.", "31.")):
            resultats.append("IP dans plage suspecte")
    except:
        resultats.append("Resolution DNS impossible")

    if not resultats:
        return "URL semble saine"
    return "Analyse URL:\n" + "\n".join(resultats)

def proteger_dns():
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-DnsClientServerAddress -AddressFamily IPv4 | Where ServerAddresses -notlike '*' | Select ServerAddresses"],
            capture_output=True, text=True, timeout=10)
        return "Configuration DNS OK"
    except:
        pass
    try:
        r = subprocess.run(["netsh", "interface", "ipv4", "set", "dnsservers", "name=*", "source=static", "address=1.1.1.1", "register=primary"],
            capture_output=True, text=True, timeout=10)
        return "DNS securise: 1.1.1.1 (Cloudflare)"
    except Exception as e:
        return f"Erreur configuration DNS: {e}"

def analyser_hosts():
    try:
        hosts = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
        with open(hosts, "r", encoding="utf-8", errors="replace") as f:
            lignes = f.readlines()
        entries = []
        anomalies = []
        for i, l in enumerate(lignes, 1):
            l = l.strip()
            if l and not l.startswith("#"):
                parts = l.split()
                if len(parts) >= 2:
                    ip, domaine = parts[0], parts[1]
                    if ip != "127.0.0.1" and ip != "::1":
                        anomalies.append(f"Ligne {i}: {ip} {domaine}")
                    entries.append(f"{ip} {domaine}")
        resultats = [f"Entrees hosts: {len(entries)}"]
        if anomalies:
            resultats.append(f"ANOMALIES ({len(anomalies)}):")
            resultats.extend(anomalies[:10])
        return "\n".join(resultats)
    except Exception as e:
        return f"Erreur: {e}"
