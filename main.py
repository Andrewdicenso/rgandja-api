from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import datetime

app = FastAPI(title="RGandja Neural API", version="1.0.0")

# ==========================
# CORS (per il sito RGandja)
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # quando hai dominio definitivo, puoi mettere ["https://rgandja.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# MODELLI DATI
# ==========================

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


# ==========================
# FUNZIONI INTERNE (PLACEHOLDER)
# Qui inseriremo il vero algoritmo RGD-Alpha
# ==========================

def calcolo_rgandja_core(data: InputData) -> dict:
    """
    Placeholder logico: qui in futuro mettiamo il vero motore RGD-Alpha.
    Ora restituisce solo una simulazione coerente.
    """
    risparmio_stimato = round(data.budget * 0.12, 2)
    efficienza_neurale = max(0, round(100 - data.ore_assenze * 0.8, 2))
    intensita_energetica = round(data.standby_watt * data.metri_quadri / 1000, 2)

    risultato = f"""
> RGandja Neural Engine v1.0
> Algoritmo selezionato: {data.algoritmo.upper()}

Budget annuale analizzato: €{data.budget:,.2f}
Numero dipendenti: {data.num_dipendenti}
Superficie operativa: {data.metri_quadri} mq
Assenze settimanali: {data.ore_assenze} ore
Standby energetico stimato: {data.standby_watt} W

→ Risparmio potenziale stimato: €{risparmio_stimato:,.2f}
→ Efficienza neurale stimata: {efficienza_neurale}%
→ Intensità energetica: {intensita_energetica} kWh/unità

Nota: Questo output è una preview strategica. I valori finali dipendono dalla calibrazione completa del Protocollo RGD-Alpha.
""".strip()

    return {
        "risultato": risultato,
        "risparmio_stimato": risparmio_stimato,
        "efficienza_neurale": efficienza_neurale,
        "intensita_energetica": intensita_energetica,
    }


def genera_link_pdf_placeholder(premium: bool) -> str:
    """
    Placeholder: in futuro qui collegheremo il vero generatore PDF.
    Ora restituisce un URL fittizio coerente.
    """
    if premium:
        return "https://rgandja.com/static/report-premium-sample.pdf"
    else:
        return "https://rgandja.com/static/report-preview-sample.pdf"


# ==========================
# 1) API /calcola
# ==========================
@app.post("/calcola")
def calcola(data: InputData):
    core = calcolo_rgandja_core(data)

    # Logica paywall base: premium solo per alcuni casi (placeholder)
    is_premium_locked = True

    pdf_link = genera_link_pdf_placeholder(premium=False)

    return {
        "risultato": core["risultato"],
        "is_premium_locked": is_premium_locked,
        "pdf_link": pdf_link,
        "kpi": {
            "risparmio_stimato": core["risparmio_stimato"],
            "efficienza_neurale": core["efficienza_neurale"],
            "intensita_energetica": core["intensita_energetica"],
        }
    }


# ==========================
# 2) API /genera-pdf  (Premium)
# ==========================
@app.post("/genera-pdf")
def genera_pdf(req: PdfRequest):
    pdf_link = genera_link_pdf_placeholder(premium=True)

    return {
        "status": "ok",
        "premium": req.premium,
        "pdf_link": pdf_link
    }


# ==========================
# 3) API /preview-pdf  (Free)
# ==========================
@app.post("/preview-pdf")
def preview_pdf(req: PdfRequest):
    pdf_link = genera_link_pdf_placeholder(premium=False)

    return {
        "status": "ok",
        "premium": False,
        "pdf_link": pdf_link
    }


# ==========================
# 4) API /status
# ==========================
@app.get("/status")
def status():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    return {
        "status": "online",
        "engine": "RGandja Neural Core v1.0.0",
        "timestamp": now
    }
import json
import os

# -----------------------------
# API /register
# -----------------------------
@app.post("/register")
def register(email: str, password: str):
    path = "users.json"
    if not os.path.exists(path):
        return {"error": "File users.json non trovato"}

    with open(path, "r") as f:
        users = json.load(f)

    if any(u["email"] == email for u in users):
        return {"error": "Utente già esistente"}

    new_user = {
        "email": email,
        "password": password,
        "licenza": "Bronzo",
        "scadenza": "2026-06-30"
    }
    users.append(new_user)

    with open(path, "w") as f:
        json.dump(users, f, indent=2)

    return {"status": "registrazione completata", "licenza": "Bronzo"}

