DZ Nova - Saved Vehicle Profile Update

What changed:
1. The user enters vehicle information only once during registration.
2. The dashboard displays the saved vehicle profile.
3. The diagnostic page is now an AI chat, not a repeated vehicle form.
4. /api/diagnose automatically uses the saved vehicle profile from the logged-in session.
5. Each diagnostic can store a vehicle_snapshot in the diagnostics table.

Database update for existing installations:
Open phpMyAdmin > diagcar_ai > SQL, then run:

ALTER TABLE users ADD COLUMN IF NOT EXISTS car_brand VARCHAR(120) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS fuel_type VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS transmission VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS mileage INT NULL;
ALTER TABLE diagnostics ADD COLUMN IF NOT EXISTS vehicle_snapshot JSON NULL;

For a fresh installation, importing database/schema.sql is enough.
