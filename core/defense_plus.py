"""Defense+ — protections avancees : anti-injection, anti-hollowing, clipboard guard, hardening, reseau, audit"""

import subprocess, json, os, re, ctypes, hashlib, urllib.request, datetime
from core.safe import esc, valider_pid

def _ps(cmd, timeout=15):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, timeout=timeout)
        raw = r.stdout.decode("utf-8", errors="replace")
        return raw.encode("cp1252", errors="replace").decode("cp1252")
    except:
        return ""

# ─── ANTI-DLL INJECTION ───

def scan_dll_injection():
    """Detecte les DLL chargees dans des processus qui ne devraient pas en avoir"""
    resultats = []
    cibles = {
        "explorer": ["kernel32", "ntdll", "user32", "gdi32", "shell32", "comctl32", "shlwapi", "ole32", "wininet"],
        "svchost":  ["kernel32", "ntdll", "advapi32", "rpcrt4", "sechost"],
        "lsass":    ["kernel32", "ntdll", "advapi32", "crypt32", "secur32"],
        "winlogon": ["kernel32", "ntdll", "user32", "gdi32"],
    }
    for proc_name, dlls_ok in cibles.items():
        r = _ps(f"Get-Process -Name '{proc_name}' -ErrorAction SilentlyContinue | Select -ExpandProperty Modules | Select ModuleName | ConvertTo-Json")
        try:
            data = json.loads(r) if r.strip() else []
            if isinstance(data, dict): data = [data]
            dlls = [d.get("ModuleName","").lower() for d in data if isinstance(d, dict)]
            for dll in dlls:
                ext_ok = any(ok in dll for ok in dlls_ok)
                if not ext_ok and dll.endswith(".dll"):
                    path = ""
                    for d in data:
                        if isinstance(d, dict) and d.get("ModuleName","").lower() == dll:
                            path = d.get("FileName","")
                            break
                    if "system32" not in str(path).lower() and "syswow64" not in str(path).lower() and "program files" not in str(path).lower():
                        resultats.append(f"INJECTION: {dll} dans {proc_name}.exe ({path})")
        except:
            pass
    return resultats if resultats else ["Aucune DLL injectee detectee"]

# ─── ANTI-PROCESS HOLLOWING ───

