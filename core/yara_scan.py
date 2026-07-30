"""Scan YARA — detection de signatures sans dependance externe"""

import os, re

REGLES_YARA = {
    "AgentTesla": [rb"AgentTesla", rb"RemoteAccess", rb"KeyLog", rb".*\.txt.*mail"],
    "CobaltStrike": [rb"cobaltstrike", rb"beacon", rb"MSSE-SERVER"],
    "Mimikatz": [rb"mimikatz", rb"sekurlsa", rb"lsadump", rb"wdigest"],
    "ProcessHollowing": [rb"ZwUnmapViewOfSection", rb"CreateProcessA", rb"NtUnmapViewOfSection"],
    "Keylogger": [rb"SetWindowsHookEx", rb"GetAsyncKeyState", rb"WH_KEYBOARD", rb"keylogger"],
    "Ransomware_Generic": [rb"bitcoin", rb"encrypt", rb"decrypt", rb"ransom", rb"README"],
    "Shellcode": [rb"\x31\xc0\x50\x68", rb"\xfc\xe8\x82", rb"\x90\x90\x90"],
    "Powershell_Abuse": [rb"-enc", rb"FromBase64String", rb"Invoke-Expression", rb"IEX"],
    "USB_Spread": [rb"CopyItems", rb"RemoveDrive", rb"Autorun\.inf"],
    "AntiDebug": [rb"IsDebuggerPresent", rb"NtGlobalFlag", rb"CheckRemoteDebugger"],
}

def scanner(chemin):
    if not os.path.exists(chemin):
        return f"Chemin introuvable: {chemin}"
    resultats = []
    fichiers_scan = []

    if os.path.isfile(chemin):
        fichiers_scan = [chemin]
    elif os.path.isdir(chemin):
        for root, _, files in os.walk(chemin):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".exe", ".dll", ".scr", ".ps1", ".vbs", ".bin", ".sys", ".com"):
                    fichiers_scan.append(os.path.join(root, f))
                    if len(fichiers_scan) >= 50:
                        break
        resultats.append(f"Scan YARA: {len(fichiers_scan)} fichiers")

    for fp in fichiers_scan[:30]:
        try:
            with open(fp, "rb") as f:
                contenu = f.read()
            for regle_nom, signatures in REGLES_YARA.items():
                for sig in signatures:
                    if re.search(sig, contenu, re.IGNORECASE):
                        resultats.append(f"  {regle_nom}: {os.path.basename(fp)}")
                        break
        except:
            pass

    if len(resultats) <= 1:
        return "Aucune signature malveillante detectee"
    return "\n".join(resultats)
