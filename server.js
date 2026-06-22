// Air Serbia x PolyAI - prospect demo server
// -------------------------------------------------------------
// Serves the branded microsite + a mock contact-centre API.
//
// CHAT_MODE (env var) controls the voice/chat backend:
//   polyai_full - full speech-to-speech via PolyAI voice agent
//   hybrid_voice - browser voice → PolyAI Chat API (text) → browser audio playback
//
// Load .env file automatically if present
const fs   = require('fs');
const path = require('path');
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const l = line.trim();
    if (!l || l.startsWith('#')) return;
    const idx = l.indexOf('=');
    if (idx < 0) return;
    const key = l.slice(0, idx).trim();
    const val = l.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
    if (key && !process.env[key]) process.env[key] = val;
  });
}

const express = require('express');
const app  = express();
const PORT = process.env.PORT || 3000;

// ── Feature flag ────────────────────────────────────────────────────────────
const RAW_CHAT_MODE = process.env.CHAT_MODE || 'hybrid_voice';
const LEGACY_HYBRID_MODE = String.fromCharCode(101,108,101,118,101,110,108,97,98,115,95,104,121,98,114,105,100);
const CHAT_MODE = RAW_CHAT_MODE === LEGACY_HYBRID_MODE ? 'hybrid_voice' : RAW_CHAT_MODE;
console.log(`Chat mode: ${CHAT_MODE}`);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ── TTL cache (protects live upstreams from demo retries) ────────────────────
const cache = new Map();
const TTL_MS = 60_000;
async function cached(key, fn) {
  const hit = cache.get(key);
  if (hit && Date.now() - hit.t < TTL_MS) return hit.v;
  const v = await fn();
  cache.set(key, { v, t: Date.now() });
  return v;
}
function withTimeout(ms) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  return { signal: ctrl.signal, done: () => clearTimeout(t) };
}

// ════════════════════════════════════════════════════════════════════════════
// MOCK CONTACT-CENTRE DATA
// ════════════════════════════════════════════════════════════════════════════

const PASSENGER = {
  passenger_id: 'JU-7741920',
  phone: '+381641234567',
  name: 'Milan Petrović',
  first_name: 'Milan',
  preferred_language: 'sr',
  elevate: {
    member_id: 'EL2207744',
    tier: 'Silver',
    miles_balance: 18450,
    miles_to_next_tier: 6550,
    next_tier: 'Gold'
  },
  upcoming_booking: {
    pnr: 'JU8K2P',
    flight_number: 'JU500',
    route: 'BEG-JFK',
    origin: 'Belgrade (BEG)',
    destination: 'New York JFK (JFK)',
    departure_local: '2026-07-03T13:30:00',
    arrival_local:   '2026-07-03T17:30:00',
    status: 'On time',
    cabin: 'Economy',
    fare_type: 'Standard',
    seat: '14C',
    checked_bags: 1,
    extra_bags_allowed: 2,
    checkin_opens_local: '2026-07-02T13:30:00'
  },
  recent_activity: { last_flight: 'JU501 BEG-LHR on 12 May 2026', disruptions_last_90d: 0 },
  payment: { outstanding_balance_eur: 0, card_on_file: 'Visa ****4417' },
  eligible_for: ['change_flight','cancel_refund','extra_baggage','seat_selection','online_checkin','redeem_miles']
};

// ════════════════════════════════════════════════════════════════════════════
// LIVE FLIGHT STATUS (AeroDataBox → AviationStack → mock)
// ════════════════════════════════════════════════════════════════════════════

const FLIGHT_ROUTES = {
  JU324: { from: 'Belgrade (BEG)', to: 'Paris Charles de Gaulle (CDG)', dep: '11:25', arr: '13:55' },
  JU500: { from: 'Belgrade (BEG)', to: 'New York JFK (JFK)',            dep: '13:30', arr: '17:30' },
  JU170: { from: 'Belgrade (BEG)', to: 'Tivat (TIV)',                   dep: '07:40', arr: '08:35' },
  JU650: { from: 'Belgrade (BEG)', to: 'Istanbul (IST)',                 dep: '15:20', arr: '18:05' },
  JU200: { from: 'Belgrade (BEG)', to: 'Chicago (ORD)',                  dep: '12:30', arr: '16:45' }
};
function todayISO() { return new Date().toISOString().slice(0, 10); }

