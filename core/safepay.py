import subprocess, os, tempfile, json

def lancer_navigateur_securise(url=None):
    if not url:
        url = "about:blank"
    try:
        profile_dir = os.path.join(tempfile.gettempdir(), "sentry_safepay_profile")
        os.makedirs(profile_dir, exist_ok=True)

        prefs = {
            "disable": [
                "--no-first-run", "--disable-sync", "--disable-extensions",
                "--disable-plugins", "--incognito", "--disable-notifications",
                "--disable-geolocation", "--disable-webgl", "--disable-webcerts",
                "--disable-webrtc", "--safe-plugins", "--disable-reading-from-canvas",
                "--disable-3d-apis", "--disable-bundled-ppapi-flash",
                "--disable-save-password-bubble", "--disable-password-generation",
                "--disable-breakingpad", "--disable-default-apps",
                "--disable-background-networking", "--no-default-browser-check",
                "--disable-component-extensions-with-background-pages"
            ],
            "enable": ["--enable-strict-powerful-feature-restrictions"]
        }

        chrome_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]

        chrome = None
        for p in chrome_paths:
            if os.path.isfile(p):
                chrome = p
                break

        edge_path = os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe")
        firefox_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Mozilla Firefox", "firefox.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Mozilla Firefox", "firefox.exe"),
        ]

        if chrome:
            args = [chrome, f"--user-data-dir={profile_dir}"] + prefs["disable"] + [url]
            subprocess.Popen(args)
            return f"SafePay lance (Chrome): {url}"
        elif os.path.isfile(edge_path):
            args = [edge_path, f"--user-data-dir={profile_dir}", "--inprivate", "--disable-extensions", url]
            subprocess.Popen(args)
            return f"SafePay lance (Edge): {url}"
        else:
            for fp in firefox_paths:
                if os.path.isfile(fp):
                    args = [fp, "-private", "-new-tab", url]
                    subprocess.Popen(args)
                    return f"SafePay lance (Firefox): {url}"
            return "Aucun navigateur trouve. Installez Chrome, Edge ou Firefox."
    except Exception as e:
        return f"Erreur: {e}"

def nettoyer_profil():
    profile_dir = os.path.join(tempfile.gettempdir(), "sentry_safepay_profile")
    try:
        import shutil
        if os.path.isdir(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
            return "Profil SafePay nettoye"
        return "Aucun profil a nettoyer"
    except Exception as e:
        return f"Erreur: {e}"
