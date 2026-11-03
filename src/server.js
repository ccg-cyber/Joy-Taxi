'use strict';
// Joy Taxi booking-request backend. Zero framework: node:http + pg.
// WhatsApp stays the booking channel; this only records each request for dispatch.
const http = require('node:http');
const crypto = require('node:crypto');
const { Pool } = require('pg');

const PORT = process.env.PORT || 3000;
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '';
const ORIGINS = (process.env.ALLOWED_ORIGINS || 'https://joytaxi.cierp.uk')
  .split(',').map(s => s.trim()).filter(Boolean);

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL && !/localhost|127\.0\.0\.1/.test(process.env.DATABASE_URL)
    ? { rejectUnauthorized: false } : false,
});

const STATUSES = ['new', 'confirmed', 'assigned', 'done', 'cancelled'];

async function migrate() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS rides (
      id          BIGSERIAL PRIMARY KEY,
      created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
      pickup      TEXT NOT NULL,
      destination TEXT NOT NULL,
      when_text   TEXT NOT NULL DEFAULT 'now',
      est_km      NUMERIC,
      est_text    TEXT,
      lang        TEXT NOT NULL DEFAULT 'en',
      status      TEXT NOT NULL DEFAULT 'new',
      note        TEXT
    );
    CREATE INDEX IF NOT EXISTS rides_created_idx ON rides (created_at DESC);
  `);
}

// ── tiny in-memory rate limit: 10 requests / 10 min / IP ──────────────────
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
function isAdmin(req) {
  if (!ADMIN_TOKEN) return false;
  const h = req.headers.authorization || '';
  const t = h.startsWith('Bearer ') ? h.slice(7) : '';
  const a = Buffer.from(t), b = Buffer.from(ADMIN_TOKEN);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const server = http.createServer(async (req, res) => {
  cors(req, res);
  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }
  const url = new URL(req.url, 'http://x');
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  try {
    if (url.pathname === '/health') {
      await pool.query('SELECT 1');
      return send(res, 200, { ok: true });
    }

    // Public: site posts a ride request. Fire-and-forget from the browser.
    if (req.method === 'POST' && url.pathname === '/api/rides') {
      const origin = req.headers.origin;
      if (origin && !ORIGINS.includes(origin)) return send(res, 403, { error: 'forbidden' });
      if (limited(ip)) return send(res, 429, { error: 'slow down' });
      const b = await readJson(req);
      if (b.website) return send(res, 200, { ok: true }); // honeypot: pretend success
      const pickup = clean(b.pickup, 200), destination = clean(b.destination, 200);
      if (!pickup && !destination) return send(res, 400, { error: 'pickup or destination required' });
      const km = Number.isFinite(+b.est_km) && +b.est_km >= 0 && +b.est_km < 2000 ? +b.est_km : null;
      const r = await pool.query(
        `INSERT INTO rides (pickup,destination,when_text,est_km,est_text,lang)
         VALUES ($1,$2,$3,$4,$5,$6) RETURNING id`,
        [pickup || '—', destination || '—', clean(b.when, 80) || 'now', km,
         clean(b.est_text, 120) || null, b.lang === 'ar' ? 'ar' : 'en']);
      return send(res, 201, { ok: true, id: r.rows[0].id });
    }

    // Owner-only below.
    if (url.pathname.startsWith('/api/rides')) {
      if (!isAdmin(req)) return send(res, 401, { error: 'unauthorized' });

      if (req.method === 'GET' && url.pathname === '/api/rides') {
        const status = url.searchParams.get('status');
        const q = STATUSES.includes(status)
          ? await pool.query('SELECT * FROM rides WHERE status=$1 ORDER BY created_at DESC LIMIT 200', [status])
          : await pool.query('SELECT * FROM rides ORDER BY created_at DESC LIMIT 200');
        return send(res, 200, { rides: q.rows });
      }
      const m = url.pathname.match(/^\/api\/rides\/(\d+)$/);
      if (req.method === 'PATCH' && m) {
        const b = await readJson(req);
        if (b.status !== undefined && !STATUSES.includes(b.status)) return send(res, 400, { error: 'bad status' });
        const q = await pool.query(
          `UPDATE rides SET status=COALESCE($2,status), note=COALESCE($3,note) WHERE id=$1 RETURNING *`,
          [m[1], b.status || null, b.note !== undefined ? clean(b.note, 500) : null]);
        return q.rowCount ? send(res, 200, q.rows[0]) : send(res, 404, { error: 'not found' });
      }
    }
    send(res, 404, { error: 'not found' });
  } catch (e) {
    console.error(e.message);
    send(res, e.message === 'bad json' || e.message === 'too large' ? 400 : 500, { error: 'error' });
  }
});

migrate().then(() => server.listen(PORT, () => console.log('joytaxi backend on', PORT)))
  .catch(e => { console.error('startup failed:', e.message); process.exit(1); });
