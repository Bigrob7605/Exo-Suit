--  Test SQL File
-- Testing emoji detection in SQL files

--  Create test table
CREATE TABLE emoji_test (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    status VARCHAR(50),
    mode VARCHAR(50),
    version VARCHAR(20)
);

--  Insert test data
INSERT INTO emoji_test (id, name, status, mode, version) VALUES
(1, ' Emoji detection', ' Active', ' Test Mode', ' V1.0'),
(2, ' Testing capabilities', ' Active', ' Test Mode', ' V1.0'),
(3, ' Small file size', ' Active', ' Test Mode', ' V1.0');

--  Select test data
SELECT * FROM emoji_test WHERE status = ' Active';
