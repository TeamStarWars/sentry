import time, os, subprocess, json

def monitorer(duree=30):
    try:
        fin = time.time() + duree
        while time.time() < fin:
            os.system("cls" if os.name == "nt" else "clear")
            print("=== Sentry MONITOR (Ctrl+C pour quitter) ===\n")

            try:
                r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_OperatingSystem | Select TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"],
                    capture_output=True, text=True, timeout=5)
                m = json.loads(r.stdout) if r.stdout.strip() else {}
                if isinstance(m, dict):
                    total = round(int(m.get('TotalVisibleMemorySize', 0)) / (1024*1024), 2)
                    free = round(int(m.get('FreePhysicalMemory', 0)) / (1024*1024), 2)
                    used = round(total - free, 2)
                    pct = round((used / total) * 100, 1) if total > 0 else 0
                    barre = "#" * int(pct // 5) + "-" * (20 - int(pct // 5))
                    print(f"RAM: [{barre}] {pct}% ({used}/{total} Go)")
            except:
                print("RAM: N/A")

            try:
                r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process | Sort CPU -Descending | Select -First 5 Name,Id,CPU,@{N='RAM_MB';E={[math]::Round($_.WorkingSet/1MB)}} | ConvertTo-Json"],
                    capture_output=True, text=True, timeout=5)
                data = json.loads(r.stdout) if r.stdout.strip() else []
                if not isinstance(data, list): data = [data]
                print("\nTop 5 CPU:")
                for p in data[:5]:
                    if isinstance(p, dict):
                        print(f"  {p.get('Name','?')}.exe CPU:{p.get('CPU',0):.1f}s RAM:{p.get('RAM_MB',0)}MB")
            except:
                pass

            try:
                r = subprocess.run(["netstat", "-n"], capture_output=True, text=True, encoding="cp1252", errors="replace", timeout=3)
                etablies = [l for l in r.stdout.split("\n") if "ESTABLISHED" in l]
                print(f"\nConnexions etablies: {len(etablies)}")
            except:
                pass

            time.sleep(2)
        return "Monitoring termine"
    except KeyboardInterrupt:
        return "Monitoring interrompu"
    except Exception as e:
        return f"Erreur monitor: {e}"
