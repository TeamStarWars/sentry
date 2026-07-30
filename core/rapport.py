import datetime
from core import network as net, antivirus as av, process as proc, system as sysinfo, security as sec, wifi, journaux as logs

def generer(chemin="rapport_vindex.html"):
    try:
        sections = [
            "<h1>Rapport Vindex</h1>",
            f"<p>Genere le {datetime.datetime.now()}</p>",
        ]

        sections.append("<h2>Systeme</h2><pre>")
        sections.append(sysinfo.diagnostic())
        sections.append("</pre>")

        sections.append("<h2>Memoire</h2><pre>")
        sections.append(sysinfo.memoire())
        sections.append("</pre>")

        sections.append("<h2>Top Processus (CPU)</h2><pre>")
        sections.append(proc.liste_processus("cpu"))
        sections.append("</pre>")

        sections.append("<h2>Connexions actives</h2><pre>")
        sections.append(net.connexions(30))
        sections.append("</pre>")

        sections.append("<h2>Ports en ecoute</h2><pre>")
        sections.append(sec.ports_ecoute())
        sections.append("</pre>")

        sections.append("<h2>Windows Defender</h2><pre>")
        sections.append(av.statut_defenseur())
        sections.append("</pre>")

        sections.append("<h2>Services actifs</h2><pre>")
        sections.append(sysinfo.services())
        sections.append("</pre>")

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Rapport Vindex</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }}
h1 {{ color: #0d6efd; }}
h2 {{ color: #198754; border-bottom: 2px solid #198754; padding-bottom: 5px; }}
pre {{ background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow-x: auto; }}
</style></head>
<body>
{"".join(sections)}
</body></html>"""

        with open(chemin, "w", encoding="utf-8") as f:
            f.write(html)
        return f"Rapport genere: {chemin}"
    except Exception as e:
        return f"Erreur rapport: {e}"
