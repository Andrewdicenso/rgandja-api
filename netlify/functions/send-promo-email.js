const axios = require('axios');

exports.handler = async (event) => {
  // Configura la chiave API di Brevo salvata su Netlify
  const BREVO_API_KEY = process.env.BREVO_API_KEY;

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { customerEmail, customerName } = JSON.parse(event.body);

    const data = {
      sender: { name: "Andrew Di Censo - RGandja", email: "info@rgandja.com" },
      to: [{ email: customerEmail, name: customerName }],
      subject: "🎁 La tua Promozione RGandja è qui!",
      htmlContent: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
          <h2>Ciao ${customerName},</h2>
          <p>Grazie per esserti interessato alla nostra promozione esclusiva.</p>
          <p>In allegato o tramite questo link puoi accedere ai dettagli del protocollo richiesto.</p>
          <br>
          <p>A presto,<br><strong>Andrew Di Censo</strong></p>
        </div>
      `
    };

    await axios.post('https://api.brevo.com/v3/smtp/email', data, {
      headers: {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json'
      }
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Email promozionale inviata!" })
    };

  } catch (error) {
    return { 
      statusCode: 500, 
      body: JSON.stringify({ error: error.message }) 
    };
  }
};