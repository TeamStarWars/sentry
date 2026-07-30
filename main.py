#!/usr/bin/env python3
"""Sentry — Outils de diagnostic, cybersecurite et analyse"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core import network as net
from core import antivirus as av
from core import process as proc
from core import system as sysinfo
from core import security as sec
from core import wifi
from core import journaux as logs
from core import rapport, vt_check, snapshot, cleaner, monitor, scanner, alerte
from core import protector, behavior, persistence, integrity, chasse
from core import usb, updates, seclog, exploit, browser_audit, registry_audit, network_capture
from core import crypto_protect, atd, web_protect, vuln_scan, firewall_adv
from core import ransomware_remedi, antispam, privacy, safepay, vpn
from core import antitheft, optimizer, data_protect, profile
from core import cloud_phare, ssl_check, pe_analyze, yara_scan, sensors
from core import password_audit, honeypot, forensic, osint_tools, telegram_bot, automation, creator_panel, malware_detect, defense_plus

SORTIE_JSON = False
SORTIE_CSV = False

def afficher(msg, commande=""):
    if SORTIE_JSON:
        import json as _json
        print(_json.dumps({"ok": True, "data": str(msg)}, ensure_ascii=False, indent=2))
    elif SORTIE_CSV:
        import csv, io
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["commande", "resultat"])
        w.writerow([commande, str(msg).replace("\n", " | ")])
        print(buf.getvalue().strip())
    else:
        print(f"\n[+] {msg}")

def executer_commande(cmd):
    if not cmd:
        return
    parts = cmd.split()
    action = parts[0].lower()

    # ── RESEAU ──
    if action in ("ping",):
        cible = parts[1] if len(parts) > 1 else "8.8.8.8"
        return net.ping(cible)

    elif action == "traceroute":
        cible = parts[1] if len(parts) > 1 else "8.8.8.8"
        return net.traceroute(cible)

    elif action == "ports":
        ip = parts[1] if len(parts) > 1 else "127.0.0.1"
        debut = int(parts[2]) if len(parts) > 2 else 1
        fin = int(parts[3]) if len(parts) > 3 else 1024
        return net.ports(ip, debut, fin)

    elif action == "connexions":
        max_l = 9999 if len(parts) > 1 and parts[1] == "all" else 50
        return net.connexions(max_l)

    elif action in ("reseau", "reseaux", "network"):
        infos = [net.ping("8.8.8.8"), sysinfo.ip_locale()]
        return "\n".join(infos)

    elif action == "dns":
        cible = parts[1] if len(parts) > 1 else "google.com"
        return net.dns(cible)

    elif action == "arp-scan":
        return net.arp_scan()

    elif action == "netstat-b":
        return net.netstat_b()

    # ── ANTIVIRUS ──
    elif action == "scan":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "."
        return av.scanner_chemin(chemin)

    elif action == "hash":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: hash <chemin>"
        return av.hash_fichier(chemin)

    elif action == "defender":
        if len(parts) > 1 and parts[1] in ("scan", "full"):
            return av.demarrer_defenseur()
        return av.statut_defenseur()

    elif action == "vt":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: vt <fichier>"
        return vt_check.analyser(chemin)

    elif action == "vt-cle":
        cle = parts[1] if len(parts) > 1 else ""
        if not cle:
            return "Usage: vt-cle <votre_cle_api>"
        return vt_check.configurer_cle(cle)

    # ── PROCESSUS ──
    elif action in ("processus", "ps"):
        tri = parts[1] if len(parts) > 1 else "cpu"
        return proc.liste_processus(tri)

    elif action == "kill":
        if len(parts) < 2:
            return "Usage: kill <nom|PID>"
        return proc.killer(parts[1])

    elif action in ("analyse", "analyze"):
        pid = parts[1] if len(parts) > 1 else None
        return proc.analyse_processus(pid)

    elif action == "analyse-av":
        return av.analyser_processus()

    elif action == "verifier-suspects":
        return proc.verifier_suspects()

    elif action == "surveiller":
        if len(parts) > 1:
            return proc.ajouter_suspect(parts[1])
        return proc.lister_suspects()

    # ── SYSTEME ──
    elif action in ("diag", "diagnostic"):
        return sysinfo.diagnostic()

    elif action == "disque":
        lecteur = parts[1] if len(parts) > 1 else "C"
        return sysinfo.disque(lecteur.upper())

    elif action == "ram":
        return sysinfo.memoire()

    elif action == "ip":
        if len(parts) > 1 and parts[1] in ("public", "publique"):
            return sysinfo.ip_publique()
        return sysinfo.ip_locale()

    elif action == "demarrage":
        return sysinfo.demarrage()

    elif action == "services":
        return sysinfo.services()

    elif action == "rapport":
        chemin = parts[1] if len(parts) > 1 else "rapport_aurelyos.html"
        return rapport.generer(chemin)

    # ── WIFI ──
    elif action == "wifi":
        return wifi.wifi_reseaux()

    elif action == "wifi-profil":
        return wifi.wifi_profil()

    elif action == "wifi-mdp":
        nom = " ".join(parts[1:]) if len(parts) > 1 else None
        return wifi.wifi_mdp(nom)

    elif action == "wifi-interface":
        return wifi.wifi_interface()

    elif action == "clean":
        return cleaner.nettoyer()

    elif action == "monitor":
        duree = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 30
        return monitor.monitorer(duree)

    # ── JOURNAUX ──
    elif action == "logs":
        nb = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
        return logs.evenements("System", nb)

    elif action == "logs-securite":
        nb = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
        return logs.securite(nb)

    elif action == "logs-apps":
        nb = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
        return logs.applications(nb)

    elif action == "logs-liste":
        return logs.logs_disponibles()

    elif action == "snapshot":
        nom = " ".join(parts[1:]) if len(parts) > 1 else None
        return snapshot.sauvegarder(nom)

    elif action == "snapshot-liste":
        return snapshot.lister()

    elif action == "snapshot-compare":
        if len(parts) < 3:
            return "Usage: snapshot-compare <nom1> <nom2>"
        return snapshot.comparer(parts[1], parts[2])

    # ── SECURITE ──
    elif action in ("securite", "firewall"):
        return sec.regle_firewall()

    elif action == "ecoute":
        return sec.ports_ecoute()

    elif action == "verifier-port":
        port = parts[1] if len(parts) > 1 else "80"
        return sec.verifier_port(port)

    elif action == "signature":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: signature <fichier>"
        return sec.analyser_signe(chemin)

    elif action == "whitelist":
        if len(parts) > 1:
            chemin = " ".join(parts[1:])
            return sec.whitelist_ajouter(chemin)
        return sec.whitelist_liste()

    elif action == "find-suspicious":
        if len(parts) < 2:
            return scanner.fichiers_suspects(".")
        if parts[-1].isdigit():
            profondeur = int(parts[-1])
            chemin = " ".join(parts[1:-1])
        else:
            profondeur = 2
            chemin = " ".join(parts[1:])
        return scanner.fichiers_suspects(chemin, profondeur)

    elif action == "find-extensions":
        return scanner.extensible_par_type()

    elif action == "alerte-email":
        if len(parts) < 4:
            return "Usage: alerte-email <destinataire> <expediteur> <mdp> [smtp_server] [port]"
        smtp = parts[4] if len(parts) > 4 else "smtp.gmail.com"
        port = int(parts[5]) if len(parts) > 5 else 587
        return alerte.configurer_email(parts[1], parts[2], parts[3], smtp, port)

    elif action == "alerte-webhook":
        url = parts[1] if len(parts) > 1 else ""
        if not url:
            return "Usage: alerte-webhook <url>"
        return alerte.configurer_webhook(url)

    elif action == "alerte-envoyer":
        message = " ".join(parts[1:]) if len(parts) > 1 else "Test depuis Sentry"
        return alerte.envoyer(message)

    elif action == "protect":
        if len(parts) > 1 and parts[1] == "start":
            return protector.demarrer()
        elif len(parts) > 1 and parts[1] == "stop":
            return protector.arreter()
        return protector.statut()

    elif action in ("analyse-comportement", "analyse-deep"):
        pid = parts[1] if len(parts) > 1 else ""
        if not pid:
            return "Usage: analyse-comportement <PID>"
        return behavior.analyser(pid)

    elif action == "persistence":
        return persistence.scanner()

    elif action == "verify-sys":
        return integrity.verifier()

    elif action == "ransomware-check":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "."
        return chasse.ransomware_check(chemin)

    elif action == "keylogger-check":
        return chasse.keylogger_check()

    elif action == "rootkit-check":
        return chasse.rootkit_check()

    elif action == "usb-log":
        return usb.historique()

    elif action == "usb-devices":
        return usb.peripheriques()

    elif action == "windows-updates":
        return updates.lister()

    elif action == "windows-updates-check":
        return updates.rechercher()

    elif action == "seclog":
        nb = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 20
        return seclog.afficher(nb)

    elif action == "seclog-clear":
        return seclog.vider()

    elif action == "malware-scan":
        return malware_detect.scan_all()

    elif action == "malware-keylog":
        return "\n".join(malware_detect.detecter_keyloggers())

    elif action == "malware-rootkit":
        return "\n".join(malware_detect.detecter_rootkits())

    elif action == "malware-trojan":
        return "\n".join(malware_detect.detecter_trojans())

    elif action == "malware-stealer":
        return "\n".join(malware_detect.detecter_infostealers())

    elif action == "malware-fileless":
        return "\n".join(malware_detect.detecter_fileless())

    elif action == "malware-bootkit":
        return "\n".join(malware_detect.detecter_bootkit())

    elif action == "malware-adware":
        return "\n".join(malware_detect.detecter_adware())

    elif action == "malware-analyse":
        if len(parts) < 2:
            return "Usage: malware-analyse <PID|chemin>"
        arg = parts[1]
        if arg.isdigit():
            return malware_detect.analyser_menace(pid=int(arg))
        return malware_detect.analyser_menace(chemin=" ".join(parts[1:]))

    elif action == "dll-inject":
        return "\n".join(defense_plus.scan_dll_injection())

    elif action == "hollowing":
        return "\n".join(defense_plus.scan_process_hollowing())

    elif action == "clipboard-guard":
        return "\n".join(defense_plus.detecter_clipboard_watchers())

    elif action == "defender-hardening":
        return defense_plus.defender_hardening()

    elif action == "defender-status":
        return defense_plus.statut_hardening()

    elif action == "bitlocker":
        return defense_plus.verifier_bitlocker()

    elif action == "doh":
        return defense_plus.forcer_doh()

    elif action == "doh-status":
        return defense_plus.statut_doh()

    elif action == "breach-check":
        email = parts[1] if len(parts) > 1 else ""
        if not email:
            return "Usage: breach-check <email>"
        return defense_plus.verifier_brèche(email)

    elif action == "exploit-scan":
        return exploit.scanner()

    elif action == "browser-audit":
        return browser_audit.extensions()

    elif action == "registry-scan":
        return registry_audit.analyser()

    elif action == "net-capture":
        duree = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
        fichier = parts[2] if len(parts) > 2 else None
        return network_capture.capturer(duree, fichier)

    elif action == "analyse-tcp":
        return network_capture.analyser_connexions()

    elif action == "crypto-scan":
        return crypto_protect.analyser_processus()

    elif action == "crypto-hosts":
        return crypto_protect.verifier_hosts()

    elif action == "crypto-block":
        return crypto_protect.proteger_hosts()

    elif action == "atd":
        return atd.analyser()

    elif action == "web-check":
        url = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not url:
            return "Usage: web-check <url>"
        return web_protect.verifier_url(url)

    elif action == "web-dns":
        return web_protect.proteger_dns()

    elif action == "web-hosts":
        return web_protect.analyser_hosts()

    elif action == "vuln-scan":
        return vuln_scan.scanner()

    elif action == "fw-profiles":
        return firewall_adv.statut_profils()

    elif action == "fw-apps":
        return firewall_adv.regles_applicatives()

    elif action == "fw-block":
        app = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not app:
            return "Usage: fw-block <chemin_app>"
        return firewall_adv.bloquer_app(app)

    elif action == "fw-strict":
        return firewall_adv.mode_strict()

    elif action == "fw-normal":
        return firewall_adv.mode_normal()

    elif action == "ransom-shadows":
        return ransomware_remedi.shadow_copies()

    elif action == "ransom-protect":
        return ransomware_remedi.activer_protection()

    elif action == "ransom-scan":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "C:\\Users"
        return ransomware_remedi.fs_scan_extensions(chemin)

    elif action == "spam-check":
        texte = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not texte:
            return "Usage: spam-check <texte>"
        return antispam.analyser_texte_libre(texte)

    elif action == "spam-file":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: spam-file <chemin.eml>"
        return antispam.analyser_email(chemin)

    elif action == "privacy-cam":
        return privacy.webcam_check()

    elif action == "privacy-mic":
        return privacy.microphone_check()

    elif action == "privacy-procs":
        return privacy.processus_camera()

    elif action == "privacy-trackers":
        return privacy.tracker_check()

    elif action == "privacy-noads":
        return privacy.desactiver_pub()

    elif action == "safepay":
        url = " ".join(parts[1:]) if len(parts) > 1 else None
        return safepay.lancer_navigateur_securise(url)

    elif action == "safepay-clean":
        return safepay.nettoyer_profil()

    elif action == "vpn-ip":
        return vpn.ip_actuelle()

    elif action == "vpn-detect":
        return vpn.detecter_vpn()

    elif action == "vpn-kill":
        return vpn.kill_switch()

    elif action == "vpn-kill-off":
        return vpn.kill_switch_desactiver()

    elif action == "vpn-dns-leak":
        return vpn.detecter_fuite_dns()

    elif action == "antitheft-locate":
        return antitheft.localiser()

    elif action == "antitheft-lock":
        return antitheft.verrouiller()

    elif action == "antitheft-alert":
        return antitheft.alerte_sonore()

    elif action == "optimize":
        return optimizer.optimiser()

    elif action == "optimize-startup":
        nom = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not nom:
            return "Usage: optimize-startup <nom_programme>"
        return optimizer.desactiver_demarrage(nom)

    elif action == "protect-encrypt":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: protect-encrypt <fichier>"
        return data_protect.chiffrer_fichier(chemin)

    elif action == "protect-decrypt":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: protect-decrypt <fichier.aurelyos>"
        return data_protect.dechiffrer_fichier(chemin)

    elif action == "protect-wipe":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: protect-wipe <fichier> [passes]"
        passes = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 3
        return data_protect.effacer_fichier(chemin, passes)

    elif action == "protect-perms":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "."
        return data_protect.verifier_permissions(chemin)

    elif action == "profile-save":
        nom = parts[1] if len(parts) > 1 else "default"
        return profile.sauvegarder(nom)

    elif action == "profile-load":
        nom = parts[1] if len(parts) > 1 else "default"
        return profile.charger(nom)

    elif action == "profile-max":
        return profile.appliquer_securite_max()

    elif action == "profile-privacy":
        return profile.appliquer_privacy()

    elif action == "phare":
        if len(parts) > 1 and parts[1] == "stop":
            cloud_phare.stop()
            return "Phare arrete"
        if len(parts) > 1 and parts[1] == "status":
            return cloud_phare.status()
        port = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 8089
        bind = parts[3] if len(parts) > 3 else "127.0.0.1"
        token = parts[4] if len(parts) > 4 else None
        msg = cloud_phare.start(port, bind, token)
        afficher(msg)
        print("\nAppuyez sur Ctrl+C pour arreter le Phare...")
        try:
            while cloud_phare.SERVEUR_ACTIF:
                import time; time.sleep(1)
        except KeyboardInterrupt:
            cloud_phare.stop()
            return "Phare arrete"

    elif action == "phare-join":
        if len(parts) < 2:
            return "Usage: phare-join <ip_phare> [port] [token]"
        port = int(parts[2]) if len(parts) > 2 else 8089
        token = parts[3] if len(parts) > 3 else None
        return cloud_phare.join(parts[1], port, token)

    elif action == "phare-client":
        if len(parts) < 2:
            return "Usage: phare-client <ip_phare> [port] [token]"
        port = int(parts[2]) if len(parts) > 2 else 8089
        token = parts[3] if len(parts) > 3 else None
        msg = cloud_phare.start_client(parts[1], port, token)
        afficher(msg)
        print("\nHeartbeat actif. Ctrl+C pour arreter...")
        try:
            while True:
                import time; time.sleep(1)
        except KeyboardInterrupt:
            cloud_phare.SERVEUR_ACTIF = False
            return "Client Phare arrete"

    elif action == "creator":
        if len(parts) > 1 and parts[1] == "stop":
            creator_panel.stop()
            return "Panel arrete"
        if len(parts) > 1 and parts[1] == "status":
            return creator_panel.status()
        msg = creator_panel.start()
        afficher(msg)
        print("\nAppuyez sur Ctrl+C pour arreter le panel...")
        try:
            while creator_panel.PANEL_ACTIF:
                import time; time.sleep(1)
        except KeyboardInterrupt:
            creator_panel.stop()
            return "Panel arrete"

    elif action == "creator-list":
        return creator_panel.display()

    elif action == "ssl-check":
        hote = parts[1] if len(parts) > 1 else ""
        if not hote:
            return "Usage: ssl-check <hostname> [port]"
        port = int(parts[2]) if len(parts) > 2 else 443
        return ssl_check.analyser(hote, port)

    elif action == "ssl-headers":
        url = parts[1] if len(parts) > 1 else ""
        if not url:
            return "Usage: ssl-headers <url>"
        return ssl_check.analyser_headers(url)

    elif action == "whois":
        domaine = parts[1] if len(parts) > 1 else ""
        if not domaine:
            return "Usage: whois <domaine>"
        return net.whois(domaine)

    elif action == "netdiscover":
        plage = parts[1] if len(parts) > 1 else "192.168.1.0/24"
        return net.netdiscover(plage)

    elif action == "mac-spoof":
        interface = parts[1] if len(parts) > 1 else "Wi-Fi"
        mac = parts[2] if len(parts) > 2 else None
        return net.mac_spoof(interface, mac)

    elif action == "pe-analyze":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not chemin:
            return "Usage: pe-analyze <fichier.exe>"
        return pe_analyze.analyser(chemin)

    elif action == "yara-scan":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "."
        return yara_scan.scanner(chemin)

    elif action == "sensors":
        return sensors.temperatures()

    elif action == "sensors-fan":
        return sensors.ventilateurs()

    elif action == "password-audit":
        mdp = parts[1] if len(parts) > 1 else ""
        if not mdp:
            return "Usage: password-audit <mot_de_passe>"
        return password_audit.analyser(mdp)

    elif action == "password-pwned":
        mdp = parts[1] if len(parts) > 1 else ""
        if not mdp:
            return "Usage: password-pwned <mot_de_passe>"
        return password_audit.verifier_compromis(mdp)

    elif action == "honeypot":
        if len(parts) > 1 and parts[1] == "stop":
            return honeypot.arreter()
        if len(parts) > 1 and parts[1] == "status":
            return honeypot.statut()
        port = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 2222
        return honeypot.demarrer(port)

    elif action == "forensic-timeline":
        chemin = " ".join(parts[1:]) if len(parts) > 1 else "."
        return forensic.timeline(chemin)

    elif action == "forensic-prefetch":
        return forensic.prefetch()

    elif action == "forensic-recent":
        return forensic.recents()

    elif action == "geoip":
        ip = parts[1] if len(parts) > 1 else None
        return osint_tools.geoip(ip)

    elif action == "email-lookup":
        email = parts[1] if len(parts) > 1 else ""
        if not email:
            return "Usage: email-lookup <email>"
        return osint_tools.email_lookup(email)

    elif action == "tor-check":
        return osint_tools.tor_check()

    elif action == "tg-config":
        if len(parts) < 3:
            return "Usage: tg-config <token> <chat_id>"
        return telegram_bot.configurer(parts[1], parts[2])

    elif action == "tg-start":
        return telegram_bot.demarrer()

    elif action == "tg-stop":
        return telegram_bot.arreter()

    elif action == "tg-send":
        message = " ".join(parts[1:]) if len(parts) > 1 else "Test Sentry"
        return telegram_bot.envoyer(message)

    elif action == "tg-status":
        return telegram_bot.statut()

    elif action == "schedule-add":
        if len(parts) < 3:
            return "Usage: schedule-add <heure> <commande> [nom]"
        heure = parts[1]
        cmd_sched = " ".join(parts[2:])
        nom = f"Sentry{cmd_sched.split()[0].capitalize()}"
        return automation.planifier_journalier(heure, cmd_sched, nom)

    elif action == "schedule-list":
        return automation.lister_taches()

    elif action == "schedule-remove":
        nom = " ".join(parts[1:]) if len(parts) > 1 else ""
        if not nom:
            return "Usage: schedule-remove <nom_tache>"
        return automation.supprimer_tache(nom)

    elif action == "backup":
        return automation.backup()

    elif action in ("help", "h", "aide", "?"):
        return None  # help handled separately

    elif action in ("quit", "exit", "q"):
        return "__EXIT__"

    return f"Commande inconnue: {action}. Tape 'help' pour la liste."

def afficher_help():
    print("""
  ============================================================
       SENTRY v2.0 - AIDE COMPLETE (80+ commandes)
  ============================================================

  --- RESEAU ---
    ping <cible>              Tester la connexion
    traceroute <cible>        Tracer la route
    ports <ip> <d> <f>        Scanner les ports (threading)
    connexions [all]          Voir les connexions actives
    dns <cible>               Resolution DNS
    reseau                    Apercu rapide du reseau
    arp-scan                  Decouvrir les peripheriques LAN
    netstat-b                 Connexions avec programmes
    net-capture [s] [fichier] Capturer le trafic TCP (CSV)
    analyse-tcp               Analyse des connexions TCP

  --- ANTIVIRUS & MENACES ---
    scan <chemin>             Analyser avec Defender
    hash <fichier>            Calculer MD5/SHA1/SHA256
    defender                  Statut Defender
    defender scan             Scan complet Defender
    analyse-av                Processus consommateurs
    vt <fichier>              Analyser VirusTotal (API)
    vt-cle <cle>              Configurer cle API VirusTotal
    ransomware-check <chem>   Detecter signatures rancon
    keylogger-check           Chercher processus keylogger
    rootkit-check             Chercher signes rootkit
    malware-scan              Scan complet toutes menaces
    malware-keylog            Detecter keyloggers
    malware-rootkit           Detecter rootkits
    malware-trojan            Detecter trojans/backdoors
    malware-stealer           Detecter infostealers
    malware-fileless          Detecter malwares fileless
    malware-bootkit           Detecter bootkits
    malware-adware            Detecter adwares/PUPs
    malware-analyse <PID/path>Analyser processus ou fichier

  --- DEFENSE+ (PROTECTIONS AVANCEES) ---
    dll-inject                Scanner DLL injectees
    hollowing                 Detecter process hollowing
    clipboard-guard           Surveiller espions presse-papier
    defender-hardening        Appliquer reglages max Defender
    defender-status           Verifier statut hardening
    bitlocker                 Verifier chiffrement volumes
    doh                       Forcer DNS over HTTPS (Cloudflare)
    doh-status                Statut DoH
    breach-check <email>      Verifier si email a fuité

  --- PROCESSUS & COMPORTEMENT ---
    processus                 Lister les processus
    kill <nom|PID>            Tuer un processus
    analyse <PID>             Analyser un processus
    analyse-comportement <PID>Analyse approfondie (DLLs, reseau)
    surveiller <nom>          Surveiller un processus
    verifier-suspects         Verifier suspects actifs

  --- SYSTEME & INTEGRITE ---
    diag                      Diagnostic complet
    disque <lettre>           Infos disque
    ram                       Infos memoire
    ip [publique]             IP locale ou publique
    demarrage                 Programmes au demarrage
    services                  Services actifs
    rapport [fichier.html]    Generer rapport HTML complet
    verify-sys                Verifier integrite (SFC, DISM)
    windows-updates           Mises a jour installees
    windows-updates-check     Rechercher mises a jour dispo

  --- WIFI ---
    wifi                      Reseaux WiFi disponibles
    wifi-profil               Profils WiFi enregistres
    wifi-mdp [nom]            Mot de passe d'un profil WiFi
    wifi-interface            Infos interface WiFi

  --- SECURITE & PARE-FEU ---
    securite                  Regles pare-feu
    ecoute                    Ports en ecoute
    verifier-port <port>      Tester un port
    signature <fichier>       Analyser la signature
    whitelist [chemin]        Exclusions Defender
    fw-profiles               Statut des profils pare-feu
    fw-apps                   Regles bloquantes applicatives
    fw-block <chemin>         Bloquer une application (outbound)
    fw-strict                 Mode strict (tout bloquer sauf DNS/HTTP)
    fw-normal                 Mode normal (sortant autorise)

  --- PROTECTION TEMPS REEL ---
    protect                   Statut du protecteur
    protect start             Demarrer la protection
    protect stop              Arreter la protection

  --- ADVANCED THREAT DEFENSE ---
    atd                       Score de menace global
    vuln-scan                 Scan vulnerabilites systeme
    exploit-scan              Scan exploits connus
    crypto-scan               Detecter minage crypto
    crypto-hosts              Verifier blocage sites minage
    crypto-block              Bloquer sites minage (hosts)
    ransomware-shadows        Lister copies shadow
    ransomware-protect        Activer protection restauration
    ransomware-scan <chem>    Scanner extensions rancon

  --- WEB & ANTI-PHISHING ---
    web-check <url>           Analyser une URL suspecte
    web-dns                   Securiser DNS (Cloudflare)
    web-hosts                 Analyser fichier hosts

  --- ANTI-SPAM ---
    spam-check <texte>        Analyser un texte (score spam)
    spam-file <fichier.eml>   Analyser un fichier email

  --- PRIVACY & VIE PRIVEE ---
    privacy-cam               Detecter cameras
    privacy-mic               Detecter microphones
    privacy-procs             Processus utilisant camera/audio
    privacy-trackers          Analyser traqueurs (cookies, hosts)
    privacy-noads             Desactiver pub personnalisee

  --- SAFEPAY (PAIEMENT SECURISE) ---
    safepay [url]             Lancer navigateur securise isole
    safepay-clean             Nettoyer profil SafePay

  --- VPN & ANONYMISATION ---
    vpn-ip                    Voir IP publique
    vpn-detect                Detecter VPN actif
    vpn-kill                  Activer kill switch (couper reseau)
    vpn-kill-off              Desactiver kill switch
    vpn-dns-leak              Tester fuite DNS

  --- ANTI-THEFT (ANTIVOL) ---
    antitheft-locate          Localiser la machine (IP + geo)
    antitheft-lock            Verrouiller la session
    antitheft-alert           Alerte sonore

  --- JOURNAUX & AUDIT ---
    logs [nb]                 Evenements Systeme
    logs-securite [nb]        Evenements de securite
    logs-apps [nb]            Evenements Applications
    logs-liste                Journaux disponibles
    seclog [nb]               Journal des alertes Sentry
    seclog-clear              Vider le journal
    persistence               Scanner points de persistence
    registry-scan             Analyser registre suspect
    browser-audit             Auditer extensions navigateur
    usb-log                   Historique peripheriques USB
    usb-devices               Peripheriques USB actuels

  --- SNAPSHOTS ---
    snapshot [nom]            Sauvegarder etat systeme
    snapshot-liste            Lister les snapshots
    snapshot-compare <a> <b>  Comparer deux snapshots

  --- OPTIMISATION ---
    clean                     Nettoyer le systeme
    optimize                  Optimisation en un clic
    optimize-startup <nom>    Desactiver programme demarrage

  --- PROTECTION DONNEES ---
    protect-encrypt <fichier> Chiffrer un fichier
    protect-decrypt <fichier> Dechiffrer un fichier
    protect-wipe <fichier>    Effacer definitivement (3 passes)
    protect-perms <chemin>    Verifier permissions fichier

  --- PROFIL ---
    profile-save [nom]        Sauvegarder profil
    profile-load [nom]        Charger profil
    profile-max               Appliquer securite maximale
    profile-privacy           Appliquer mode prive

  --- MAINTENANCE ---
    monitor [secondes]        Monitoring temps reel
    find-suspicious <chem>    Chercher fichiers suspects
    find-extensions           Extensions surveillees

  --- ALERTES ---
    alerte-email <dest> <exp> <mdp> [smtp] [port]
    alerte-webhook <url>
    alerte-envoyer [message]

  --- CLOUD PHARE ---
    phare [port] [bind] [token]   Demarrer le serveur Phare
    phare stop                    Arreter le Phare
    phare status                  Statut du Phare
    phare-join <ip> [port] [tok]  Connecter un client au Phare
    phare-client <ip> [port][tok] Mode client heartbeat

  --- PANEL CREATEUR ---
    creator [port]                Lancer le panel web createur
    creator stop                  Arreter le panel
    creator status                Statut du panel
    creator-list                  Resume console des machines

  --- FLAGS ---
    --json                    Sortie en JSON
    --csv                     Sortie en CSV

  quit / exit                 Quitter
    """)

def mode_interactif():
    print("""
  ============================================
     SENTRY v2.0
     Cyber - Analyse - Protection - Surveillance
  ============================================
    """)
    print(">70 commandes — Tape 'help' pour la liste complete")
    print("Exemple: diag | rapport | protect start | monitor\n")
    while True:
        try:
            cmd = input("outil> ").strip()
            if not cmd:
                continue
            resultat = executer_commande(cmd)
            if resultat is None:
                afficher_help()
            elif resultat == "__EXIT__":
                print("Sentry termine.")
                break
            else:
                afficher(resultat)
        except KeyboardInterrupt:
            print("\nInterrompu.")
            break
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if "--json" in flags:
        SORTIE_JSON = True
    if "--csv" in flags:
        SORTIE_CSV = True

    if args:
        cmd = " ".join(args)
        resultat = executer_commande(cmd)
        if resultat is None:
            afficher_help()
        elif resultat == "__EXIT__":
            pass
        else:
            afficher(resultat)
    else:
        mode_interactif()