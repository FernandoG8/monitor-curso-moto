# Revisa cupo del curso MOTOCILISTA (SPSC Campeche) y avisa por ntfy.sh
import json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone

CURSO = os.environ.get("CURSO", "MOTO")
TOPIC = os.environ["NTFY_TOPIC"]
ESTADO = "notificados.json"
PAGINA = "https://www.spsc.campeche.gob.mx/cursos/"
API = PAGINA + "wp-admin/admin-ajax.php?action=wpamelia_api&call=/events&page=1"

hoy = datetime.now(timezone(timedelta(hours=-6))).date()
fin = hoy + timedelta(days=30)
req = urllib.request.Request(f"{API}&dates[]={hoy}&dates[]={fin}", headers={"User-Agent": "Mozilla/5.0"})
eventos = json.load(urllib.request.urlopen(req, timeout=60))["data"]["events"]

avisados = json.load(open(ESTADO)) if os.path.exists(ESTADO) else []

def ntfy(titulo, texto, prioridad="urgent"):
    r = urllib.request.Request(f"https://ntfy.sh/{TOPIC}", data=texto.encode(), headers={
        "Title": titulo.encode("utf-8").decode("latin-1"), "Priority": prioridad,
        "Tags": "motorcycle", "Click": PAGINA, "Actions": f"view, Inscribirme, {PAGINA}"})
    urllib.request.urlopen(r, timeout=30)

if "--prueba" in sys.argv:
    ntfy("Prueba monitor moto", "Las notificaciones funcionan.", "default")

for e in eventos:
    inicio = e["periods"][0]["periodStart"]
    print(f'{e["name"]} inicio={inicio} lugares={e["places"]}/{e["maxCapacity"]} inscribible={e["bookable"]}')
    if CURSO not in e["name"].upper() or not e["bookable"] or e["places"] <= 0:
        continue
    if e["id"] in avisados:
        continue
    ntfy(f'Cupo {e["name"]}: {e["places"]} lugares',
         f'Curso del {inicio[:10]} ({inicio[11:16]} hrs). Inscribete ya.')
    avisados.append(e["id"])

json.dump(avisados, open(ESTADO, "w"))
