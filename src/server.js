'use strict';
// Joy Taxi backend v2 — ride requests, live status, driver accept, dispatcher.
// node:http + pg only. WhatsApp stays as the fallback channel.
const http = require('node:http');
const crypto = require('node:crypto');
const { Pool } = require('pg');
const webpush = require('web-push');

const PORT = process.env.PORT || 3000;
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';
const DRIVER_TOKEN = process.env.DRIVER_TOKEN || '';
const PUSH_ON = !!(process.env.VAPID_PUBLIC && process.env.VAPID_PRIVATE);
if (PUSH_ON) webpush.setVapidDetails(process.env.VAPID_SUBJECT || 'mailto:joytaxi@cierp.uk', process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);
const DEFAULT_CONFIG = {
  rates: { enabled: false, base: 5, perKm: 0.9, minimum: 7, nightFrom: 23, nightTo: 5, nightExtra: 1.25, spread: 0.12, airport: {} },
  whish: { enabled: false, number: '', name: '' },
};
const ORIGINS = (process.env.ALLOWED_ORIGINS || 'https://joytaxi.cierp.uk')
  .split(',').map(s => s.trim()).filter(Boolean);

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && !/localhost|127\.0\.0\.1/.test(process.env.DATABASE_URL)
    ? { rejectUnauthorized: false } : false,
});

const STATUSES = ['new', 'confirmed', 'assigned', 'arrived', 'ontrip', 'done', 'cancelled'];
// token is never returned by list/driver endpoints
const COLS = `id, created_at, pickup, destination, when_text, est_km, est_text, lang, status, note,
  lat, lng, dest_lat, dest_lng, phone, vehicle, driver_name, driver_plate, driver_lat, driver_lng, driver_ts, accepted_at`;

