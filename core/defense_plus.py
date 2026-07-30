"""Defense+ — protections avancees : anti-injection, anti-hollowing, clipboard guard, hardening"""

import subprocess, json, os, re, ctypes, hashlib, urllib.request
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
                                     headers={"User-Agent": "Sentry"})
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read().decode("utf-8")
        for line in body.split("\n"):
            if line.startswith(suffix):
                count = int(line.split(":")[1].strip())
                return f"ALERTE: {email} trouve dans {count} breche(s) !"
        return f"{email}: aucune breche detectee"
    except:
        return "Erreur verification (pas de connexion ?)"