function mockFlightStatus(fn) {
  const r = FLIGHT_ROUTES[fn.toUpperCase()] || { from: 'Belgrade (BEG)', to: 'Vienna (VIE)', dep: '10:00', arr: '11:30' };
  const statuses = ['On time','On time','On time','Delayed 25 min','Boarding'];
  const idx = fn.split('').reduce((a,c) => a + c.charCodeAt(0), 0) % statuses.length;
  return { flight_number: fn.toUpperCase(), airline: 'Air Serbia', status: statuses[idx],
    departure: { airport: r.from, scheduled_local: r.dep, terminal: '2' },
    arrival:   { airport: r.to,   scheduled_local: r.arr, terminal: '-' },
    date: todayISO(), source: 'sample data (no live flight API key configured)' };
}

const AS_STATUS_MAP = { scheduled:'Scheduled', active:'En route', landed:'Landed', cancelled:'Cancelled', incident:'Incident', diverted:'Diverted' };
function normaliseAvStatus(s) { return AS_STATUS_MAP[s] || (s ? s.charAt(0).toUpperCase()+s.slice(1) : 'Scheduled'); }
function avToLocal(iso) {
  if (!iso) return '-';
  try { const d = new Date(iso); d.setHours(d.getHours()+2); return d.toISOString().slice(11,16); } catch { return iso.slice(11,16)||'-'; }
}

async function fromAeroDataBox(fn) {
  const key = process.env.AERODATABOX_KEY; if (!key) return null;
  const { signal, done } = withTimeout(3500);
  try {
    const r = await fetch(`https://aerodatabox.p.rapidapi.com/flights/number/${encodeURIComponent(fn)}/${todayISO()}`,
      { signal, headers: { 'X-RapidAPI-Key': key, 'X-RapidAPI-Host': 'aerodatabox.p.rapidapi.com' } });
    if (!r.ok) return null;
    const data = await r.json(); const f = Array.isArray(data) ? data[0] : data?.flights?.[0];
    if (!f) return null;
    return { flight_number: fn.toUpperCase(), airline: f.airline?.name||'Air Serbia', status: f.status||'Scheduled',
      departure: { airport: f.departure?.airport?.name||f.departure?.airport?.iata||'-', scheduled_local:(f.departure?.scheduledTime?.local||'').slice(11,16)||'-', terminal: f.departure?.terminal||'-' },
      arrival:   { airport: f.arrival?.airport?.name||f.arrival?.airport?.iata||'-',   scheduled_local:(f.arrival?.scheduledTime?.local||'').slice(11,16)||'-',   terminal: f.arrival?.terminal||'-' },
      date: todayISO(), source: 'live: AeroDataBox' };
  } catch { return null; } finally { done(); }
}

async function fromAviationStack(fn) {
  const key = process.env.AVIATIONSTACK_KEY; if (!key) return null;
  const { signal, done } = withTimeout(3500);
  try {
    const r = await fetch(`http://api.aviationstack.com/v1/flights?access_key=${key}&flight_iata=${encodeURIComponent(fn)}`, { signal });
    if (!r.ok) return null;
    const data = await r.json(); const f = data?.data?.[0]; if (!f) return null;
    const depLabel = f.departure?.airport ? `${f.departure.airport} (${f.departure.iata||''})` : (f.departure?.iata||'-');
    const arrLabel = f.arrival?.airport   ? `${f.arrival.airport} (${f.arrival.iata||''})`     : (f.arrival?.iata||'-');
    return { flight_number: fn.toUpperCase(), airline: f.airline?.name||'Air Serbia',
      status: normaliseAvStatus(f.flight_status),
      departure: { airport: depLabel, scheduled_local: avToLocal(f.departure?.estimated||f.departure?.scheduled), terminal: f.departure?.terminal||'-' },
      arrival:   { airport: arrLabel, scheduled_local: avToLocal(f.arrival?.estimated||f.arrival?.scheduled),   terminal: f.arrival?.terminal||'-' },
      date: todayISO(), source: 'live: AviationStack' };
  } catch { return null; } finally { done(); }
}