async function migrate() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS rides (
      id BIGSERIAL PRIMARY KEY,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      pickup TEXT NOT NULL, destination TEXT NOT NULL,
      when_text TEXT NOT NULL DEFAULT 'now',
      est_km NUMERIC, est_text TEXT,
      lang TEXT NOT NULL DEFAULT 'en',
      status TEXT NOT NULL DEFAULT 'new', note TEXT
    );
    CREATE INDEX IF NOT EXISTS rides_created_idx ON rides (created_at DESC);
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS token TEXT;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS lat NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS lng NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS phone TEXT;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS vehicle TEXT;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_name TEXT;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_plate TEXT;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMPTZ;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS dest_lat NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS dest_lng NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_lat NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_lng NUMERIC;
    ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_ts TIMESTAMPTZ;
    CREATE TABLE IF NOT EXISTS push_subs (
      endpoint TEXT PRIMARY KEY, sub JSONB NOT NULL, role TEXT NOT NULL DEFAULT 'driver',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value JSONB NOT NULL);
  `);
}

async function getConfig() {
  const q = await pool.query("SELECT value FROM settings WHERE key='config'");
  const v = q.rowCount ? q.rows[0].value : {};
  return { rates: { ...DEFAULT_CONFIG.rates, ...(v.rates || {}) }, whish: { ...DEFAULT_CONFIG.whish, ...(v.whish || {}) } };
}
function cleanConfig(b) {
  const r = b.rates || {}, w = b.whish || {}, out = { rates: {}, whish: {} };
  const n = (x, lo, hi, d) => (Number.isFinite(+x) && +x >= lo && +x <= hi ? +x : d);
  out.rates = { enabled: !!r.enabled, base: n(r.base, 0, 500, 5), perKm: n(r.perKm, 0, 50, 0.9), minimum: n(r.minimum, 0, 500, 7),
    nightFrom: n(r.nightFrom, 0, 23, 23), nightTo: n(r.nightTo, 0, 23, 5), nightExtra: n(r.nightExtra, 1, 5, 1.25), spread: n(r.spread, 0, 0.5, 0.12), airport: {} };
  for (const [k, v] of Object.entries(r.airport || {})) if (Number.isFinite(+v) && +v > 0 && +v < 1000) out.rates.airport[clean(k, 40)] = +v;
  out.whish = { enabled: !!w.enabled, number: clean(w.number, 24), name: clean(w.name, 60) };
  return out;
}
async function notifyNew(ride) {
  if (!PUSH_ON) return;
  const subs = (await pool.query('SELECT endpoint, sub FROM push_subs')).rows;
  const payload = JSON.stringify({ title: 'New Joy Taxi ride #' + ride.id, body: ride.pickup + ' → ' + ride.destination + (ride.when_text !== 'now' ? ' · ' + ride.when_text : ''), url: '/app/driver/', tag: 'ride-' + ride.id });
  await Promise.all(subs.map(s => webpush.sendNotification(s.sub, payload, { TTL: 600, urgency: 'high' }).catch(async e => {
    if (e.statusCode === 404 || e.statusCode === 410) await pool.query('DELETE FROM push_subs WHERE endpoint=$1', [s.endpoint]);
  })));
}

// ── tiny in-memory rate limit for ride creation: 10 / 10 min / IP ──────────
const hits = new Map();
function limited(ip) {
  const now = Date.now(), win = 10 * 60 * 1000;
  const arr = (hits.get(ip) || []).filter(t => now - t < win);
  arr.push(now); hits.set(ip, arr);
  if (hits.size > 5000) for (const [k, v] of hits) if (!v.some(t => now - t < win)) hits.delete(k);
  return arr.length > 10;
}

function cors(req, res) {
  const o = req.headers.origin;
  if (o && ORIGINS.includes(o)) {
    res.setHeader('Access-Control-Allow-Origin', o);
    res.setHeader('Vary', 'Origin');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PATCH,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization');
  }
}
function send(res, code, body) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(body));
}
function readJson(req) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', c => { size += c.length; if (size > 8192) { reject(new Error('too large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => { try { resolve(JSON.parse(Buffer.concat(chunks).toString() || '{}')); } catch { reject(new Error('bad json')); } });
    req.on('error', reject);
  });
}
const clean = (v, max) => String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max);
const num = (v, lo, hi) => (v !== null && v !== '' && Number.isFinite(+v) && +v >= lo && +v <= hi) ? +v : null;
function safeEq(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}
function bearer(req) { const h = req.headers.authorization || ''; return h.startsWith('Bearer ') ? h.slice(7) : ''; }
const isAdmin = req => !!ADMIN_TOKEN && safeEq(bearer(req), ADMIN_TOKEN);
const isDriver = req => isAdmin(req) || (!!DRIVER_TOKEN && safeEq(bearer(req), DRIVER_TOKEN));

const server = http.createServer(async (req, res) => {
  cors(req, res);
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
  const url = new URL(req.url, 'http://x');
  const path = url.pathname;
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  try {
    if (path === '/health') { await pool.query('SELECT 1'); return send(res, 200, { ok: true, v: 3, push: PUSH_ON }); }

    // ── Public: create a ride (rider app or homepage note) ────────────────
    if (req.method === 'POST' && path === '/api/rides') {
      const origin = req.headers.origin;
      if (origin && !ORIGINS.includes(origin)) return send(res, 403, { error: 'forbidden' });
      if (limited(ip)) return send(res, 429, { error: 'slow down' });
      const b = await readJson(req);
      if (b.website) return send(res, 200, { ok: true }); // honeypot
      const pickup = clean(b.pickup, 200), destination = clean(b.destination, 200);
      if (!pickup && !destination) return send(res, 400, { error: 'pickup or destination required' });
      const token = crypto.randomBytes(16).toString('hex');
      const r = await pool.query(
        `INSERT INTO rides (pickup,destination,when_text,est_km,est_text,lang,token,lat,lng,phone,vehicle,dest_lat,dest_lng)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13) RETURNING id`,
        [pickup || '—', destination || '—', clean(b.when, 80) || 'now',
         num(b.est_km, 0, 2000), clean(b.est_text, 120) || null, b.lang === 'ar' ? 'ar' : 'en', token,
         num(b.lat, -90, 90), num(b.lng, -180, 180), clean(b.phone, 24) || null, clean(b.vehicle, 24) || null,
         num(b.dest_lat, -90, 90), num(b.dest_lng, -180, 180)]);
      notifyNew({ id: r.rows[0].id, pickup: pickup || '—', destination: destination || '—', when_text: clean(b.when, 80) || 'now' }).catch(e => console.error('push', e.message));
      return send(res, 201, { ok: true, id: r.rows[0].id, token });
    }

    // ── Rider: live status + cancel (needs the ride's own token) ──────────
    let m = path.match(/^\/api\/rides\/(\d+)\/(status|cancel)$/);
    if (m) {
      const id = m[1];
      const tok = m[2] === 'status' ? (url.searchParams.get('token') || '') : (await readJson(req)).token || '';
      const q = await pool.query('SELECT token,status,pickup,destination,driver_name,driver_plate,vehicle,est_text,lat,lng,dest_lat,dest_lng,driver_lat,driver_lng,driver_ts FROM rides WHERE id=$1', [id]);
      if (!q.rowCount || !q.rows[0].token || !safeEq(tok, q.rows[0].token)) return send(res, 404, { error: 'not found' });
      let r = q.rows[0];
      if (m[2] === 'cancel') {
        if (!['new', 'assigned'].includes(r.status)) return send(res, 409, { error: 'cannot cancel now' });
        r = (await pool.query(`UPDATE rides SET status='cancelled' WHERE id=$1 RETURNING token,status,pickup,destination,driver_name,driver_plate,vehicle,est_text,lat,lng,dest_lat,dest_lng,driver_lat,driver_lng,driver_ts`, [id])).rows[0];
      }
      delete r.token;
      return send(res, 200, r);
    }

    if (req.method === 'GET' && path === '/api/config') return send(res, 200, await getConfig());
    if (req.method === 'GET' && path === '/api/push/key') return send(res, 200, { key: PUSH_ON ? process.env.VAPID_PUBLIC : null });
    if (req.method === 'POST' && path === '/api/push/subscribe') {
      if (!isDriver(req)) return send(res, 401, { error: 'unauthorized' });
      const b = await readJson(req), sub = b.subscription;
      if (!sub || typeof sub.endpoint !== 'string' || !sub.keys) return send(res, 400, { error: 'bad subscription' });
      await pool.query(`INSERT INTO push_subs (endpoint, sub, role) VALUES ($1,$2,$3)
        ON CONFLICT (endpoint) DO UPDATE SET sub=$2, role=$3`, [sub.endpoint.slice(0, 500), JSON.stringify(sub), isAdmin(req) ? 'admin' : 'driver']);
      return send(res, 200, { ok: true });
    }
    if (req.method === 'PUT' && path === '/api/config') {
      if (!isAdmin(req)) return send(res, 401, { error: 'unauthorized' });
      const c = cleanConfig(await readJson(req));
      await pool.query(`INSERT INTO settings (key,value) VALUES ('config',$1) ON CONFLICT (key) DO UPDATE SET value=$1`, [JSON.stringify(c)]);
      return send(res, 200, await getConfig());
    }

    // ── Driver: list open + own rides, accept, progress ───────────────────
    if (path.startsWith('/api/driver/')) {
      if (!isDriver(req)) return send(res, 401, { error: 'unauthorized' });
      if (req.method === 'GET' && path === '/api/driver/rides') {
        const q = await pool.query(
          `SELECT ${COLS} FROM rides
           WHERE created_at > now() - interval '12 hours' AND status IN ('new','assigned','arrived','ontrip')
           ORDER BY created_at DESC LIMIT 100`);
        // riders' phone numbers are only shown once a driver has taken the ride
        return send(res, 200, { rides: q.rows.map(r => (r.status === 'new' ? { ...r, phone: null } : r)) });
      }
      m = path.match(/^\/api\/driver\/rides\/(\d+)\/pos$/);
      if (req.method === 'POST' && m) {
        const b = await readJson(req), la = num(b.lat, -90, 90), lo = num(b.lng, -180, 180);
        if (la == null || lo == null) return send(res, 400, { error: 'bad position' });
        const q = await pool.query(`UPDATE rides SET driver_lat=$2, driver_lng=$3, driver_ts=now()
          WHERE id=$1 AND status IN ('assigned','arrived','ontrip') AND driver_name=$4`, [m[1], la, lo, clean(b.driver_name, 60)]);
        return send(res, 200, { ok: q.rowCount === 1 });
      }
      m = path.match(/^\/api\/driver\/rides\/(\d+)\/(accept|status)$/);
      if (req.method === 'POST' && m) {
        const b = await readJson(req);
        if (m[2] === 'accept') {
          const name = clean(b.driver_name, 60), plate = clean(b.plate, 20);
          if (!name) return send(res, 400, { error: 'driver_name required' });
          const q = await pool.query(
            `UPDATE rides SET status='assigned', driver_name=$2, driver_plate=$3, accepted_at=now()
             WHERE id=$1 AND status='new' RETURNING ${COLS}`, [m[1], name, plate || null]);
          return q.rowCount ? send(res, 200, q.rows[0]) : send(res, 409, { error: 'already taken' });
        }
        const next = b.status;
        const from = { arrived: ['assigned'], ontrip: ['arrived', 'assigned'], done: ['ontrip', 'arrived'] }[next];
        if (!from) return send(res, 400, { error: 'bad status' });
        const q = await pool.query(`UPDATE rides SET status=$2 WHERE id=$1 AND status = ANY($3) RETURNING ${COLS}`, [m[1], next, from]);
        return q.rowCount ? send(res, 200, q.rows[0]) : send(res, 409, { error: 'wrong state' });
      }
      return send(res, 404, { error: 'not found' });
    }

    // ── Owner / dispatcher ────────────────────────────────────────────────
    if (path.startsWith('/api/rides')) {
      if (!isAdmin(req)) return send(res, 401, { error: 'unauthorized' });
      if (req.method === 'GET' && path === '/api/rides') {
        const status = url.searchParams.get('status');
        const q = STATUSES.includes(status)
          ? await pool.query(`SELECT ${COLS} FROM rides WHERE status=$1 ORDER BY created_at DESC LIMIT 200`, [status])
          : await pool.query(`SELECT ${COLS} FROM rides ORDER BY created_at DESC LIMIT 200`);
        return send(res, 200, { rides: q.rows });
      }
      m = path.match(/^\/api\/rides\/(\d+)$/);
      if (req.method === 'PATCH' && m) {
        const b = await readJson(req);
        if (b.status !== undefined && !STATUSES.includes(b.status)) return send(res, 400, { error: 'bad status' });
        const q = await pool.query(
          `UPDATE rides SET status=COALESCE($2,status), note=COALESCE($3,note),
             driver_name=COALESCE($4,driver_name), driver_plate=COALESCE($5,driver_plate)
           WHERE id=$1 RETURNING ${COLS}`,
          [m[1], b.status || null, b.note !== undefined ? clean(b.note, 500) : null,
           b.driver_name !== undefined ? clean(b.driver_name, 60) : null,
           b.driver_plate !== undefined ? clean(b.driver_plate, 20) : null]);
        return q.rowCount ? send(res, 200, q.rows[0]) : send(res, 404, { error: 'not found' });
      }
    }
    send(res, 404, { error: 'not found' });
  } catch (e) {
    console.error(e.message);
    send(res, e.message === 'bad json' || e.message === 'too large' ? 400 : 500, { error: 'error' });
  }
});

migrate().then(() => server.listen(PORT, () => console.log('joytaxi backend v2 on', PORT)))
  .catch(e => { console.error('startup failed:', e.message); process.exit(1); });