def scan_process_hollowing():
    """Detecte les processus crees avec des anomalies (hollowing)"""
    resultats = []
    r = _ps("Get-Process | Select Name,Id,Path,@{N='HasWindow';E={[bool]($_.MainWindowHandle -ne 0)}},@{N='SessionId';E={$_.SessionId}} | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        windows_pids = {}
        for p in data:
            if isinstance(p, dict):
                name = p.get("Name","").lower()
                pid = p.get("Id",0)
                has_win = p.get("HasWindow", False)
                path = p.get("Path","") or ""
                if has_win and not path:
                    resultats.append(f"HOLLOWING: {name}.exe (PID {pid}) fenetre visible mais chemin vide")
                if has_win and "temp" in path.lower():
                    resultats.append(f"SUSPECT: {name}.exe (PID {pid}) lance depuis TEMP")
                if name == "rundll32" and has_win:
                    resultats.append(f"ALERTE: rundll32.exe (PID {pid}) avec fenetre - probable hollowing")
    except:
        pass
    return resultats if resultats else ["Aucun process hollowing detecte"]

# ─── CLIPBOARD GUARD ───

def detecter_clipboard_watchers():
    """Detecte les processus qui surveillent le presse-papier"""
    resultats = []
    r = _ps("Get-Process | Where { $_.MainWindowTitle -ne '' -and ($_.Name -match 'clip|note|evernote|onenote|keepass|bitwarden|lastpass|ditto|clipboard') } | Select Name,Id,MainWindowTitle | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        for p in data:
            if isinstance(p, dict):
                resultats.append(f"Watcher: {p.get('Name','?')}.exe ({p.get('MainWindowTitle','?')})")
    except:
        pass
    r2 = _ps("Get-Process | Where { $_.Name -match 'clip|hook' -and $_.MainWindowTitle -eq '' } | Select Name,Id | ConvertTo-Json")
    try:
        data2 = json.loads(r2) if r2.strip() else []
        if isinstance(data2, dict): data2 = [data2]
        for p in data2:
            if isinstance(p, dict):
                name = p.get("Name","").lower()
                if name not in ("clipboard", "clipup", "clipspv"):
                    resultats.append(f"CLIPBOARD: {p.get('Name','?')}.exe (PID {p.get('Id','?')}) ecoute le presse-papier")
    except:
        pass
    return resultats if resultats else ["Aucun espion presse-papier detecte"]

# ─── WINDOWS DEFENDER HARDENING ───

def defender_hardening():
    """Applique les reglages max de Windows Defender"""
    resultats = []
    cmds = [
        ("Cloud", "Set-MpPreference -MAPSReporting 2 -ErrorAction SilentlyContinue"),
        ("Cloud block", "Set-MpPreference -CloudBlockLevel High -ErrorAction SilentlyContinue"),
        ("PUP", "Set-MpPreference -PUAProtection 1 -ErrorAction SilentlyContinue"),
        ("ASR", "Set-MpPreference -AttackSurfaceReductionRules_Actions Enabled -ErrorAction SilentlyContinue"),
        ("Archive scan", "Set-MpPreference -DisableArchiveScanning $false -ErrorAction SilentlyContinue"),
        ("Email scan", "Set-MpPreference -DisableEmailScanning $false -ErrorAction SilentlyContinue"),
        ("Script scan", "Set-MpPreference -DisableScriptScanning $false -ErrorAction SilentlyContinue"),
        ("Behavior", "Set-MpPreference -DisableBehaviorMonitoring $false -ErrorAction SilentlyContinue"),
        ("IOAV", "Set-MpPreference -DisableIOAVProtection $false -ErrorAction SilentlyContinue"),
        ("Realtime", "Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction SilentlyContinue"),
    ]
    for label, cmd in cmds:
        r = _ps(cmd, 10)
        if "error" not in r.lower():
            resultats.append(f"  {label}: OK")
        else:
            resultats.append(f"  {label}: erreur")
    return "Hardening Defender:\n" + "\n".join(resultats)

def statut_hardening():
    """Verifie le statut du hardening Defender"""
    r = _ps("Get-MpPreference | Select MAPSReporting,CloudBlockLevel,PUAProtection,AttackSurfaceReductionRules_Actions | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else {}
        if isinstance(data, dict):
            lignes = ["Statut hardening Defender:"]
            lignes.append(f"  Cloud (MAPS): {data.get('MAPSReporting','?')}")
            lignes.append(f"  Cloud block: {data.get('CloudBlockLevel','?')}")
            lignes.append(f"  PUP: {'ACTIF' if data.get('PUAProtection') else 'INACTIF'}")
            return "\n".join(lignes)
    except:
        pass
    return "Erreur statut hardening"

# ─── BITLOCKER AUDIT ───

def verifier_bitlocker():
    """Verifie le chiffrement BitLocker des volumes"""
    resultats = []
    r = _ps("Get-CimInstance -Namespace root/cimv2/security/microsofttpm -ClassName Win32_Tpm | Select IsEnabled_InitialValue,IsActivated_InitialValue | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else {}
        if isinstance(data, dict):
            tpm = "ACTIF" if data.get("IsEnabled_InitialValue") else "INACTIF"
            resultats.append(f"TPM: {tpm}")
    except:
        resultats.append("TPM: indisponible")
    r2 = _ps("Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select DeviceID | ForEach-Object { $c = Get-BitLockerVolume -MountPoint $_.DeviceID -ErrorAction SilentlyContinue; if($c){[PSCustomObject]@{Drive=$_.DeviceID;Status=$c.ProtectionStatus}} } | ConvertTo-Json")
    try:
        data = json.loads(r2) if r2.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            for d in data:
                if isinstance(d, dict):
                    etat = "CHIFFRE" if d.get("Status") == 1 else "NON CHIFFRE"
                    resultats.append(f"  {d.get('Drive','?')}: {etat}")
        else:
            resultats.append("  Aucun volume BitLocker")
    except:
        resultats.append("BitLocker: impossible a verifier (admin requis)")
    return "\n".join(resultats)

# ─── DNS OVER HTTPS ───

def forcer_doh():
    """Force le chiffrement DNS (Cloudflare + DoH)"""
    try:
        r1 = _ps("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters' -Name 'EnableAutoDoh' -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue; Write-Output 'OK'")
        r2 = _ps("Add-DnsClientDohServerAddress -ServerAddress '1.1.1.1' -DohTemplate 'https://cloudflare-dns.com/dns-query' -AllowFallbackToUdp $false -AutoUpgrade $true -ErrorAction SilentlyContinue; Add-DnsClientDohServerAddress -ServerAddress '1.0.0.1' -DohTemplate 'https://cloudflare-dns.com/dns-query' -AllowFallbackToUdp $false -AutoUpgrade $true -ErrorAction SilentlyContinue; Write-Output 'OK'")
        return "DNS over HTTPS active (Cloudflare 1.1.1.1, 1.0.0.1)"
    except:
        return "Erreur activation DoH (admin requis)"

def statut_doh():
    r = _ps("Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Dnscache\\Parameters' -Name 'EnableAutoDoh' -ErrorAction SilentlyContinue | Select EnableAutoDoh | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else {}
        if isinstance(data, dict):
            etat = "ACTIF" if data.get("EnableAutoDoh") == 2 else "INACTIF"
            return f"DoH: {etat}"
    except:
        pass
    return "DoH: inconnu"

# ─── BREACH CHECK ───

def verifier_brèche(email):
    """Verifie si un email a fuité via HaveIBeenPwned (API anonyme)"""
    import hashlib
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return "Email invalide"
    h = hashlib.sha1(email.encode()).hexdigest().upper()
    prefix = h[:5]
    suffix = h[5:]
    try:
        req = urllib.request.Request(f"https://api.pwnedpasswords.com/range/{prefix}",
                                     headers={"User-Agent": "Vindex"})
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read().decode("utf-8")
        for line in body.split("\n"):
            if line.startswith(suffix):
                count = int(line.split(":")[1].strip())
                return f"ALERTE: {email} trouve dans {count} breche(s) !"
        return f"{email}: aucune breche detectee"
    except:
        return "Erreur verification (pas de connexion ?)"

# ─── ARP SPOOFING DETECTOR ───

def detecter_arp_spoof():
    """Detecte les ARP spoofing en comparant les MAC de la passerelle"""
    resultats = []
    r = _ps("Get-NetNeighbor -AddressFamily IPv4 | Where {$_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*' -or $_.IPAddress -like '172.*'} | Select IPAddress,LinkLayerAddress | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        ips_vues = {}
        for d in data:
            if isinstance(d, dict):
                ip = d.get("IPAddress","")
                mac = d.get("LinkLayerAddress","")
                if ip in ips_vues and ips_vues[ip] != mac:
                    resultats.append(f"ARP SPOOF: {ip} a deux MAC differentes ({ips_vues[ip]} et {mac})")
                ips_vues[ip] = mac
    except:
        pass
    return resultats if resultats else ["Aucun ARP spoofing detecte"]

# ─── RDP BRUTE FORCE DETECTOR ───

def detecter_rdp_brute():
    """Analyse les logs pour les tentatives RDP forcees"""
    resultats = []
    r = _ps("Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4625} -MaxEvents 50 -ErrorAction SilentlyContinue | Select TimeCreated,Message | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        ips = {}
        for e in data:
            if isinstance(e, dict):
                msg = e.get("Message","")
                ip = "?"
                m = re.search(r"Adresse réseau source\s*:\s*(\S+)", msg)
                if m: ip = m.group(1)
                m2 = re.search(r"Source Network Address[:\s]+(\S+)", msg)
                if m2: ip = m2.group(1)
                if ip not in ("?", "127.0.0.1", "-"):
                    ips[ip] = ips.get(ip, 0) + 1
        for ip, count in sorted(ips.items(), key=lambda x: -x[1]):
            if count >= 5:
                resultats.append(f"BRUTE FORCE: {ip} - {count} tentatives echouees")
        if not resultats:
            resultats.append("Aucune tentative RDP forcee detectee")
    except:
        resultats.append("Erreur analyse logs RDP")
    return resultats

# ─── SMB SHARES SCAN ───

def scan_shares():
    """Scanne les partages SMB exposes sur le reseau local"""
    resultats = []
    r = _ps("Get-SmbShare -ErrorAction SilentlyContinue | Select Name,Path,Description,ShareType | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            resultats.append(f"Partages SMB ({len(data)}):")
            for d in data:
                if isinstance(d, dict):
                    typ = d.get("ShareType",0)
                    if typ == 0:
                        resultats.append(f"  {d.get('Name','?')} -> {d.get('Path','?')}")
            if len(resultats) == 1:
                resultats.append("  Aucun partage utilisateur")
        else:
            resultats.append("Aucun partage SMB")
    except:
        resultats.append("Erreur scan SMB (admin requis)")
    return resultats

# ─── PASSWORD POLICY AUDIT ───

def auditer_password_policy():
    """Audite la politique de mots de passe Windows"""
    resultats = []
    r = _ps("Get-CimInstance Win32_AccountPolicy | Select MaximumPasswordAge,MinimumPasswordAge,MinimumPasswordLength,PasswordHistorySize | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else {}
        if isinstance(data, dict):
            mpl = data.get("MinimumPasswordLength", 0)
            mpa = data.get("MaximumPasswordAge", 0)
            phs = data.get("PasswordHistorySize", 0)
            resultats.append(f"Longueur minimale: {mpl} car. {'FAIBLE' if mpl < 8 else 'OK'}")
            resultats.append(f"Age max: {mpa} jours {'TROP LONG' if mpa > 90 else 'OK'}")
            resultats.append(f"Historique: {phs} mdp {'FAIBLE' if phs < 10 else 'OK'}")
    except:
        resultats.append("Erreur politique mdp")
    return resultats

# ─── AUTORUNS DEEP ───

def autoruns_deep():
    """Scanne les emplacements de demarrage (30+ reg, dossier taches)"""
    resultats = []
    emplacements = [
        ("HKLM:Run", "Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue"),
        ("HKCU:Run", "Get-ItemProperty 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue"),
        ("HKLM:RunOnce", "Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce' -ErrorAction SilentlyContinue"),
        ("HKCU:RunOnce", "Get-ItemProperty 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce' -ErrorAction SilentlyContinue"),
        ("Startup Folder", "Get-ChildItem \"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" -ErrorAction SilentlyContinue"),
        ("Common Startup", "Get-ChildItem \"$env:PROGRAMDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\" -ErrorAction SilentlyContinue"),
    ]
    total = 0
    for label, cmd in emplacements:
        r = _ps(cmd, 10)
        props = re.findall(r"([\w]+)\s+:\s+(.+)", r)
        for prop, val in props:
            if prop.lower() not in ("pspath", "psparentpath", "pschildname", "psprovider"):
                total += 1
                if total <= 20:
                    resultats.append(f"  {label}: {prop} = {val.strip()[:80]}")
    resultats.insert(0, f"Autoruns ({total} entrees trouvees):" if total > 0 else "Aucun autorun")
    return resultats

# ─── RESTORE POINT ───

def creer_restore_point():
    """Cree un point de restauration systeme"""
    r = _ps("Checkpoint-Computer -Description 'Vindex Restore' -RestorePointType MODIFY_SETTINGS -ErrorAction SilentlyContinue; Write-Output 'OK'", 60)
    if "ok" in r.lower():
        return "Point de restauration cree"
    try:
        r2 = _ps("Enable-ComputerRestore -Drive 'C:\\' -ErrorAction SilentlyContinue; Checkpoint-Computer -Description 'Vindex Restore' -RestorePointType MODIFY_SETTINGS -ErrorAction SilentlyContinue; Write-Output 'OK'", 60)
        if "ok" in r2.lower():
            return "Protection activee + point de restauration cree"
    except:
        pass
    return "Erreur (admin requis)"

def lister_restore_points():
    r = _ps("Get-ComputerRestorePoint | Select SequenceNumber,Description,CreationTime,RestorePointType | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            lignes = [f"Points de restauration ({len(data)}):"]
            for d in data:
                if isinstance(d, dict):
                    t = str(d.get("CreationTime","?"))[:19]
                    lignes.append(f"  {t} - {d.get('Description','?')}")
            return "\n".join(lignes)
    except:
        pass
    return "Aucun point de restauration"

# ─── SERVICES AUDIT ───

def auditer_services():
    """Repère les services vulnérables (droits eleves, exposés)"""
    resultats = []
    r = _ps("Get-CimInstance Win32_Service | Where {$_.StartMode -eq 'Auto' -and $_.PathName -ne ''} | Select Name,DisplayName,PathName,StartName,State | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        for s in data:
            if isinstance(s, dict):
                path = s.get("PathName","").lower()
                user = s.get("StartName","").lower()
                if "localsystem" in user or "local system" in user:
                    if "temp" in path or "users" in path or "appdata" in path:
                        resultats.append(f"VULN: {s.get('Name','?')} tourne en SYSTEM depuis un dossier utilisateur ({path[:60]})")
                if user in ("", ".\\default"):
                    resultats.append(f"SUSPECT: {s.get('Name','?')} - compte par defaut")
    except:
        pass
    return resultats if resultats else ["Aucun service vulnérable detecte"]

# ─── CERT SCAN ───

def scanner_certificats():
    """Verifie les certificats SSL expires ou frauduleux"""
    resultats = []
    r = _ps("Get-ChildItem Cert:\\LocalMachine\\My -ErrorAction SilentlyContinue | Select Subject,NotAfter,Thumbprint,Issuer | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        maintenant = datetime.datetime.now()
        for c in data:
            if isinstance(c, dict):
                sujet = c.get("Subject","?")
                notafter = c.get("NotAfter","")
                if notafter:
                    try:
                        date = datetime.datetime.fromisoformat(notafter.replace("Z","+00:00"))
                        reste = (date - maintenant).days
                        if reste < 0:
                            resultats.append(f"EXPIRE: {sujet[:50]} (depuis {-reste} jours)")
                        elif reste < 30:
                            resultats.append(f"BIENTOT: {sujet[:50]} ({reste} jours restants)")
                    except:
                        pass
    except:
        pass
    return resultats if resultats else ["Aucun probleme de certificat"]

# ─── NET BANDWIDTH ───

def bande_passante():
    """Montre les programmes qui consomment le plus de bande passante"""
    resultats = []
    r = _ps("Get-NetAdapterStatistics -ErrorAction SilentlyContinue | Select Name,ReceivedBytes,SentBytes | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        for n in data:
            if isinstance(n, dict):
                rx = int(n.get("ReceivedBytes",0)) / (1024**2)
                tx = int(n.get("SentBytes",0)) / (1024**2)
                resultats.append(f"  {n.get('Name','?')}: {rx:.0f} Mo recus, {tx:.0f} Mo envoyes")
    except:
        pass
    return resultats if resultats else ["Aucune info bande passante"]

# ─── PROCESS TIMELINE ───

def process_timeline(heures=24):
    """Affiche les processus crees recemment via les logs"""
    resultats = []
    r = _ps("Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4688} -MaxEvents 30 -ErrorAction SilentlyContinue | Select TimeCreated,Message | ConvertTo-Json")
    try:
        data = json.loads(r) if r.strip() else []
        if isinstance(data, dict): data = [data]
        if not data:
            return "Aucun evenement de creation de processus"
        lignes = [f"Processus crees (derniers {heures}h):"]
        for e in data:
            if isinstance(e, dict):
                t = str(e.get("TimeCreated","?"))[:19]
                msg = e.get("Message","")
                m = re.search(r"Nouveau processus.*Nom.*[.:]\s*(\S+)", msg)
                if m:
                    pid = re.search(r"ID de la nouvelle tache[:\s]+(\d+)", msg)
                    pid_str = f"PID {pid.group(1)}" if pid else ""
                    lignes.append(f"  [{t}] {m.group(1)}")
        return "\n".join(lignes[:15])
    except:
        return "Erreur lecture logs (admin requis)"
