-- upgrade

-- BCP 47 (RFC 5646 §4.4.1): language tags need up to 35 chars.
ALTER TABLE district_translations ALTER COLUMN language_code TYPE VARCHAR(35);
ALTER TABLE category_translations ALTER COLUMN language_code TYPE VARCHAR(35);
ALTER TABLE practitioners_translations ALTER COLUMN language_code TYPE VARCHAR(35);

-- rollback

ALTER TABLE district_translations ALTER COLUMN language_code TYPE VARCHAR(10);
ALTER TABLE category_translations ALTER COLUMN language_code TYPE VARCHAR(10);
ALTER TABLE practitioners_translations ALTER COLUMN language_code TYPE VARCHAR(10);
