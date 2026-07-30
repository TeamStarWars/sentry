import subprocess, json, hashlib, os

def verifier():
    resultats = []

    try:
        r = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True, timeout=300)
        if "found" in r.stdout.lower() or "trouve" in r.stdout.lower():
            if "none" in r.stdout.lower() or "aucun" in r.stdout.lower():
                resultats.append("SFC: Integrite OK")
            else:
                resultats.append("SFC: Fichiers corrompus detects")
        else:
            resultats.append(f"SFC: {r.stdout.strip()[:100]}")
    except subprocess.TimeoutExpired:
        resultats.append("SFC: Timeout (scan long)")
    except Exception as e:
        resultats.append(f"SFC: {e}")

    try:
        r = subprocess.run(["Dism", "/Online", "/Cleanup-Image", "/CheckHealth"],
            capture_output=True, text=True, timeout=60)
        if "repairable" in r.stdout.lower() or "reparable" in r.stdout.lower():
            resultats.append("DISM: Image reparables detectee")
        elif "no component" in r.stdout.lower() or "aucun" in r.stdout.lower():
            resultats.append("DISM: Image saine")
        else:
            lignes = [l.strip() for l in r.stdout.split("\n") if l.strip() and ":" in l]
            resultats.append(f"DISM: {lignes[-1] if lignes else 'voir detail'}")
    except:
        resultats.append("DISM: erreur")

    sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
    fichiers_critiques = ["ntoskrnl.exe", "hal.dll", "kernel32.dll", "ntdll.dll"]
    for f in fichiers_critiques:
        chemin = os.path.join(sys32, f)
        if os.path.isfile(chemin):
            try:
                h = hashlib.sha256()
                with open(chemin, "rb") as fh:
                    while chunk := fh.read(8192):
                        h.update(chunk)
                sha = h.hexdigest()
                resultats.append(f"  {f}: SHA256 present")
            except:
                resultats.append(f"  {f}: erreur lecture")
        else:
            resultats.append(f"  {f}: INTROUVABLE")

    return "Verification integrite:\n" + "\n".join(resultats)
