export default function handler(req, res) {
  const origin = req.headers.origin || '';
  const allowed = ['https://wealthdelay.com', 'https://www.wealthdelay.com'];
  if (allowed.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Vary', 'Origin');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).end();

  const { email, result, scenario } = req.body || {};

  if (!email || typeof email !== 'string') {
    return res.status(400).json({ error: 'email required' });
  }
  const emailTrimmed = email.trim().slice(0, 254);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailTrimmed)) {
    return res.status(400).json({ error: 'invalid email' });
  }

  const VALID_SCENARIOS = ['habit', 'purchase', 'debt', 'invest'];
  const scenarioSafe = VALID_SCENARIOS.includes(scenario) ? scenario : 'unknown';
  const resultSafe = typeof result === 'string'
    ? result.replace(/<[^>]*>/g, '').slice(0, 50)
    : '';

  console.log(`LEAD | ${emailTrimmed} | ${resultSafe} | ${scenarioSafe} | ${new Date().toISOString()}`);
  res.status(200).json({ ok: true });
}
