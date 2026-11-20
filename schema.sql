CREATE DATABASE IF NOT EXISTS migration_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE migration_demo;

CREATE TABLE IF NOT EXISTS customers (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  full_name    VARCHAR(150)  NOT NULL,
  email        VARCHAR(255)  NOT NULL,
  signup_date  DATE          NOT NULL,
  country      VARCHAR(50)   NOT NULL,
  total_spent  DECIMAL(10,2) NOT NULL,
  loaded_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_customers_email (email)
);
