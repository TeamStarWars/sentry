import ssl, socket, datetime, json

def analyser(hostname, port=443):
    try:
        if "://" in hostname:
            hostname = hostname.split("/")[2]
        hostname = hostname.split(":")[0]
    except:
        pass

    resultats = []

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                resultats.append(f"Certificat SSL pour: {hostname}:{port}")
                sujet_items = [(item[0][0], item[0][1]) for item in cert.get("subject", []) if item]
                cn = [v for k, v in sujet_items if k == "commonName" or k == "CN"]
                resultats.append(f"CN: {cn[0] if cn else '?'}")
                issuer_items = [(item[0][0], item[0][1]) for item in cert.get("issuer", []) if item]
                org = [v for k, v in issuer_items if k == "organizationName"]
                resultats.append(f"Emetteur: {org[0] if org else '?'}")
                expire = cert.get("notAfter", "?")
                fmt = "%b %d %H:%M:%S %Y %Z" if " " in expire else "%Y%m%d%H%M%SZ"
                try:
                    expire_dt = datetime.datetime.strptime(expire.replace(" GMT", "").strip(), fmt)
                    reste = (expire_dt - datetime.datetime.now()).days
                    if reste < 0:
                        resultats.append(f"EXPIRE: {expire} ({-reste} jours depasse)")
                    elif reste < 30:
                        resultats.append(f"EXPIRATION: {expire} (dans {reste} jours - URGENT)")
                    else:
                        resultats.append(f"Expire: {expire} (dans {reste} jours)")
                except:
                    resultats.append(f"Expire: {expire}")
                algo = cert.get("signatureAlgorithm", "?")
                resultats.append(f"Signature: {algo}")
                san = cert.get("subjectAltName", [])
                if san:
                    resultats.append(f"SAN ({len(san)} domaines): OK")
                resultats.append(f"Version: {cert.get('version', '?')}")
    except ssl.CertificateError as e:
        resultats.append(f"Erreur certificat: {e}")
    except Exception as e:
        resultats.append(f"Erreur connexion: {e}")

    return "\n".join(resultats) if resultats else "Analyse SSL impossible"

def analyser_headers(url):
    """Analyse les en-tetes de securite HTTP"""
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD")
        r = urllib.request.urlopen(req, timeout=10)
        headers = dict(r.headers)
        securite = {
            "Strict-Transport-Security": headers.get("Strict-Transport-Security", "ABSENT"),
            "X-Frame-Options": headers.get("X-Frame-Options", "ABSENT"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options", "ABSENT"),
            "Content-Security-Policy": "PRESENT" if headers.get("Content-Security-Policy") else "ABSENT",
            "X-XSS-Protection": headers.get("X-XSS-Protection", "ABSENT"),
            "Referrer-Policy": headers.get("Referrer-Policy", "ABSENT"),
        }
        lignes = [f"Headers securite HTTP pour {url}"]
        for k, v in securite.items():
            flag = "OK" if v != "ABSENT" else "MANQUANT"
            lignes.append(f"  {k}: {v} [{flag}]")
        return "\n".join(lignes)
    except Exception as e:
        return f"Erreur HTTP: {e}"