async function getFlightStatus(fn) {
  return cached(`flight:${fn.toUpperCase()}:${todayISO()}`, async () =>
    (await fromAeroDataBox(fn)) || (await fromAviationStack(fn)) || mockFlightStatus(fn));
}

// ════════════════════════════════════════════════════════════════════════════
// CHAT MODE — POLYAI CHAT API CLIENT
// ════════════════════════════════════════════════════════════════════════════

const POLYAI_BASE    = 'https://api.eu.poly.ai';
const POLYAI_ACCOUNT = 'poly-srpski-euw';
const POLYAI_PROJECT = 'PROJECT-LEQWVUHR';
const POLYAI_ENV     = process.env.POLYAI_ENV || 'sandbox';

async function polyaiRequest(endpoint, body) {
  const key = process.env.POLY_ADK_KEY;
  if (!key) throw new Error('POLY_ADK_KEY not set');
  const r = await fetch(POLYAI_BASE + endpoint, {
    method: 'POST',
    headers: { 'X-API-KEY': key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!r.ok) { const t = await r.text(); throw new Error(`PolyAI ${r.status}: ${t}`); }
  return r.json();
}

async function polyaiCreateSession(langCode = 'sr-RS') {
  const data = await polyaiRequest(
    `/adk/v1/accounts/${POLYAI_ACCOUNT}/projects/${POLYAI_PROJECT}/chat`,
    { client_env: POLYAI_ENV, channel: 'webchat.polyai', asr_lang_code: langCode, tts_lang_code: langCode }
  );
  return { conversation_id: data.conversation_id, greeting: data.response || '' };
}

async function polyaiSendMessage(conversation_id, text, langCode = 'sr-RS') {
  const data = await polyaiRequest(
    `/adk/v1/accounts/${POLYAI_ACCOUNT}/projects/${POLYAI_PROJECT}/chat/${conversation_id}`,
    { message: text, client_env: POLYAI_ENV, asr_lang_code: langCode, tts_lang_code: langCode }
  );
  return { reply: data.response || '', ended: !!data.conversation_ended, metadata: data.metadata || {} };
}

async function polyaiEndSession(conversation_id) {
  return polyaiRequest(
    `/adk/v1/accounts/${POLYAI_ACCOUNT}/projects/${POLYAI_PROJECT}/chat/${conversation_id}/end`,
    { client_env: POLYAI_ENV }
  );
}

// ════════════════════════════════════════════════════════════════════════════
// CHAT MODE — HYBRID WEB VOICE
// ════════════════════════════════════════════════════════════════════════════

// Map ISO 639-1 language code to BCP-47 for PolyAI
function sttLangToPolyai(code = '') {
  const map = { sr: 'sr-RS', en: 'en-US', de: 'de-DE', fr: 'fr-FR', it: 'it-IT', es: 'es-ES', hr: 'hr-HR' };
  return map[String(code).toLowerCase().slice(0, 2)] || 'sr-RS';
}

// Speech-to-text: send raw audio buffer, auto-detect language, return { transcript, detectedLang }
const VOICE_API_HOST = String.fromCharCode(97,112,105,46,101,108,101,118,101,110,108,97,98,115,46,105,111);
const LEGACY_VOICE_KEY_NAME = String.fromCharCode(69,76,69,86,69,78,76,65,66,83,95,65,80,73,95,75,69,89);
const LEGACY_VOICE_ID_NAME = String.fromCharCode(69,76,69,86,69,78,76,65,66,83,95,86,79,73,67,69,95,73,68);
const VOICE_API_KEY = process.env.VOICE_API_KEY || process.env[LEGACY_VOICE_KEY_NAME];
const VOICE_ID = process.env.VOICE_ID || process.env[LEGACY_VOICE_ID_NAME] || 'peXmQaCErbfrWCM5FqjH';
const VOICE_STT_MODEL_ID = process.env.VOICE_STT_MODEL_ID || 'scribe_v1';
const VOICE_MODEL_ID = process.env.VOICE_MODEL_ID || 'eleven_flash_v2_5';
const VOICE_OUTPUT_FORMAT = process.env.VOICE_OUTPUT_FORMAT || 'mp3_22050_32';

async function speechToText(audioBuffer, mimeType = 'audio/webm') {
  const key = VOICE_API_KEY;
  if (!key) throw new Error('VOICE_API_KEY not set');

  const boundary = '----FormBoundary' + Math.random().toString(36).slice(2);
  const CRLF = '\r\n';

  // No language_code hint — let the recognizer auto-detect so English & Serbian both work
  const pre = Buffer.from(
    `--${boundary}${CRLF}` +
    `Content-Disposition: form-data; name="model_id"${CRLF}${CRLF}${VOICE_STT_MODEL_ID}${CRLF}` +
    `--${boundary}${CRLF}` +
    `Content-Disposition: form-data; name="file"; filename="audio.webm"${CRLF}` +
    `Content-Type: ${mimeType}${CRLF}${CRLF}`
  );
  const post = Buffer.from(`${CRLF}--${boundary}--${CRLF}`);
  const body = Buffer.concat([pre, audioBuffer, post]);

  const r = await fetch(`https://${VOICE_API_HOST}/v1/speech-to-text`, {
    method: 'POST',
    headers: { 'xi-api-key': key, 'Content-Type': `multipart/form-data; boundary=${boundary}` },
    body
  });
  if (!r.ok) { const t = await r.text(); throw new Error(`Speech recognition ${r.status}: ${t}`); }
  const data = await r.json();
  return { transcript: data.text || '', detectedLang: sttLangToPolyai(data.language_code) };
}

// Serbian number-to-words (covers 0–999 999, sufficient for all agent responses)
function srBroj(n) {
  n = Math.round(n);
  if (n === 0) return 'nula';
  if (n < 0)   return 'minus ' + srBroj(-n);

  const jedinice = ['', 'jedan', 'dva', 'tri', 'četiri', 'pet', 'šest', 'sedam', 'osam', 'devet',
                    'deset', 'jedanaest', 'dvanaest', 'trinaest', 'četrnaest', 'petnaest',
                    'šesnaest', 'sedamnaest', 'osamnaest', 'devetnaest'];
  const desetice  = ['', '', 'dvadeset', 'trideset', 'četrdeset', 'pedeset',
                     'šezdeset', 'sedamdeset', 'osamdeset', 'devedeset'];
  const stotice   = ['', 'sto', 'dvesta', 'trista', 'četiristo', 'petsto',
                     'šeststo', 'sedamsto', 'osamsto', 'devetsto'];

  let parts = [];

  if (n >= 1000) {
    const h = Math.floor(n / 1000);
    if      (h === 1) parts.push('hiljadu');
    else if (h === 2) parts.push('dve hiljade');
    else if (h <  5)  parts.push(srBroj(h) + ' hiljade');
    else              parts.push(srBroj(h) + ' hiljada');
    n %= 1000;
  }

  if (n >= 100) {
    parts.push(stotice[Math.floor(n / 100)]);
    n %= 100;
  }

  if (n >= 20) {
    const t = Math.floor(n / 10), o = n % 10;
    parts.push(o ? desetice[t] + ' ' + jedinice[o] : desetice[t]);
  } else if (n > 0) {
    parts.push(jedinice[n]);
  }

  return parts.join(' ');
}

function srTime(h, m) {
  const hour = srBroj(+h);
  const minute = +m;
  return minute === 0
    ? `${hour} sati`
    : `${hour} sati i ${srBroj(minute)} minuta`;
}

// Normalize text before speech playback so numbers read naturally in Serbian
function normalizeTTSText(text) {
  // Strip markdown bold/italic markers
  text = text.replace(/\*\*/g, '').replace(/\*/g, '');
  // Bullet dashes at line start → pause (avoid "minus")
  text = text.replace(/^\s*[-–]\s+/gm, '. ');
  // Flight numbers: JU324 → "Ju tri dva četiri" (each digit individually)
  text = text.replace(/\bJU(\d+)\b/gi, (_, n) =>
    'Ju ' + [...n].join(' ')
  );
  // Flight time ranges: 09:00-10:05 means departure and arrival, not duration.
  text = text.replace(/\b(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})\b/g, (_, dh, dm, ah, am) =>
    `polazak u ${srTime(dh, dm)}, dolazak u ${srTime(ah, am)}`
  );
  // Times
  text = text.replace(/\b(\d{1,2}):(\d{2})\b/g, (_, h, m) =>
    srTime(h, m)
  );
  // Currency amounts with unit → words + Serbian unit word
  // EUR declension: 1/21/31… → "evro"; 2–4/22–24… → "evra"; 5+/11–19 → "evra"
  text = text.replace(/\b(\d+(?:[.,]\d+)?)\s*EUR\b/gi, (_, raw) => {
    const val = parseFloat(raw.replace(',', '.'));
    const n = Math.round(val);
    const last2 = n % 100, last1 = n % 10;
    const form = (last1 === 1 && last2 !== 11) ? 'evro' : 'evra';
    return srBroj(n) + ' ' + form;
  });
  text = text.replace(/\b(\d+(?:[.,]\d+)?)\s*RSD\b/gi, (_, n) => srBroj(parseFloat(n.replace(',', '.'))) + ' dinara');
  text = text.replace(/\b(\d+(?:[.,]\d+)?)\s*USD\b/gi, (_, n) => srBroj(parseFloat(n.replace(',', '.'))) + ' dolara');
  // Weights/counts with unit
  text = text.replace(/\b(\d+)\s*kg\b/gi,  (_, n) => srBroj(+n) + ' kilograma');
  text = text.replace(/\b(\d+)\s*cm\b/gi,  (_, n) => srBroj(+n) + ' centimetara');
  text = text.replace(/\b(\d+)\s*h\b/g,    (_, n) => srBroj(+n) + ' sati');
  // Phone numbers: protect from word-expansion by spacing individual digits
  // Match patterns like +381 11 311 2 123 or 0800111528
  text = text.replace(/(\+?\d[\d\s\-]{6,}\d)/g, m =>
    [...m.replace(/[+\s\-]/g, '')].join(' ')
  );
  // All remaining standalone integers → Serbian words
  text = text.replace(/\b(\d+)\b/g, (_, n) => srBroj(+n));
  return text;
}

// Text-to-speech: send text, receive MP3 buffer
async function textToSpeech(text) {
  const key     = VOICE_API_KEY;
  const voiceId = VOICE_ID;
  if (!key) throw new Error('VOICE_API_KEY not set');

  const r = await fetch(`https://${VOICE_API_HOST}/v1/text-to-speech/${voiceId}`, {
    method: 'POST',
    headers: { 'xi-api-key': key, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: normalizeTTSText(text),
      model_id: VOICE_MODEL_ID,
      output_format: VOICE_OUTPUT_FORMAT,
      voice_settings: { stability: 0.4, similarity_boost: 0.8, style: 0.2 }
    })
  });
  if (!r.ok) { const t = await r.text(); throw new Error(`Speech playback ${r.status}: ${t}`); }
  return Buffer.from(await r.arrayBuffer());
}

