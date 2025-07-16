CREATE DATABASE railway_database;
USE railway_database;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
CREATE TABLE trains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
CREATE TABLE classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(30) NOT NULL
);
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    train_id INT,
    class_id INT,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
CREATE TABLE passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    name VARCHAR(50),
    age INT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    passenger_name VARCHAR(100),
    passenger_age INT,
    train VARCHAR(50),
    class VARCHAR(20),
    booking_time DATETIME
);


