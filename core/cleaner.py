import subprocess, os

def nettoyer():
    resultats = []
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path $env:TEMP -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=60)
        resultats.append(f"Temp: {r.stdout.strip()}")
    except:
        resultats.append("Temp: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path $env:SystemRoot\\Prefetch -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=30)
        resultats.append(f"Prefetch: {r.stdout.strip()}")
    except:
        resultats.append("Prefetch: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Clear-RecycleBin -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=15)
        resultats.append(f"Corbeille: {r.stdout.strip()}")
    except:
        resultats.append("Corbeille: erreur")

    try:
        r = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, timeout=10)
        resultats.append("Cache DNS: vide")
    except:
        resultats.append("Cache DNS: erreur")

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path $env:LOCALAPPDATA\\Microsoft\\Windows\\INetCache -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer -and $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Output 'OK'"],
            capture_output=True, text=True, timeout=30)
        resultats.append(f"Cache navigateur: {r.stdout.strip()}")
    except:
        resultats.append("Cache navigateur: erreur")

    return "Nettoyage:\n" + "\n".join(resultats)
