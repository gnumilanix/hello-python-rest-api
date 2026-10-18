-- upgrade

-- Convert comma-separated TEXT to a JSONB array.
-- Doctors have no seeded rows at this point, so a plain type change
-- with an empty-array default is sufficient.
ALTER TABLE doctors
    ALTER COLUMN phone_numbers TYPE JSONB
    USING '[]'::jsonb;

-- rollback

ALTER TABLE doctors
    ALTER COLUMN phone_numbers TYPE TEXT
    USING CASE
        WHEN phone_numbers IS NULL THEN NULL
        ELSE array_to_string(ARRAY(SELECT jsonb_array_elements_text(phone_numbers)), ',')
    END;
