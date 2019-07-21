CREATE DATABASE urls;
use urls;

CREATE TABLE urls (
  id INT AUTO_INCREMENT PRIMARY KEY,
  short_url VARCHAR(50),
  long_url VARCHAR(50)
);

INSERT INTO urls
  (short_url, long_url)
VALUES
  ('UWY8JFWaCBe5', 'www.google.com')