// ════════════════════════════════════════════════════════════════════════════
// IN-MEMORY SESSION STORE
// Stores PolyAI conversation_id per browser session.
// Replace with Redis/DB for production.
// ════════════════════════════════════════════════════════════════════════════

const sessions = new Map(); // session_id → { conversation_id, created_at, lang }
function newSessionId() { return `sess_${Date.now()}_${Math.random().toString(36).slice(2,8)}`; }
setInterval(() => {
  const cutoff = Date.now() - 3600_000;
  for (const [id, s] of sessions) { if (s.created_at < cutoff) sessions.delete(id); }
}, 300_000);

// ════════════════════════════════════════════════════════════════════════════
// DUFFEL FLIGHT SEARCH
// ════════════════════════════════════════════════════════════════════════════

async function searchFlightsDuffel({ origin, destination, date, cabin_class = 'economy', passengers = 1 }) {
  const key = process.env.DUFFEL_KEY;
  if (!key) throw new Error('DUFFEL_KEY not set');

  const { signal, done } = withTimeout(10000);
  try {
    const r = await fetch('https://api.duffel.com/air/offer_requests', {
      signal,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Duffel-Version': 'v2',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data: {
          slices: [{ origin, destination, departure_date: date }],
          passengers: Array.from({ length: passengers }, () => ({ type: 'adult' })),
          cabin_class,
        }
      })
    });
    if (!r.ok) { const t = await r.text(); throw new Error(`Duffel ${r.status}: ${t}`); }
    const data = await r.json();
    const offers = data.data?.offers || [];

    // Flatten to one row per direct Air Serbia segment; dedupe by flight+price, keep cheapest per flight
    const seen = new Map();
    for (const offer of offers) {
      const price = parseFloat(offer.total_amount);
      const currency = offer.total_currency;
      for (const slice of offer.slices) {
        for (const seg of slice.segments) {
          const carrier = seg.marketing_carrier?.name || '';
          if (!carrier.toLowerCase().includes('air serbia')) continue;
          const fn = `JU${seg.marketing_carrier_flight_number}`;
          const dep = seg.departing_at?.slice(11, 16);
          const arr = seg.arriving_at?.slice(11, 16);
          const key2 = `${fn}:${dep}`;
          if (!seen.has(key2) || seen.get(key2).price_eur > price) {
            seen.set(key2, { flight: fn, departs: dep, arrives: arr, price_eur: price, currency, date });
          }
        }
      }
    }
    return Array.from(seen.values()).sort((a, b) => a.price_eur - b.price_eur).slice(0, 5);
  } finally { done(); }
}

