-- upgrade

-- Convert comma-separated TEXT to a JSONB array, preserving existing data.
ALTER TABLE practitioners
    ALTER COLUMN phone_numbers TYPE JSONB
    USING CASE
        WHEN phone_numbers IS NULL OR btrim(phone_numbers) = '' THEN NULL
        ELSE to_jsonb(
            ARRAY(SELECT btrim(x) FROM unnest(string_to_array(phone_numbers, ',')) AS x)
        )
    END;

-- rollback

ALTER TABLE practitioners
    ALTER COLUMN phone_numbers TYPE TEXT
    USING CASE
        WHEN phone_numbers IS NULL THEN NULL
        ELSE array_to_string(ARRAY(SELECT jsonb_array_elements_text(phone_numbers)), ',')
    END;
