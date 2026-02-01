const axios = require('axios');

exports.handler = async (event) => {
  // Recupera la chiave API di Brevo dalle variabili d'ambiente di Netlify
  const BREVO_API_KEY = process.env.BREVO_API_KEY;

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { customerEmail, customerName } = JSON.parse(event.body);

    // --- 1. EMAIL PER IL CLIENTE ---
    const customerData = {
      sender: { name: "Andrew Di Censo - RGandja", email: "info@rgandja.com" },
      to: [{ email: customerEmail, name: customerName }],
      subject: "🎁 La tua Promozione RGandja è qui!",
      htmlContent: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee;">
          <h2 style="color: #111;">Ciao ${customerName},</h2>
          <p>Grazie per esserti interessato alla nostra promozione esclusiva.</p>
          <p>Il tuo posto è stato riservato con successo.</p>
          <br>
          <p>A presto,<br><strong>Andrew Di Censo</strong></p>
        </div>
      `
    };

    // --- 2. EMAIL DI NOTIFICA PER TE (ADMIN) ---
    const adminData = {
      sender: { name: "Sistema Notifiche RGandja", email: "info@rgandja.com" },
      to: [{ email: "info@rgandja.com", name: "Andrew Admin" }],
      subject: `🚨 NUOVA PRENOTAZIONE: ${customerName}`,
      htmlContent: `
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 2px solid #f00;">
          <h2 style="color: #d00;">Nuovo Lead dal Sito!</h2>
          <p><strong>Nome:</strong> ${customerName}</p>
          <p><strong>Email:</strong> ${customerEmail}</p>
          <p><strong>Azione:</strong> Richiesta Promozione</p>
        </div>
      `
    };

    // Invio al cliente
    await axios.post('https://api.brevo.com/v3/smtp/email', customerData, {
      headers: { 'api-key': BREVO_API_KEY, 'Content-Type': 'application/json' }
    });

    // Invio notifica a te
    await axios.post('https://api.brevo.com/v3/smtp/email', adminData, {
      headers: { 'api-key': BREVO_API_KEY, 'Content-Type': 'application/json' }
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Invio cliente e notifica admin completati!" })
    };

  } catch (error) {
    console.error("Errore invio Brevo:", error.message);
    return { 
      statusCode: 500, 
      body: JSON.stringify({ error: error.message }) 
    };
  }
};