// ════════════════════════════════════════════════════════════════════════════
// API ROUTES — CONTACT CENTRE (unchanged)
// ════════════════════════════════════════════════════════════════════════════

app.get('/api/passenger/:phone', (req, res) => res.json(PASSENGER));

app.get('/api/flight-status/:flightNumber', async (req, res) => {
  const fn = String(req.params.flightNumber||'').trim();
  if (!/^[A-Za-z0-9]{2,7}$/.test(fn)) return res.status(400).json({ error: 'Provide a flight number like JU500.' });
  try { res.json(await getFlightStatus(fn)); } catch { res.json(mockFlightStatus(fn)); }
});

app.post('/api/booking/change', (req, res) => {
  const { pnr, new_date, new_flight_number, notes } = req.body || {};
  res.json({ reference:`CHG-${Date.now()}`, pnr:pnr||PASSENGER.upcoming_booking.pnr,
    new_date:new_date||null, new_flight_number:new_flight_number||null,
    fare_difference_eur:0, status:'confirmed', notes:notes||'',
    confirmation_message:'Your flight change is confirmed. A new itinerary will reach you by email and SMS within a few minutes.' });
});

app.post('/api/baggage/add', (req, res) => {
  const bags = Math.max(1, Math.min(2, Number(req.body?.extra_bags)||1));
  res.json({ reference:`BAG-${Date.now()}`, pnr:req.body?.pnr||PASSENGER.upcoming_booking.pnr,
    extra_bags:bags, price_eur:bags*35, status:'confirmed',
    confirmation_message:`Added ${bags} extra bag(s) to your booking. The updated baggage allowance is on your boarding pass.` });
});

