import smtplib, json, os, urllib.request

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "alerte_config.json")

def configurer_email(destinataire, expediteur, mdp, smtp_server="smtp.gmail.com", smtp_port=587):
    config = {
        "type": "email",
        "destinataire": destinataire,
        "expediteur": expediteur,
        "mdp": mdp,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return "Notification email configuree"

def configurer_webhook(url):
    config = {"type": "webhook", "url": url}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return "Notification webhook configuree"

def envoyer(message, sujet="Vindex Alerte"):
    if not os.path.exists(CONFIG_FILE):
        return "Aucune configuration. Utilisez 'alerte-email' ou 'alerte-webhook'"
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        if config.get("type") == "email":
            return _envoyer_email(config, sujet, message)
        elif config.get("type") == "webhook":
            return _envoyer_webhook(config, message)
        return "Type inconnu"
    except Exception as e:
        return f"Erreur envoi: {e}"

def _envoyer_email(config, sujet, message):
    try:
        msg = f"From: {config['expediteur']}\nTo: {config['destinataire']}\nSubject: {sujet}\n\n{message}"
        s = smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=15)
        s.starttls()
        s.login(config["expediteur"], config["mdp"])
        s.sendmail(config["expediteur"], [config["destinataire"]], msg.encode("utf-8"))
        s.quit()
        return "Alerte envoyee par email"
    except Exception as e:
        return f"Erreur email: {e}"

def _envoyer_webhook(config, message):
    try:
        data = json.dumps({"text": message}).encode()
        req = urllib.request.Request(config["url"], data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        return "Alerte envoyee au webhook"
    except Exception as e:
        return f"Erreur webhook: {e}"
