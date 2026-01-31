const axios = require('axios');

exports.handler = async (event) => {
  // Legge la chiave dalle Environment Variables di Netlify per massima sicurezza
  const SECRET_KEY = process.env.REVOLUT_SECRET_KEY;

  try {
    const response = await axios.post('https://merchant.revolut.com/api/1.0/orders', 
    {
      amount: 1000, // Esempio: 10.00 EUR (espresso in centesimi)
      currency: 'EUR'
    }, 
    {
      headers: {
        'Authorization': `Bearer ${SECRET_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    return {
      statusCode: 200,
      body: JSON.stringify({ public_id: response.data.public_id })
    };
  } catch (error) {
    return { 
      statusCode: 500, 
      body: JSON.stringify({ error: error.message }) 
    };
  }
};