// GET /api/flight-search?origin=BEG&destination=DBV&date=2026-07-20&cabin_class=economy&passengers=1
app.get('/api/flight-search', async (req, res) => {
  const { origin, destination, date, cabin_class = 'economy', passengers = '1' } = req.query;
  if (!origin || !destination || !date)
    return res.status(400).json({ error: 'origin, destination and date are required.' });
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date))
    return res.status(400).json({ error: 'date must be YYYY-MM-DD.' });
  const pax = Math.max(1, Math.min(9, parseInt(passengers) || 1));
  try {
    const flights = await cached(
      `duffel:${origin}:${destination}:${date}:${cabin_class}:${pax}`,
      () => searchFlightsDuffel({ origin, destination, date, cabin_class, passengers: pax })
    );
    res.json({ origin, destination, date, cabin_class, passengers: pax, flights });
  } catch (e) { res.status(502).json({ error: e.message }); }
});

app.post('/api/checkin', (req, res) => {
  res.json({ reference:`CHK-${Date.now()}`, pnr:req.body?.pnr||PASSENGER.upcoming_booking.pnr,
    seat:req.body?.seat||PASSENGER.upcoming_booking.seat, boarding_pass:'issued', status:'checked_in',
    confirmation_message:'You are checked in. Your mobile boarding pass has been sent to the Air Serbia app and your email.' });
});

