import os, glob, json, subprocess

def extensions():
    resultats = []
    chemins = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Extensions"),
        os.path.join(os.environ.get("APPDATA", ""), "Opera Software", "Opera Stable", "Extensions"),
    ]
    for base in chemins:
        if os.path.isdir(base):
            for ext_id in os.listdir(base)[:20]:
                ext_chemin = os.path.join(base, ext_id)
                if os.path.isdir(ext_chemin):
                    for version in os.listdir(ext_chemin):
                        manifest = os.path.join(ext_chemin, version, "manifest.json")
                        if os.path.isfile(manifest):
                            try:
                                with open(manifest, "r", encoding="utf-8", errors="replace") as f:
                                    m = json.load(f)
                                nom = m.get("name", ext_id)
                                permissions = m.get("permissions", [])
                                perms_suspectes = [p for p in permissions if p in ["history", "tabs", "debugger", "webRequest", "nativeMessaging", "clipboardRead"]]
                                if perms_suspectes:
                                    resultats.append(f"{nom}: permissions risquent {', '.join(perms_suspectes)}")
                                else:
                                    resultats.append(f"{nom}: OK")
                            except:
                                pass

    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
            "Get-ChildItem -Path \"$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Downloads\" -ErrorAction SilentlyContinue | Sort LastWriteTime -Descending | Select -First 10 Name,LastWriteTime | ConvertTo-Json"],
            capture_output=True, text=True, timeout=10)
        data = json.loads(r.stdout) if r.stdout.strip() else []
        if isinstance(data, dict): data = [data]
        if data:
            resultats.append(f"\nDerniers telechargements ({len(data)}):")
            for d in data[:5]:
                if isinstance(d, dict):
                    resultats.append(f"  {d.get('Name','?')} ({str(d.get('LastWriteTime','?'))[:10]})")
    except:
        pass

    if not resultats:
        return "Aucune extension detectee"
    return "Audit navigateur:\n" + "\n".join(resultats)
