-- upgrade

-- Backfill NULL phone_numbers to an empty array before enforcing NOT NULL.
UPDATE doctors SET phone_numbers = '[]'::jsonb WHERE phone_numbers IS NULL;

ALTER TABLE doctors
    ALTER COLUMN phone_numbers SET NOT NULL,
    ALTER COLUMN consultation_fee SET NOT NULL;

-- rollback

ALTER TABLE doctors
    ALTER COLUMN phone_numbers DROP NOT NULL,
    ALTER COLUMN consultation_fee DROP NOT NULL;
