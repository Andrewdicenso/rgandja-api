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

# ============================================================
# MODELLI DATI (STRUTTURA RGD-ALPHA)
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
        # Moltiplicatori di Crescita basati sull'Algoritmo
        k_map = {"junior": 1.12, "pmi": 1.38, "enterprise": 1.72}
        k = k_map.get(data.algoritmo.lower(), 1.20)

        # Calcolo Attrito Operativo (Costi Invisibili)
        # Più metri quadri e standby watt ci sono, più l'efficienza scende
        attrito = (data.ore_assenze * 0.2) + ((data.standby_watt * data.metri_quadri) / 5000)
        
        # Fattore Resilienza (Riduzione volatilità)
        stabilita = 0.98 if data.resilienza else 0.75

        # Proiezione Guadagno Netto (Successo Aziendale)
        proiezione_lorda = data.budget * k
        incremento_netto = round((proiezione_lorda - data.budget) * stabilita, 2)
        
        # Probabilità Deterministica di Successo (Sigmoide)
        prob_successo = round(100 / (1 + math.exp(-0.08 * (100 - attrito))), 2)
        
        # Efficienza Neurale (Ottimizzazione Risorse)
        efficienza = max(0, round(100 - attrito, 2))

        return {
            "incremento_guadagno": incremento_netto,
            "probabilita_successo": prob_successo,
            "efficienza_neurale": efficienza,
            "vettore": "Espansione" if incremento_netto > (data.budget * 0.1) else "Mantenimento"
        }

# ============================================================
# API ENDPOINTS - CALCOLO & STRATEGIA
# ============================================================
@app.post("/calcola")
def calcola(data: InputData):
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

Nota: L'algoritmo ha identificato un percorso di espansione a basso attrito.
""".strip()

    return {
        "risultato": risultato_testo,
        "kpi": analisi,
        "pdf_link": "https://rgandja.com/static/preview.pdf",
        "is_premium_locked": data.algoritmo.lower() != "junior"
    }

# ============================================================
# GESTIONE LICENZE & UTENTI
# ============================================================
def verifica_licenza(email: str) -> bool:
    path = "users.json"
    if not os.path.exists(path): return False
    with open(path, "r") as f:
        users = json.load(f)
    for u in users:
        if u["email"] == email:
            return u["licenza"] in ["Argento", "Oro"]
    return False

@app.post("/login")
def login(email: str, password: str):
    path = "users.json"
    if not os.path.exists(path): return {"error": "Database non trovato"}
    with open(path, "r") as f:
        users = json.load(f)
    for u in users:
        if u["email"] == email and u["password"] == password:
            return {"status": "success", "licenza": u["licenza"], "email": u["email"]}
    return {"error": "Credenziali non valide"}

# ============================================================
# NOTIFICHE & EMAIL (INTEGRAZIONE BREVO)
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
    successo = invia_email_brevo(
        req.email, 
        "Il tuo Report Decisionale RGandja è Pronto", 
        f"L'analisi RGD-Alpha è completa. Accedi al tuo vettore di espansione qui: {req.pdf_link}"
    )
    return {"status": "inviata" if successo else "errore"}

# ============================================================
# SISTEMA & MONITORAGGIO
# ============================================================
@app.get("/status")
def status():
    return {
        "engine": "RGandja Neural Core v5.0",
        "protocol": "RGD-Alpha",
        "uptime": "Operational",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }