-- upgrade

-- necktie core schema.
--
-- Design notes:
-- - One row per clinic listing: a doctor with multiple clinics is stored once
--   per clinic (name clashes make deduplication unreliable), so there is no
--   separate clinic table.
-- - place_id holds the Google Places ID for navigation.
-- - phone_numbers is a JSONB array of validated HK numbers.
-- - is_open_on_public_holidays: HK clinics either open or close on public
--   holidays as a whole, regardless of which weekday a holiday falls on.
-- - Translatable fields are fixed per-language columns (en/yue/zh): the product
--   serves Hong Kong only, so the language set is closed. See README.
-- - day_of_week follows ISO 8601: 1 = Monday, 7 = Sunday.

CREATE TABLE district (
    id SERIAL PRIMARY KEY,
    sort_order INTEGER NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_yue VARCHAR(255) NOT NULL,
    name_zh VARCHAR(255) NOT NULL
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name_key VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(255) NOT NULL,
    name_yue VARCHAR(255) NOT NULL,
    name_zh VARCHAR(255) NOT NULL
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES category(id),
    district_id INTEGER NOT NULL REFERENCES district(id),
    place_id VARCHAR(255),
    phone_numbers JSONB NOT NULL DEFAULT '[]'::jsonb,
    member_exclusive_fee INTEGER,
    consultation_fee INTEGER NOT NULL,
    is_open_on_public_holidays BOOLEAN NOT NULL DEFAULT FALSE,
    name_en VARCHAR(255) NOT NULL,
    name_yue VARCHAR(255) NOT NULL,
    name_zh VARCHAR(255) NOT NULL,
    address_en TEXT NOT NULL,
    address_yue TEXT NOT NULL,
    address_zh TEXT NOT NULL,
    fee_detail_en TEXT,
    fee_detail_yue TEXT,
    fee_detail_zh TEXT
);

CREATE TABLE operating_hours (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL
);

-- rollback

DROP TABLE IF EXISTS operating_hours;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS district;
