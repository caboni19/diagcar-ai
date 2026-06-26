USE diagcar_ai;

-- Run only the statements for columns that do not already exist in phpMyAdmin.
ALTER TABLE users ADD COLUMN car_brand VARCHAR(120) NULL;
ALTER TABLE users ADD COLUMN car_model VARCHAR(120) NULL;
ALTER TABLE users ADD COLUMN car_year INT NULL;
ALTER TABLE users ADD COLUMN fuel_type VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN transmission VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN mileage INT NULL;
ALTER TABLE diagnostics ADD COLUMN vehicle_snapshot JSON NULL;