# -----------------------------
# API /login
# -----------------------------
@app.post("/login")
def login(email: str, password: str):
    path = "users.json"
    if not os.path.exists(path):
        return {"error": "File users.json non trovato"}

    with open(path, "r") as f:
        users = json.load(f)

    for u in users:
        if u["email"] == email and u["password"] == password:
            return {"status": "accesso riuscito", "licenza": u["licenza"]}
    
    return {"error": "Credenziali non valide"}

# -----------------------------
# API /licenza/valida
# -----------------------------
@app.get("/licenza/valida")
def licenza_valida(email: str):
    path = "users.json"
    if not os.path.exists(path):
        return {"error": "File users.json non trovato"}

    with open(path, "r") as f:
        users = json.load(f)

    for u in users:
        if u["email"] == email:
            return {
                "licenza": u["licenza"],
                "scadenza": u["scadenza"],
                "premium": u["licenza"] in ["Argento", "Oro"]
            }

    return {"error": "Utente non trovato"}

# -----------------------------
# API /licenza/attiva
# -----------------------------
@app.post("/licenza/attiva")
def licenza_attiva(email: str, nuova_licenza: str):
    path = "users.json"
    if not os.path.exists(path):
        return {"error": "File users.json non trovato"}

    with open(path, "r") as f:
        users = json.load(f)

    for u in users:
        if u["email"] == email:
            u["licenza"] = nuova_licenza
            u["scadenza"] = "2026-12-31"

            with open(path, "w") as f:
                json.dump(users, f, indent=2)

            return {"status": "licenza aggiornata", "licenza": nuova_licenza}

    return {"error": "Utente non trovato"}

# -----------------------------
# API /licenza/dettagli
# -----------------------------
@app.get("/licenza/dettagli")
def licenza_dettagli(email: str):
    return licenza_valida(email)
