-- upgrade

CREATE TABLE district (
    id SERIAL PRIMARY KEY,
    sort_order INTEGER NOT NULL
);

CREATE TABLE district_translations (
    district_id INTEGER NOT NULL REFERENCES district(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (district_id, language_code)
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name_key VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE category_translations (
    category_id INTEGER NOT NULL REFERENCES category(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (category_id, language_code)
);

-- One row per clinic listing: a practitioner with multiple clinics is
-- stored once per clinic (name clashes make deduplication unreliable).
-- place_id holds the Google Places ID for navigation.
-- phone_numbers is a comma-separated string.
-- is_open_on_public_holidays: HK clinics either open or close on public
-- holidays as a whole, regardless of which weekday a holiday falls on.
CREATE TABLE practitioners (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES category(id),
    district_id INTEGER NOT NULL REFERENCES district(id),
    place_id VARCHAR(255),
    phone_numbers TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    member_exclusive_fee INTEGER,
    consultation_fee INTEGER,
    is_open_on_public_holidays BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE practitioners_translations (
    practitioner_id INTEGER NOT NULL REFERENCES practitioners(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    fee_detail TEXT,
    PRIMARY KEY (practitioner_id, language_code)
);

-- day_of_week follows ISO 8601: 1 = Monday, 7 = Sunday.
CREATE TABLE operating_hours (
    id SERIAL PRIMARY KEY,
    practitioner_id INTEGER NOT NULL REFERENCES practitioners(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    open_time TIME NOT NULL,
    close_time TIME NOT NULL
);

-- rollback

DROP TABLE IF EXISTS operating_hours;
DROP TABLE IF EXISTS practitioners_translations;
DROP TABLE IF EXISTS practitioners;
DROP TABLE IF EXISTS category_translations;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS district_translations;
DROP TABLE IF EXISTS district;
