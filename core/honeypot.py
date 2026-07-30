import socket, threading, datetime
from core import seclog

ACTIF = False
THREAD = None
PORT = 2222

def _handle_client(conn, addr):
    timestamp = str(datetime.datetime.now())[:19]
    ip, port = addr
    try:
        data = conn.recv(1024)
        msg = f"Honeypot: connexion de {ip}:{port} -> {data[:50]}"
    except:
        msg = f"Honeypot: connexion de {ip}:{port}"
    conn.close()
    seclog.ajouter_entree("HONEYPOT", msg)
    print(f"[HONEYPOT] {msg}")

def _listen():
    global ACTIF
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", PORT))
        s.listen(5)
        s.settimeout(1)
        while ACTIF:
            try:
                conn, addr = s.accept()
                t = threading.Thread(target=_handle_client, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except:
                break
    except:
        pass
    finally:
        s.close()

def demarrer(port=2222):
    global ACTIF, THREAD, PORT
    if ACTIF:
        return f"Honeypot deja actif sur port {PORT}"
    PORT = port
    ACTIF = True
    THREAD = threading.Thread(target=_listen, daemon=True)
    THREAD.start()
    seclog.ajouter_entree("HONEYPOT", f"Demarre sur port {PORT}")
    return f"Honeypot actif: port {PORT}"

def arreter():
    global ACTIF
    if not ACTIF:
        return "Honeypot inactif"
    ACTIF = False
    seclog.ajouter_entree("HONEYPOT", "Arrete")
    return "Honeypot arrete"

def statut():
    if ACTIF:
        return f"Honeypot: ACTIF (port {PORT})"
    return "Honeypot: INACTIF"
