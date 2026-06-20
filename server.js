// Air Serbia x PolyAI - prospect demo server
// Load .env file automatically if present (so `npm start` picks up API keys without manual export)
const fs = require('fs');
const path2 = require('path');
const envPath = path2.join(__dirname, '.env');
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
// -------------------------------------------------------------
// Serves the branded microsite + a mock contact-centre API the
// PolyAI Studio voice agent calls live during the meeting.
//
// Gateway pattern (see reference/working-system.md): the Studio agent
// always calls one stable contract. Reads can be LIVE (flight status),
// writes are always mock (no writes to Air Serbia's real systems).
//
// LIVE action: GET /api/flight-status/:flightNumber proxies a real
// flight-status API (AeroDataBox via RapidAPI, or AviationStack), keyed
// from server-side env vars only. If no key is set or the upstream fails,
// it degrades gracefully to a deterministic mock so the demo never dies.

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ----------------------------------------------------------------------
// Tiny in-process TTL cache (protects the live upstream from demo retries)
// ----------------------------------------------------------------------
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

// ----------------------------------------------------------------------
// MOCK PASSENGER RECORD - one believable Elevate member, looked up by phone.
// The agent looks up "any" phone on call-open and gets this record, so the
// personalization wow (greet by name, read back the booking) is reproducible.
// ----------------------------------------------------------------------
const PASSENGER = {
  passenger_id: 'JU-7741920',
  phone: '+381641234567',
  name: 'Milan Petrović',
  first_name: 'Milan',
  preferred_language: 'sr', // sr = Serbian, en = English
  elevate: {
    member_id: 'EL2207744',
    tier: 'Silver',
    miles_balance: 18450,
    miles_to_next_tier: 6550,
    next_tier: 'Gold'
  },
  upcoming_booking: {
    pnr: 'JU8K2P',
    flight_number: 'JU324',
    route: 'BEG-CDG',
    origin: 'Belgrade (BEG)',
    destination: 'Paris Charles de Gaulle (CDG)',
    departure_local: '2026-07-03T11:25:00',
    arrival_local: '2026-07-03T13:55:00',
    status: 'On time',
    cabin: 'Economy',
    fare_type: 'Standard',
    seat: '14C',
    checked_bags: 1,
    extra_bags_allowed: 2,
    checkin_opens_local: '2026-07-02T11:25:00'
  },
  recent_activity: {
    last_flight: 'JU501 BEG-LHR on 12 May 2026',
    disruptions_last_90d: 0
  },
  payment: {
    outstanding_balance_eur: 0,
    card_on_file: 'Visa ****4417'
  },
  // Actions the agent is allowed to offer this passenger.
  eligible_for: [
    'change_flight',
    'cancel_refund',
    'extra_baggage',
    'seat_selection',
    'online_checkin',
    'redeem_miles'
  ]
};

// ----------------------------------------------------------------------
// LIVE FLIGHT STATUS - real external call, with graceful mock fallback.
// ----------------------------------------------------------------------
const FLIGHT_ROUTES = {
  JU324: { from: 'Belgrade (BEG)', to: 'Paris Charles de Gaulle (CDG)', dep: '11:25', arr: '13:55' },
  JU500: { from: 'Belgrade (BEG)', to: 'London Heathrow (LHR)', dep: '09:10', arr: '11:05' },
  JU170: { from: 'Belgrade (BEG)', to: 'Tivat (TIV)', dep: '07:40', arr: '08:35' },
  JU650: { from: 'Belgrade (BEG)', to: 'Istanbul (IST)', dep: '15:20', arr: '18:05' },
  JU200: { from: 'Belgrade (BEG)', to: 'New York JFK (JFK)', dep: '12:30', arr: '16:45' }
};

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

