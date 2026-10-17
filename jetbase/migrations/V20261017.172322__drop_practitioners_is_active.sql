-- upgrade

ALTER TABLE practitioners DROP COLUMN is_active;

-- rollback

ALTER TABLE practitioners ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
