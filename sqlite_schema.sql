-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Trains Table
CREATE TABLE IF NOT EXISTS trains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Classes Table
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    train_id INTEGER,
    class_id INTEGER,
    booking_time TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);



-- Passengers Table
CREATE TABLE IF NOT EXISTS passengers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER,
    name TEXT,
    age INTEGER,
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);


-- -- Trains 
-- INSERT INTO trains (name) VALUES
-- ('Train A'),
-- ('Train B'),
-- ('Train C'),
-- ('Superfast Express'),
-- ('Intercity Express');

-- -- Classes
-- INSERT INTO classes (class_name) VALUES
-- ('Sleeper'),
-- ('AC'),
-- ('General');

-- DELETE FROM trains;
-- DELETE FROM classes;
-- SELECT * FROM bookings;