const axios = require('axios');

exports.handler = async (event) => {
  const SECRET_KEY = process.env.REVOLUT_SECRET_KEY;
  
  // Verifichiamo che la richiesta sia un POST
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    // Leggiamo i dati inviati dal tuo sito (email e nome del cliente)
    const { customerEmail, customerName, amount } = JSON.parse(event.body);

    // 1. CREAZIONE ORDINE SU REVOLUT
    const revolutResponse = await axios.post('https://merchant.revolut.com/api/1.0/orders', 
    {
      amount: amount || 1000, // Usa l'importo inviato o 10.00 EUR come default
      currency: 'EUR'
    }, 
    {
      headers: {
        'Authorization': `Bearer ${SECRET_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    const public_id = revolutResponse.data.public_id;

    // 2. INVIO EMAIL AUTOMATICA (Tramite la tua funzione send-welcome-email)
    // Usiamo l'URL interno di Netlify per chiamare l'altra funzione
    try {
      await axios.post(`${process.env.URL}/.netlify/functions/send-welcome-email`, {
        customerEmail: customerEmail,
        customerName: customerName,
        planName: 'Protocollo RGD-Alpha'
      });
    } catch (emailError) {
      console.error("Errore invio email:", emailError.message);
      // Non blocchiamo il pagamento se l'email fallisce, ma lo segnamo nei log
    }

    // Restituiamo il public_id per aprire il checkout sul sito
    return {
      statusCode: 200,
      body: JSON.stringify({ public_id: public_id })
    };

  } catch (error) {
    return { 
      statusCode: 500, 
      body: JSON.stringify({ error: error.message }) 
    };
  }
};