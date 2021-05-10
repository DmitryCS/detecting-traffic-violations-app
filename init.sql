sudo -u postgres psql postgres
DROP DATABASE detections;
CREATE DATABASE detections;
CREATE USER user1 WITH PASSWORD 'qwerty';
GRANT ALL PRIVILEGES ON DATABASE "detections" to user1;