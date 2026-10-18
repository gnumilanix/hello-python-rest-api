-- upgrade

ALTER TABLE doctors DROP COLUMN is_active;

-- rollback

ALTER TABLE doctors ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
