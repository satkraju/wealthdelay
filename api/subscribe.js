const nodemailer = require('nodemailer');

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { email, result, scenario } = req.body || {};
  if (!email) return res.status(400).json({ error: 'email required' });

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: 'satkraju@gmail.com',
        pass: process.env.GMAIL_APP_PASS
      }
    });

    await transporter.sendMail({
      from: '"WealthDelay Leads" <satkraju@gmail.com>',
      to: 'satkraju@gmail.com',
      subject: `New subscriber: ${email} — result ${result}`,
      html: `
        <div style="font-family:sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#16A34A">New WealthDelay Subscriber</h2>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="padding:8px;color:#666;width:120px">Email</td><td style="padding:8px;font-weight:700">${email}</td></tr>
            <tr style="background:#f9f9f9"><td style="padding:8px;color:#666">Result</td><td style="padding:8px;font-weight:700;color:#DC2626">${result}</td></tr>
            <tr><td style="padding:8px;color:#666">Scenario</td><td style="padding:8px">${scenario}</td></tr>
            <tr style="background:#f9f9f9"><td style="padding:8px;color:#666">Time</td><td style="padding:8px">${new Date().toLocaleString('en-US',{timeZone:'America/New_York'})}</td></tr>
          </table>
        </div>
      `
    });

    console.log(`email_capture: ${email} | ${result} | ${scenario}`);
    res.status(200).json({ ok: true });
  } catch (err) {
    console.error('subscribe error:', err.message);
    res.status(500).json({ error: 'failed' });
  }
}
