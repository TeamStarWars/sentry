import winreg, subprocess, json

POINTS_SUSPECTS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\LoadAppInit_DLLs"),
    (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services"),
]

def analyser():
    resultats = []

    for hkey, chemin in POINTS_SUSPECTS:
        try:
            key = winreg.OpenKey(hkey, chemin)
            i = 0
            while True:
                try:
                    nom, valeur, _ = winreg.EnumValue(key, i)
                    if len(valeur) > 5 or valeur:
                        resultats.append(f"{chemin} -> {nom}")
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except:
            pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Services' -ErrorAction SilentlyContinue | Get-Member -MemberType NoteProperty | Select Name | ConvertTo-Json"],
            capture_output=True, text=True, timeout=15)
    except:
        pass

    if not resultats:
        return "Aucune entree registre suspecte"
    return f"Analyse registre ({len(resultats)} entrees):\n" + "\n".join(resultats[:25])
