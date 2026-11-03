# Joy Taxi backend (v2)

Env: `DATABASE_URL`, `ADMIN_TOKEN`, `DRIVER_TOKEN`, `ALLOWED_ORIGINS` (default https://joytaxi.cierp.uk).

Public: `POST /api/rides` -> `{id, token}`; `GET /api/rides/:id/status?token=`; `POST /api/rides/:id/cancel {token}`
Driver (Bearer DRIVER_TOKEN): `GET /api/driver/rides`; `POST /api/driver/rides/:id/accept {driver_name, plate}`; `POST /api/driver/rides/:id/status {status: arrived|ontrip|done}`
Owner (Bearer ADMIN_TOKEN): `GET /api/rides[?status=]`; `PATCH /api/rides/:id`
Statuses: new, confirmed, assigned, arrived, ontrip, done, cancelled.
