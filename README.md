# Joy Taxi — booking-request backend

Records each ride request made on https://joytaxi.cierp.uk so the owner can dispatch from a list.
WhatsApp remains the booking channel; the site posts here in the background and a failure here never blocks it.

Env: `DATABASE_URL`, `ADMIN_TOKEN` (long random string), `ALLOWED_ORIGINS` (default `https://joytaxi.cierp.uk`), `PORT`.

- `POST /api/rides` public, from the site: `{pickup, destination, when, est_km, est_text, lang}`
- `GET /api/rides?status=new` owner (`Authorization: Bearer <ADMIN_TOKEN>`)
- `PATCH /api/rides/:id` owner: `{status: new|confirmed|assigned|done|cancelled, note}`
- `GET /health`

Stored: pickup, destination, requested time, estimate, language. No names, phone numbers or accounts.
