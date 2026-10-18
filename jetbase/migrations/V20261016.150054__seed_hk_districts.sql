-- upgrade

-- The 18 districts of Hong Kong, sort_order follows English alphabetical order.
INSERT INTO district (id, sort_order, name_en, name_yue, name_zh) VALUES
    (1, 1, 'Central and Western', '中西區', '中西區'),
    (2, 2, 'Eastern', '東區', '東區'),
    (3, 3, 'Islands', '離島區', '離島區'),
    (4, 4, 'Kowloon City', '九龍城區', '九龍城區'),
    (5, 5, 'Kwai Tsing', '葵青區', '葵青區'),
    (6, 6, 'Kwun Tong', '觀塘區', '觀塘區'),
    (7, 7, 'North', '北區', '北區'),
    (8, 8, 'Sai Kung', '西貢區', '西貢區'),
    (9, 9, 'Sha Tin', '沙田區', '沙田區'),
    (10, 10, 'Sham Shui Po', '深水埗區', '深水埗區'),
    (11, 11, 'Southern', '南區', '南區'),
    (12, 12, 'Tai Po', '大埔區', '大埔區'),
    (13, 13, 'Tsuen Wan', '荃灣區', '荃灣區'),
    (14, 14, 'Tuen Mun', '屯門區', '屯門區'),
    (15, 15, 'Wan Chai', '灣仔區', '灣仔區'),
    (16, 16, 'Wong Tai Sin', '黃大仙區', '黃大仙區'),
    (17, 17, 'Yau Tsim Mong', '油尖旺區', '油尖旺區'),
    (18, 18, 'Yuen Long', '元朗區', '元朗區');

ALTER SEQUENCE district_id_seq RESTART WITH 19;

-- rollback

DELETE FROM district WHERE id BETWEEN 1 AND 18;
ALTER SEQUENCE district_id_seq RESTART WITH 1;
