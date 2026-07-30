import subprocess, os, json, re
from core.safe import esc

def optimiser():
    resultats = []

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-3) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=30)
        resultats.append(f"Temp: {r.stdout.strip()}")
    except:
        resultats.append("Temp: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        resultats.append(f"Corbeille: {r.stdout.strip()}")
    except:
        resultats.append("Corbeille: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path $env:SystemRoot\\Prefetch -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-14) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=30)
        resultats.append(f"Prefetch: {r.stdout.strip()}")
    except:
        resultats.append("Prefetch: erreur")

    try:
        r = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=10)
        resultats.append("DNS: vide")
    except:
        resultats.append("DNS: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path \"$env:LOCALAPPDATA\\Microsoft\\Windows\\INetCache\" -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=60)
        resultats.append(f"Cache IE/Edge: {r.stdout.strip()}")
    except:
        resultats.append("Cache IE/Edge: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path \"$env:APPDATA\\..\\Local\\Temp\" -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=60)
        resultats.append(f"Temp utilisateur: {r.stdout.strip()}")
    except:
        resultats.append("Temp utilisateur: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path \"$env:WINDIR\\SoftwareDistribution\\Download\" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=30)
        resultats.append(f"Cache WU: {r.stdout.strip()}")
    except:
        resultats.append("Cache WU: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Disable-NetAdapterChecksumOffload -Name '*', -ErrorAction SilentlyContinue; Disable-NetAdapterLso -Name '*' -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=10)
    except:
        pass

    return "Optimisation:\n" + "\n".join(resultats)

def desactiver_demarrage(nom):
    if not re.match(r"^[a-zA-Z0-9_ .-]+$", str(nom)):
        return "Nom invalide"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            f"Get-CimInstance Win32_StartupCommand | Where Name -like '*{esc(nom)}*' | ForEach-Object {{ Remove-Item -Path $_.Command -ErrorAction SilentlyContinue }}; Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -Name '{esc(nom)}' -ErrorAction SilentlyContinue | Remove-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' -Name '{esc(nom)}' -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        return f"Tentative desactivation: {nom}"
    except Exception as e:
        return f"Erreur: {e}"