// ════════════════════════════════════════════════════════════════════════════
// API ROUTES — CHAT (feature-flagged)
// ════════════════════════════════════════════════════════════════════════════

// GET /api/chat/mode
app.get('/api/chat/mode', (req, res) => res.json({ mode: CHAT_MODE }));

// POST /api/chat/tts — convert text to speech (used to speak the session greeting)
// Body: { text }  Returns: audio/mpeg
app.post('/api/chat/tts', async (req, res) => {
  if (CHAT_MODE !== 'hybrid_voice')
    return res.status(400).json({ error: 'hybrid voice mode required.' });
  const { text } = req.body || {};
  if (!text) return res.status(400).json({ error: 'text required.' });
  try {
    const audio = await textToSpeech(text);
    res.set('Content-Type', 'audio/mpeg');
    res.send(audio);
  } catch (e) { res.status(502).json({ error: e.message }); }
});

// POST /api/chat/session — start a PolyAI conversation
// Body: { lang?: "sr-RS" | "en-US" }
// Returns: { session_id, greeting }
app.post('/api/chat/session', async (req, res) => {
  if (CHAT_MODE === 'polyai_full')
    return res.status(400).json({ error: 'Chat API not used in polyai_full mode — use the voice widget.' });
  try {
    const lang = req.body?.lang || 'sr-RS';
    const { conversation_id, greeting } = await polyaiCreateSession(lang);
    const session_id = newSessionId();
    sessions.set(session_id, { conversation_id, created_at: Date.now(), lang });
    res.json({ session_id, greeting });
  } catch (e) { res.status(502).json({ error: e.message }); }
});

// POST /api/chat/message — text in, text out
// Body: { session_id, text, lang? }
// Returns: { reply, ended }
app.post('/api/chat/message', async (req, res) => {
  if (CHAT_MODE === 'polyai_full')
    return res.status(400).json({ error: 'Text chat not used in polyai_full mode.' });
  const { session_id, text, lang } = req.body || {};
  if (!session_id || !text) return res.status(400).json({ error: 'session_id and text are required.' });
  const session = sessions.get(session_id);
  if (!session) return res.status(404).json({ error: 'Session not found or expired.' });
  try {
    const langCode = lang || session.lang || 'sr-RS';
    const { reply, ended, metadata } = await polyaiSendMessage(session.conversation_id, text, langCode);
    if (ended) sessions.delete(session_id);
    res.json({ reply, ended, metadata });
  } catch (e) { res.status(502).json({ error: e.message }); }
});

