-- upgrade

-- Backfill NULL phone_numbers to an empty array before enforcing NOT NULL.
UPDATE practitioners SET phone_numbers = '[]'::jsonb WHERE phone_numbers IS NULL;

ALTER TABLE practitioners
    ALTER COLUMN phone_numbers SET NOT NULL,
    ALTER COLUMN consultation_fee SET NOT NULL;

-- rollback

ALTER TABLE practitioners
    ALTER COLUMN phone_numbers DROP NOT NULL,
    ALTER COLUMN consultation_fee DROP NOT NULL;
