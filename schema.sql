CREATE DATABASE IF NOT EXISTS aim_trainer_db;
USE aim_trainer_db;

CREATE TABLE IF NOT EXISTS aim_trainer_scores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  time_elapsed FLOAT NOT NULL,
  targets_hit INT NOT NULL,
  accuracy FLOAT NOT NULL
);
