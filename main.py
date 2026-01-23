import json
import os
import math
import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- CONFIGURAZIONE CORE ---
app = FastAPI(
    title="RGandja Neural Engine",
    description="Sistema Decisionale RGD-Alpha per l'Efficienza Aziendale",
    version="6.2.0"
)

@app.get("/")
def read_root():
    return health()

# Sicurezza CORS: Permette al sito RGandja di dialogare con l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rgandja.com", "https://www.rgandja.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE FILES (Inizializzazione) ---
DB_FILES = ["users.json", "analytics.json", "logs.json"]
for db in DB_FILES:
    if not os.path.exists(db):
        with open(db, "w") as f:
            json.dump([], f)

# --- MODELLI DATI (Validazione Rigorosa) ---
class InputData(BaseModel):
    algoritmo: str  # junior / pmi / enterprise
    budget: float
    resilienza: bool = True
    ore_assenze: float
    standby_watt: float
    metri_quadri: float
    num_dipendenti: int

class ReportEmailRequest(BaseModel):
    email: EmailStr
    pdf_link: str

# --- LOGICA DI CALCOLO RGD-ALPHA ---
class NeuralProcessor:
    @staticmethod
    def calcola_metriche(data: InputData):
        # 1. Calcolo Attrito Energetico-Spaziale
        attrito_energetico = (data.standby_watt * data.metri_quadri) / 10000
        
        # 2. Calcolo Attrito Risorse Umane
        rapporto_assenze = data.ore_assenze / (data.num_dipendenti if data.num_dipendenti > 0 else 1)
        attrito_umano = rapporto_assenze * 2.5
        
        # 3. Indice di Efficienza Neurale (IEN)
        # Più alto è l'attrito, più basso è l'IEN
        ien = max(5, 100 - (attrito_energetico + attrito_umano))
        
        # 4. Probabilità di Successo (Funzione Sigmoide non lineare)
        # Simula il rischio reale: oltre una certa soglia di inefficienza, il sistema crolla
        prob = round(100 / (1 + math.exp(-0.15 * (ien - 50))), 2)
        
        # 5. Stima Risparmio in base all'algoritmo scelto
        coeff = {"junior": 0.08, "pmi": 0.14, "enterprise": 0.22}
        risparmio = round(data.budget * (coeff.get(data.algoritmo.lower(), 0.1)) * (1 - prob/100), 2)
        
        return {
            "ien": round(ien, 2),
            "probabilita": prob,
            "risparmio": risparmio,
            "stato": "CRITICO" if prob < 40 else "STABILE" if prob < 75 else "OTTIMALE"
        }

# --- FUNZIONI DI SERVIZIO ---
def registra_log(tipo: str, messaggio: str):
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "tipo": tipo,
        "messaggio": messaggio
    }
    with open("logs.json", "r+") as f:
        logs = json.load(f)
        logs.append(log_entry)
        f.seek(0)
        json.dump(logs[-500:], f, indent=2) # Mantiene solo gli ultimi 500 log

# --- ENDPOINT API ---

@app.post("/calcola")
async def calcola(data: InputData):
    try:
        res = NeuralProcessor.calcola_metriche(data)
        
        # Costruzione del Report Testuale Professionale
        report = f"""
> RGD-ALPHA CORE ANALYSIS COMPLETED
> PROTOCOLO: {data.algoritmo.upper()} 2026

[INDICATORI DI PERFORMANCE]
• Indice Efficienza Neurale: {res['ien']}%
• Probabilità di Successo Operativo: {res['probabilita']}%
• Risparmio Annuo Stimato: €{res['risparmio']:,.2f}

[DIAGNOSTICA]
Stato del Sistema: {res['stato']}
Il modello ha rilevato che l'ottimizzazione del capitale umano e il monitoraggio 
dei carichi passivi (Watt) possono generare un impatto immediato del {round(100 - res['probabilita'], 1)}% 
sulla resilienza aziendale.

[AZIONI RACCOMANDATE]
1. Attivazione monitoraggio nodi energetici.
2. Riorganizzazione flussi per riduzione attrito risorse.
"""
        return {
            "risultato": report.strip(),
            "kpi": res,
            "is_premium_locked": data.algoritmo.lower() != "junior" # Blocca PMI ed Enterprise
        }
    except Exception as e:
        registra_log("ERRORE", f"Errore nel calcolo: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore interno al cluster neurale.")

@app.post("/email/invia-report")
async def invia_report(req: ReportEmailRequest):
    # Nota: Assicurati di impostare la variabile d'ambiente BREVO_API_KEY sul server
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        registra_log("WARNING", "Email non inviata: API Key mancante")
        return {"status": "debug", "message": "Email simulata correttamente (API Key non configurata)"}

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": req.email}],
        subject="Il tuo Report RGandja Decision Intelligence",
        html_content=f"<h3>Analisi Completata</h3><p>Scarica la tua roadmap strategica qui: <a href='{req.pdf_link}'>REPORT PDF</a></p>",
        sender={"email": "intelligence@rgandja.com", "name": "RGandja Neural System"}
    )

    try:
        api_instance.send_transac_email(email)
        registra_log("INFO", f"Report inviato a {req.email}")
        return {"status": "success"}
    except ApiException as e:
        registra_log("ERRORE", f"Errore Brevo: {str(e)}")
        return {"status": "error", "message": "Invio fallito"}

@app.get("/healthcheck")
def health():
    return {"status": "online", "version": "6.2.0", "node": "Athens-01"}