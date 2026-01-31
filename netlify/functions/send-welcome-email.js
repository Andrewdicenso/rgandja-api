const { Resend } = require('resend');

// Inizializza Resend usando la chiave salvata su Netlify
const resend = new Resend(process.env.RESEND_API_KEY);

exports.handler = async (event) => {
  // Accetta solo richieste POST
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    // Recupera i dati dal frontend
    const { customerEmail, customerName, planName } = JSON.parse(event.body);

    // Invio email tramite il sottodominio verificato
    const { data, error } = await resend.emails.send({
      from: 'Andrew - RGandja <info@mail.rgandja.com>', 
      to: [customerEmail],
      subject: '🛡️ Protocollo RGD-Alpha: Accesso Autorizzato',
      html: `
        <div style="font-family: 'Helvetica', sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee;">
          <h2 style="color: #111; text-align: center;">Benvenuto nel Sistema, ${customerName}</h2>
          <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
          <p>Siamo lieti di confermare che l'attivazione del tuo <strong>${planName}</strong> è stata completata con successo.</p>
          <p>I nostri sistemi stanno inizializzando i parametri del tuo nodo dedicato. Riceverai a breve le credenziali di accesso crittografate in una comunicazione separata.</p>
          <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; font-size: 0.9em; color: #666;"><strong>Dettagli Ordine:</strong><br>
            Servizio: ${planName}<br>
            Stato: Attivo</p>
          </div>
          <p>Se non hai richiesto tu questa attivazione, contatta il supporto a supporto@rgandja.it.</p>
          <br>
          <p>Cordiali saluti,<br><strong>Andrew Di Censo</strong><br>RGandja Enterprise</p>
        </div>
      `
    });

    if (error) {
      throw new Error(error.message);
    }

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Email inviata!", id: data.id })
    };

  } catch (error) {
    console.error("Errore Invio:", error.message);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Errore durante l'invio" })
    };
  }
};