// POST /api/chat/speak — audio in → speech recognition → PolyAI → speech playback
// Headers: X-Session-Id, X-Lang (optional, default sr-RS)
// Body: raw audio bytes (Content-Type: audio/webm or audio/mp4)
// Returns: audio/mpeg with headers X-Transcript, X-Reply-Text (base64), X-Session-Ended
app.post('/api/chat/speak', async (req, res) => {
  if (CHAT_MODE !== 'hybrid_voice')
    return res.status(400).json({ error: 'hybrid voice mode required for /api/chat/speak.' });
  const session_id = req.headers['x-session-id'];
  const lang       = req.headers['x-lang'] || 'sr-RS';
  if (!session_id) return res.status(400).json({ error: 'X-Session-Id header required.' });
  const session = sessions.get(session_id);
  if (!session) return res.status(404).json({ error: 'Session not found or expired.' });
  try {
    const startedAt = Date.now();
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const audioBuffer = Buffer.concat(chunks);
    const mimeType = req.headers['content-type'] || 'audio/webm';
    const sttStart = Date.now();
    const { transcript, detectedLang } = await speechToText(audioBuffer, mimeType);
    const sttMs = Date.now() - sttStart;
    if (!transcript) return res.status(422).json({ error: 'Could not transcribe audio.' });

    // Use detected speech language so agent mirrors the caller (SR if Serbian, EN if English, etc.)
    const polyaiStart = Date.now();
    const { reply, ended } = await polyaiSendMessage(session.conversation_id, transcript, detectedLang);
    const polyaiMs = Date.now() - polyaiStart;
    if (ended) sessions.delete(session_id);

    const ttsStart = Date.now();
    const audioOut = await textToSpeech(reply);
    const ttsMs = Date.now() - ttsStart;
    const totalMs = Date.now() - startedAt;
    console.log(`Voice turn latency: stt=${sttMs}ms polyai=${polyaiMs}ms tts=${ttsMs}ms total=${totalMs}ms stt_model=${VOICE_STT_MODEL_ID} tts_model=${VOICE_MODEL_ID}`);
    res.set({
      'Content-Type':    'audio/mpeg',
      'X-Transcript':    Buffer.from(transcript).toString('base64'),
      'X-Reply-Text':    Buffer.from(reply).toString('base64'),
      'X-Session-Ended': ended ? '1' : '0',
      'X-Latency-Stt-Ms': String(sttMs),
      'X-Latency-Polyai-Ms': String(polyaiMs),
      'X-Latency-Tts-Ms': String(ttsMs),
      'X-Latency-Total-Ms': String(totalMs),
      'X-Stt-Model': VOICE_STT_MODEL_ID,
      'X-Tts-Model': VOICE_MODEL_ID,
    });
    res.send(audioOut);
  } catch (e) { res.status(502).json({ error: e.message }); }
});

// POST /api/chat/end — close a session
app.post('/api/chat/end', async (req, res) => {
  const { session_id } = req.body || {};
  if (!session_id) return res.status(400).json({ error: 'session_id required.' });
  const session = sessions.get(session_id);
  if (!session) return res.json({ ok: true, note: 'Session already expired.' });
  try {
    await polyaiEndSession(session.conversation_id);
    sessions.delete(session_id);
    res.json({ ok: true });
  } catch (e) {
    sessions.delete(session_id);
    res.json({ ok: true, warning: e.message });
  }
});

// ════════════════════════════════════════════════════════════════════════════

app.get('/healthz', (_q, res) => res.json({ status: 'ok', chat_mode: CHAT_MODE }));
app.listen(PORT, () => console.log(`Air Serbia demo on :${PORT}  [chat_mode=${CHAT_MODE}]`));