# -----------------------------
# API /analytics/salva
# -----------------------------
@app.post("/analytics/salva")
def salva_analisi(email: str, risultato: str, risparmio: float, efficienza: float):
    path = "analytics.json"
    if not os.path.exists(path):
        return {"error": "File analytics.json non trovato"}

    with open(path, "r") as f:
        storico = json.load(f)

    nuovo_record = {
        "email": email,
        "risultato": risultato,
        "risparmio": risparmio,
        "efficienza": efficienza,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    storico.append(nuovo_record)

    with open(path, "w") as f:
        json.dump(storico, f, indent=2)

    return {"status": "analisi salvata"}

# -----------------------------
# API /analytics/storico
# -----------------------------
@app.get("/analytics/storico")
def storico_utente(email: str):
    path = "analytics.json"
    if not os.path.exists(path):
        return {"error": "File analytics.json non trovato"}

    with open(path, "r") as f:
        storico = json.load(f)

    filtrati = [r for r in storico if r["email"] == email]

    return {"storico": filtrati, "totale": len(filtrati)}

# -----------------------------
# API /analytics/kpi
# -----------------------------
@app.get("/analytics/kpi")
def kpi_utente(email: str):
    path = "analytics.json"
    if not os.path.exists(path):
        return {"error": "File analytics.json non trovato"}

    with open(path, "r") as f:
        storico = json.load(f)

    filtrati = [r for r in storico if r["email"] == email]

    if not filtrati:
        return {"error": "Nessuna analisi trovata"}

    media_risparmio = round(sum(r["risparmio"] for r in filtrati) / len(filtrati), 2)
    media_efficienza = round(sum(r["efficienza"] for r in filtrati) / len(filtrati), 2)

    return {
        "totale_analisi": len(filtrati),
        "media_risparmio": media_risparmio,
        "media_efficienza": media_efficienza
    }
# ==============================
# MODULO 4 — EMAIL & NOTIFICHE
# ==============================

def invia_email_placeholder(destinatario: str, oggetto: str, contenuto: str):
    """
    Placeholder: in futuro qui collegheremo l'API Brevo.
    Ora simula l'invio email.
    """
    print(f"[EMAIL SIMULATA] A: {destinatario} | Oggetto: {oggetto}")
    print(contenuto)
    return True


# -----------------------------
# API /email/invia-report
# -----------------------------
@app.post("/email/invia-report")
def email_invia_report(email: str, pdf_link: str):
    oggetto = "Il tuo Report RGandja è pronto"
    contenuto = f"""
Ciao,

il tuo report è stato generato con successo.

Puoi scaricarlo qui:
{pdf_link}

Grazie per aver utilizzato RGandja Decision Systems.
"""

    invia_email_placeholder(email, oggetto, contenuto)

    return {"status": "email inviata", "destinatario": email}


# -----------------------------
# API /email/onboarding
# -----------------------------
@app.post("/email/onboarding")
def email_onboarding(email: str):
    oggetto = "Benvenuto in RGandja"
    contenuto = f"""
Ciao,

benvenuto nella piattaforma RGandja Decision Intelligence.

La tua registrazione è attiva e puoi iniziare subito a utilizzare il sistema.

Per assistenza: support@rgandja.com
"""

    invia_email_placeholder(email, oggetto, contenuto)

    return {"status": "email onboarding inviata", "destinatario": email}


# -----------------------------
# API /email/alert-licenza
# -----------------------------
@app.post("/email/alert-licenza")
def email_alert_licenza(email: str, giorni_rimanenti: int):
    oggetto = "La tua licenza RGandja sta per scadere"
    contenuto = f"""
Ciao,

la tua licenza RGandja scadrà tra {giorni_rimanenti} giorni.

Per rinnovarla, accedi alla tua area personale o contatta support@rgandja.com.
"""

    invia_email_placeholder(email, oggetto, contenuto)

    return {"status": "alert licenza inviato", "destinatario": email}
# ==============================
# MODULO 5 — SISTEMA & SICUREZZA
# ==============================

# -----------------------------
# API /healthcheck
# -----------------------------
@app.get("/healthcheck")
def healthcheck():
    return {
        "status": "online",
        "engine": "RGandja Neural Core v1.0.0",
        "uptime": "OK",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }


# -----------------------------
# Funzione interna per log
# -----------------------------
def salva_log(tipo: str, messaggio: str):
    path = "logs.json"
    if not os.path.exists(path):
        return False

    with open(path, "r") as f:
        logs = json.load(f)

    nuovo_log = {
        "tipo": tipo,
        "messaggio": messaggio,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    logs.append(nuovo_log)

    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

    return True


# -----------------------------
# API /log/errori
# -----------------------------
@app.post("/log/errori")
def log_errori(messaggio: str):
    salva_log("errore", messaggio)
    return {"status": "errore registrato"}


# -----------------------------
# API /log/eventi
# -----------------------------
@app.post("/log/eventi")
def log_eventi(messaggio: str):
    salva_log("evento", messaggio)
    return {"status": "evento registrato"}


# -----------------------------
# API /config/versione
# -----------------------------
@app.get("/config/versione")
def config_versione():
    return {
        "engine": "RGandja Neural Core",
        "versione": "1.0.0",
        "protocollo": "RGD-Alpha"
    }


# -----------------------------
# API /config/limiti
# -----------------------------
@app.get("/config/limiti")
def config_limiti(piano: str):
    limiti = {
        "Bronzo": {
            "analisi_mensili": 10,
            "pdf": False,
            "supporto": "Email"
        },
        "Argento": {
            "analisi_mensili": 50,
            "pdf": True,
            "supporto": "Prioritario"
        },
        "Oro": {
            "analisi_mensili": "Illimitate",
            "pdf": True,
            "supporto": "Premium 24/7"
        }
    }

    if piano not in limiti:
        return {"error": "Piano non valido"}

    return limiti[piano]
# ==========================
# Endpoint per demo RGandja
# ==========================

class InputData(BaseModel):
    nome: Optional[str]
    settore: Optional[str]
    dipendenti: Optional[int]

@app.post("/pmi")
def elabora_pmi(data: InputData):
    # Simulazione di elaborazione
    risultato = {
        "nome": data.nome,
        "settore": data.settore,
        "dipendenti": data.dipendenti,
        "valutazione": "Eccellente",
        "timestamp": datetime.datetime.now().isoformat()
    }
    return risultato