// Deterministic mock so a given flight number always reads the same on stage.
function mockFlightStatus(flightNumber) {
  const fn = flightNumber.toUpperCase();
  const r = FLIGHT_ROUTES[fn] || { from: 'Belgrade (BEG)', to: 'Vienna (VIE)', dep: '10:00', arr: '11:30' };
  const statuses = ['On time', 'On time', 'On time', 'Delayed 25 min', 'Boarding'];
  const idx = fn.split('').reduce((a, c) => a + c.charCodeAt(0), 0) % statuses.length;
  return {
    flight_number: fn,
    airline: 'Air Serbia',
    status: statuses[idx],
    departure: { airport: r.from, scheduled_local: r.dep, terminal: '2' },
    arrival: { airport: r.to, scheduled_local: r.arr, terminal: r.to.includes('CDG') ? '2D' : '-' },
    date: todayISO(),
    source: 'sample data (no live flight API key configured)'
  };
}

// Adapter: AeroDataBox via RapidAPI (HTTPS, by flight number + date).
async function fromAeroDataBox(flightNumber) {
  const key = process.env.AERODATABOX_KEY;
  if (!key) return null;
  const date = todayISO();
  const url = `https://aerodatabox.p.rapidapi.com/flights/number/${encodeURIComponent(flightNumber)}/${date}`;
  const { signal, done } = withTimeout(3500);
  try {
    const r = await fetch(url, {
      signal,
      headers: { 'X-RapidAPI-Key': key, 'X-RapidAPI-Host': 'aerodatabox.p.rapidapi.com' }
    });
    if (!r.ok) return null;
    const data = await r.json();
    const f = Array.isArray(data) ? data[0] : (data.flights ? data.flights[0] : null);
    if (!f) return null;
    return {
      flight_number: flightNumber.toUpperCase(),
      airline: f.airline?.name || 'Air Serbia',
      status: f.status || 'Scheduled',
      departure: {
        airport: f.departure?.airport?.name || f.departure?.airport?.iata || '-',
        scheduled_local: (f.departure?.scheduledTime?.local || '').slice(11, 16) || '-',
        terminal: f.departure?.terminal || '-'
      },
      arrival: {
        airport: f.arrival?.airport?.name || f.arrival?.airport?.iata || '-',
        scheduled_local: (f.arrival?.scheduledTime?.local || '').slice(11, 16) || '-',
        terminal: f.arrival?.terminal || '-'
      },
      date,
      source: 'live: AeroDataBox'
    };
  } catch (_e) {
    return null;
  } finally {
    done();
  }
}

// Normalise AviationStack raw status strings to human-readable labels.
const AS_STATUS_MAP = {
  scheduled: 'Scheduled', active: 'En route', landed: 'Landed',
  cancelled: 'Cancelled', incident: 'Incident', diverted: 'Diverted'
};
function normaliseAvStatus(s) { return AS_STATUS_MAP[s] || (s ? s.charAt(0).toUpperCase() + s.slice(1) : 'Scheduled'); }

// Format a UTC ISO datetime from AviationStack into local HH:MM.
// AviationStack free tier returns UTC; Air Serbia operates on CET/CEST (UTC+1/+2).
// We add 2h for CEST (summer) as a practical approximation for the demo.
function avToLocal(iso) {
  if (!iso) return '-';
  try {
    const d = new Date(iso);
    d.setHours(d.getHours() + 2); // CEST offset (UTC+2, valid Apr–Oct)
    return d.toISOString().slice(11, 16);
  } catch { return iso.slice(11, 16) || '-'; }
}

