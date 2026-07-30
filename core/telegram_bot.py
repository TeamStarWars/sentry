"""Telegram Bot — controle distant via Telegram"""

import urllib.request, json, threading, time
from core import seclog

TOKEN = ""
CHAT_ID = ""
POLLING = False
THREAD = None
DERNIERES_CMDS = []

def configurer(token, chat_id):
    global TOKEN, CHAT_ID
    TOKEN = token
    CHAT_ID = chat_id
    seclog.ajouter_entree("TG_BOT", "Configure avec nouveau token")
    return "Telegram bot configure"

def envoyer(message):
    if not TOKEN or not CHAT_ID:
        return "Bot non configure. Utilisez 'tg-config <token> <chat_id>'"
    try:
        data = json.dumps({"chat_id": CHAT_ID, "text": message}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"}
        )
        r = urllib.request.urlopen(req, timeout=15)
        return "Message envoye"
    except Exception as e:
        return f"Erreur envoi: {e}"

def _poll():
    global POLLING, DERNIERES_CMDS
    offset = 0
    from main import executer_commande
    while POLLING:
        try:
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            )
            r = urllib.request.urlopen(req, timeout=35)
            data = json.loads(r.read().decode())
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {}).get("text", "")
                chat = update.get("message", {}).get("chat", {}).get("id", "")
                if str(chat) == CHAT_ID and msg:
                    if msg.startswith("/"):
                        cmd = msg[1:]
                        result = executer_commande(cmd)
                        envoyer(f"[{cmd}]\n{str(result)[:1000]}")
                        DERNIERES_CMDS.append(f"{cmd} -> OK")
            time.sleep(1)
        except:
            time.sleep(5)

def demarrer():
    global POLLING, THREAD
    if not TOKEN or not CHAT_ID:
        return "Configurez d'abord le bot: tg-config <token> <chat_id>"
    if POLLING:
        return "Bot deja actif"
    POLLING = True
    THREAD = threading.Thread(target=_poll, daemon=True)
    THREAD.start()
    seclog.ajouter_entree("TG_BOT", "Polling demarre")
    return "Telegram bot actif (ecoute les commandes /...)"

def arreter():
    global POLLING
    POLLING = False
    seclog.ajouter_entree("TG_BOT", "Arrete")
    return "Telegram bot arrete"

def statut():
    if TOKEN and CHAT_ID:
        etat = "ACTIF" if POLLING else "CONFIGURE (inactif)"
        return f"Telegram Bot: {etat}"
    return "Telegram Bot: NON CONFIGURE"
