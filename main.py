import json
import os
import math
import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

app = FastAPI(title="RGandja Neural Core", version="5.0.0")

# ============================================================
# CONFIGURAZIONE & CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rgandja.com", "https://www.rgandja.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inizializzazione Database (Previene errori di file mancante)
def init_db(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump([], f)

init_db("users.json")
init_db("analytics.json")

# ============================================================
# MODELLI DATI
# ============================================================
class InputData(BaseModel):
    algoritmo: str           # junior / pmi / enterprise
    budget: float
    resilienza: bool
    ore_assenze: float
    standby_watt: float
    metri_quadri: float
    num_dipendenti: int

class PdfRequest(BaseModel):
    algoritmo: str
    budget: float
    risultato_testuale: str
    premium: bool
    email: Optional[str] = None

class ReportEmailRequest(BaseModel):
    email: str
    pdf_link: str

# ============================================================
# IL CUORE: RGD-ALPHA ANALYTICS ENGINE
# ============================================================
class RGDAlphaEngine:
    @staticmethod
    def simula_successo_espansione(data: InputData) -> dict:
        k_map = {"junior": 1.12, "pmi": 1.38, "enterprise": 1.72}
        k = k_map.get(data.algoritmo.lower(), 1.20)

        # Calcolo Attrito Operativo
        attrito = (data.ore_assenze * 0.2) + ((data.standby_watt * data.metri_quadri) / 5000)
        stabilita = 0.98 if data.resilienza else 0.75

        # Proiezione Successo
        proiezione_lorda = data.budget * k
        incremento_netto = round((proiezione_lorda - data.budget) * stabilita, 2)
        
        # Probabilità (Sigmoide)
        prob_successo = round(100 / (1 + math.exp(-0.08 * (100 - attrito))), 2)
        efficienza = max(0, round(100 - attrito, 2))

        return {
            "incremento_guadagno": incremento_netto,
            "probabilita_successo": prob_successo,
            "efficienza_neurale": efficienza,
            "vettore": "Espansione" if incremento_netto > (data.budget * 0.1) else "Mantenimento"
        }

# ============================================================
# API ENDPOINTS - LOGICA COMMERCIALE & CALCOLO
# ============================================================
@app.post("/calcola")
def calcola(data: InputData):
    try:
        analisi = RGDAlphaEngine.simula_successo_espansione(data)
        
        risultato_testo = f"""
> PROTOCOLLO RGD-ALPHA V5 ACTIVATED
> TARGET: SUCCESS OPTIMIZATION ({data.algoritmo.upper()})

[ANALISI STATISTICA]
- Efficienza Neurale: {analisi['efficienza_neurale']}%
- Neutralizzazione Rischio: {analisi['probabilita_successo']}%

[PROIEZIONE DI SUCCESSO]
→ Incremento Guadagno Stimato: €{analisi['incremento_guadagno']:,.2f}
→ Vettore Aziendale: {analisi['vettore']}
""".strip()

        return {
            "risultato": risultato_testo,
            "kpi": analisi,
            "pdf_link": "https://rgandja.com/static/preview.pdf",
            "is_premium_locked": data.algoritmo.lower() != "junior"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/limiti")
def config_limiti(piano: str):
    limiti = {
        "Junior": {"analisi_mensili": 10, "pdf": "Basic", "supporto": "Ticket", "nodi": 128},
        "PMI": {"analisi_mensili": 50, "pdf": "Advanced", "supporto": "Prioritario 24h", "nodi": 1024},
        "Enterprise": {"analisi_mensili": "Illimitate", "pdf": "Full", "supporto": "Advisory Dedicato", "nodi": "HPC"}
    }
    piano_norm = piano.title() if piano.lower() != "pmi" else "PMI"
    if piano_norm not in limiti:
        raise HTTPException(status_code=404, detail="Piano non trovato")
    return limiti[piano_norm]

# ============================================================
# GESTIONE UTENTI & ANALYTICS
# ============================================================
@app.post("/login")
def login(email: str, password: str):
    with open("users.json", "r") as f:
        users = json.load(f)
    for u in users:
        if u["email"] == email and u["password"] == password:
            return {"status": "success", "licenza": u["licenza"], "email": u["email"]}
    raise HTTPException(status_code=401, detail="Credenziali non valide")

@app.post("/analytics/salva")
def salva_analisi(email: str, incremento: float, successo: float, efficienza: float):
    try:
        with open("analytics.json", "r") as f: storico = json.load(f)
        storico.append({
            "email": email, "incremento": incremento, "successo": successo, 
            "efficienza": efficienza, "timestamp": datetime.datetime.utcnow().isoformat()
        })
        with open("analytics.json", "w") as f: json.dump(storico, f, indent=2)
        return {"status": "success"}
    except Exception:
        raise HTTPException(status_code=500, detail="Errore archiviazione")

# ============================================================
# EMAIL & STATUS
# ============================================================
def invia_email_brevo(destinatario: str, oggetto: str, contenuto: str):
    config = sib_api_v3_sdk.Configuration()
    config.api_key['api-key'] = os.getenv('BREVO_API_KEY')
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(config))
    
    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        subject=oggetto,
        html_content=f"<html><body>{contenuto}</body></html>",
        sender={"email": "intelligence@rgandja.com", "name": "RGandja Neural Engine"}
    )
    try:
        api_instance.send_transac_email(email)
        return True
    except ApiException:
        return False

@app.post("/email/invia-report")
def email_invia_report(req: ReportEmailRequest):
    if invia_email_brevo(req.email, "Report Pronto", f"Link: {req.pdf_link}"):
        return {"status": "inviata"}
    return {"status": "errore"}

@app.get("/status")
def status():
    return {"engine": "RGandja Neural Core v5.0", "status": "Operational", "time": datetime.datetime.utcnow().isoformat()}