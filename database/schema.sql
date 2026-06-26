CREATE DATABASE IF NOT EXISTS diagcar_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE diagcar_ai;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80),
    email VARCHAR(160) NOT NULL UNIQUE,
    phone VARCHAR(40),
    password_hash VARCHAR(255) NOT NULL,
    car_brand VARCHAR(120),
    car_model VARCHAR(120),
    car_year INT NULL,
    fuel_type VARCHAR(80),
    transmission VARCHAR(80),
    mileage INT NULL,
    is_premium TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS diagnostic_cases (
    id_car INT PRIMARY KEY,
    categorie VARCHAR(120),
    sous_categorie VARCHAR(160),
    nom_francais VARCHAR(200),
    description_darija TEXT,
    description_arabe TEXT,
    mots_cles_fr TEXT,
    codes_obd VARCHAR(255),
    niveau_gravite VARCHAR(80),
    action_recommandee TEXT,
    source VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS diagnostics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    input_text TEXT NOT NULL,
    vehicle_snapshot JSON NULL,
    top_fault VARCHAR(200),
    probability DECIMAL(5,2),
    severity VARCHAR(80),
    obd_codes VARCHAR(255),
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Safe migration for existing databases created before the dashboard/chat redesign.
ALTER TABLE users ADD COLUMN IF NOT EXISTS car_brand VARCHAR(120) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS fuel_type VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS transmission VARCHAR(80) NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS mileage INT NULL;
ALTER TABLE diagnostics ADD COLUMN IF NOT EXISTS vehicle_snapshot JSON NULL;
