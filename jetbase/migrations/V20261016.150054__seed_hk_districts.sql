-- upgrade

-- The 18 districts of Hong Kong, sort_order follows English alphabetical order.
INSERT INTO district (id, sort_order) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (12, 12),
    (13, 13),
    (14, 14),
    (15, 15),
    (16, 16),
    (17, 17),
    (18, 18);

ALTER SEQUENCE district_id_seq RESTART WITH 19;

INSERT INTO district_translations (district_id, language_code, name) VALUES
    (1, 'en-US', 'Central and Western'),
    (1, 'zh-HK', '中西區'),
    (2, 'en-US', 'Eastern'),
    (2, 'zh-HK', '東區'),
    (3, 'en-US', 'Islands'),
    (3, 'zh-HK', '離島區'),
    (4, 'en-US', 'Kowloon City'),
    (4, 'zh-HK', '九龍城區'),
    (5, 'en-US', 'Kwai Tsing'),
    (5, 'zh-HK', '葵青區'),
    (6, 'en-US', 'Kwun Tong'),
    (6, 'zh-HK', '觀塘區'),
    (7, 'en-US', 'North'),
    (7, 'zh-HK', '北區'),
    (8, 'en-US', 'Sai Kung'),
    (8, 'zh-HK', '西貢區'),
    (9, 'en-US', 'Sha Tin'),
    (9, 'zh-HK', '沙田區'),
    (10, 'en-US', 'Sham Shui Po'),
    (10, 'zh-HK', '深水埗區'),
    (11, 'en-US', 'Southern'),
    (11, 'zh-HK', '南區'),
    (12, 'en-US', 'Tai Po'),
    (12, 'zh-HK', '大埔區'),
    (13, 'en-US', 'Tsuen Wan'),
    (13, 'zh-HK', '荃灣區'),
    (14, 'en-US', 'Tuen Mun'),
    (14, 'zh-HK', '屯門區'),
    (15, 'en-US', 'Wan Chai'),
    (15, 'zh-HK', '灣仔區'),
    (16, 'en-US', 'Wong Tai Sin'),
    (16, 'zh-HK', '黃大仙區'),
    (17, 'en-US', 'Yau Tsim Mong'),
    (17, 'zh-HK', '油尖旺區'),
    (18, 'en-US', 'Yuen Long'),
    (18, 'zh-HK', '元朗區');

-- rollback

DELETE FROM district_translations WHERE district_id BETWEEN 1 AND 18;
DELETE FROM district WHERE id BETWEEN 1 AND 18;
ALTER SEQUENCE district_id_seq RESTART WITH 1;