// Adapter: AviationStack (free tier, by IATA flight number; note: free tier is HTTP only).
async function fromAviationStack(flightNumber) {
  const key = process.env.AVIATIONSTACK_KEY;
  if (!key) return null;
  const url = `http://api.aviationstack.com/v1/flights?access_key=${key}&flight_iata=${encodeURIComponent(flightNumber)}`;
  const { signal, done } = withTimeout(3500);
  try {
    const r = await fetch(url, { signal });
    if (!r.ok) return null;
    const data = await r.json();
    const f = data?.data?.[0];
    if (!f) return null;
    // Build a friendly airport label: "City (IATA)" or just IATA if no name.
    const depLabel = f.departure?.airport
      ? `${f.departure.airport} (${f.departure.iata || ''})`
      : (f.departure?.iata || '-');
    const arrLabel = f.arrival?.airport
      ? `${f.arrival.airport} (${f.arrival.iata || ''})`
      : (f.arrival?.iata || '-');
    // Prefer estimated times if available, else scheduled.
    const depTime = f.departure?.estimated || f.departure?.scheduled;
    const arrTime = f.arrival?.estimated || f.arrival?.scheduled;
    return {
      flight_number: flightNumber.toUpperCase(),
      airline: f.airline?.name || 'Air Serbia',
      status: normaliseAvStatus(f.flight_status),
      departure: {
        airport: depLabel,
        scheduled_local: avToLocal(depTime),
        terminal: f.departure?.terminal || '-'
      },
      arrival: {
        airport: arrLabel,
        scheduled_local: avToLocal(arrTime),
        terminal: f.arrival?.terminal || '-'
      },
      date: todayISO(),
      source: 'live: AviationStack'
    };
  } catch (_e) {
    return null;
  } finally {
    done();
  }
}

async function getFlightStatus(flightNumber) {
  return cached(`flight:${flightNumber.toUpperCase()}:${todayISO()}`, async () => {
    const live = (await fromAeroDataBox(flightNumber)) || (await fromAviationStack(flightNumber));
    return live || mockFlightStatus(flightNumber);
  });
}

// ----------------------------------------------------------------------
// API ROUTES
// ----------------------------------------------------------------------

// Call-open lookup. Returns the one demo passenger regardless of phone,
// so the agent's personalization is deterministic on stage.
app.get('/api/passenger/:phone', (req, res) => {
  res.json(PASSENGER);
});

// LIVE read: flight status by flight number (e.g. JU324).
app.get('/api/flight-status/:flightNumber', async (req, res) => {
  const fn = String(req.params.flightNumber || '').trim();
  if (!/^[A-Za-z0-9]{2,7}$/.test(fn)) {
    return res.status(400).json({ error: 'Provide a flight number like JU324.' });
  }
  try {
    res.json(await getFlightStatus(fn));
  } catch (_e) {
    res.json(mockFlightStatus(fn));
  }
});

// WRITE (mock): change a flight on an existing booking.
app.post('/api/booking/change', (req, res) => {
  const { pnr, new_date, new_flight_number, notes } = req.body || {};
  res.json({
    reference: `CHG-${Date.now()}`,
    pnr: pnr || PASSENGER.upcoming_booking.pnr,
    new_date: new_date || null,
    new_flight_number: new_flight_number || null,
    fare_difference_eur: 0,
    status: 'confirmed',
    notes: notes || '',
    confirmation_message: 'Your flight change is confirmed. A new itinerary will reach you by email and SMS within a few minutes.'
  });
});

// WRITE (mock): add extra baggage.
app.post('/api/baggage/add', (req, res) => {
  const { pnr, extra_bags } = req.body || {};
  const bags = Math.max(1, Math.min(2, Number(extra_bags) || 1));
  res.json({
    reference: `BAG-${Date.now()}`,
    pnr: pnr || PASSENGER.upcoming_booking.pnr,
    extra_bags: bags,
    price_eur: bags * 35,
    status: 'confirmed',
    confirmation_message: `Added ${bags} extra bag(s) to your booking. The updated baggage allowance is on your boarding pass.`
  });
});

// WRITE (mock): online check-in.
app.post('/api/checkin', (req, res) => {
  const { pnr, seat } = req.body || {};
  res.json({
    reference: `CHK-${Date.now()}`,
    pnr: pnr || PASSENGER.upcoming_booking.pnr,
    seat: seat || PASSENGER.upcoming_booking.seat,
    boarding_pass: 'issued',
    status: 'checked_in',
    confirmation_message: 'You are checked in. Your mobile boarding pass has been sent to the Air Serbia app and your email.'
  });
});

app.get('/healthz', (_q, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => console.log(`Air Serbia demo on :${PORT}`));
