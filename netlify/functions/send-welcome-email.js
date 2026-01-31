const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return { statusCode: 405, body: "Method Not Allowed" };

  const { customerEmail, customerName, planName } = JSON.parse(event.body);

  try {
    await resend.emails.send({
      from: 'RGandja Enterprise <info@mail.rgandja.com>', 
      to: [customerEmail],
      subject: '🛡️ Benvenuto nel Protocollo RGD-Alpha',
      html: `
        <div style="font-family: sans-serif;">
          <h2 style="color: #d4af37;">Benvenuto nel sistema, ${customerName}</h2>
          <p>La tua licenza per il <strong>${planName}</strong> è stata attivata con successo.</p>
          <p>I nostri cluster ad Atene stanno inizializzando il tuo nodo dedicato.</p>
          <br>
          <p>Saluti,<br><strong>Andrew Di Censo</strong></p>
        </div>
      `
    });
    return { statusCode: 200, body: JSON.stringify({ message: "Email inviata" }) };
  } catch (error) {
    return { statusCode: 500, body: JSON.stringify({ error: error.message }) };
  }
};