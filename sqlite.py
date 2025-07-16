# Railway Reservation Project - SQLite Version
import sqlite3
from datetime import datetime

def connect_db():
    conn = sqlite3.connect("railway.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_db():
    conn = sqlite3.connect("railway.db")
    cursor = conn.cursor()

    with open("sqlite_schema.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
#print("SQLite database and tables created successfully!")

create_db()

# Inserting Trains into Tables
def add_default_trains():
    conn = connect_db()
    cursor = conn.cursor()

    # Check if any trains already exist
    cursor.execute("SELECT COUNT(*) FROM trains")
    count = cursor.fetchone()[0]

    if count == 0:
        default_trains = [
            "Intercity Express", "Train A", "Train B", "Train C", "Superfast Express"
        ]
        for train in default_trains:
            cursor.execute("INSERT INTO trains (name) VALUES (?)", (train,))
        print("✅ Default trains inserted.")

    conn.commit()
    conn.close()


add_default_trains()

# Inserting Classes into Tables
def add_default_classes():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM classes")
    count = cursor.fetchone()[0]

    if count == 0:
        default_classes = ["Sleeper", "AC", "General"]
        for cls in default_classes:
            cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (cls,))
        print("✅ Default classes inserted.")


    conn.commit()
    conn.close()

add_default_classes()
def account():
    conn = connect_db()
    cursor = conn.cursor()

    while True:
        login = input("Do you have an account? (yes/no): ").lower()

        if login == "yes":
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                print(f"Welcome back, {username}!")
                break
            else:
                print("Account not found or incorrect password. Please try again.\n")

        elif login == "no":
            print("Please create an account to continue.")
            username = input("Choose a username: ")
            password = input("Choose a password: ")

            try:
                query = "INSERT INTO users (username, password) VALUES (?, ?)"
                cursor.execute(query, (username, password))
                conn.commit()
                print(f"Account created successfully for {username}!")
                break
            except sqlite3.IntegrityError:
                print("⚠️ Username already exists. Try logging in or use a different username.\n")
        
        else:
            print("Invalid input. Please enter 'yes' or 'no'.\n")

    cursor.close()
    conn.close()
    return username

def passengers():
    num_passengers = int(input("Enter the number of passengers: "))
    passengers_list = []
    for i in range(num_passengers):
        name = input(f"Enter the name of passenger {i + 1}: ")
        age = int(input(f"Enter the age of passenger {i + 1}: "))
        passengers_list.append((name, age))
    return passengers_list

def train_selection():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM trains")
    trains = cursor.fetchall()
    if not trains:
        print("No trains available in database.")
        return None

    print("Available trains:")
    for i, (train_id, name) in enumerate(trains, start=1):
        print(f"{i}. {name}")
    choice = int(input("Select a train by number: "))
    if 1 <= choice <= len(trains):
        selected_train_id, selected_train_name = trains[choice - 1]
        return selected_train_id
    else:
        print("Invalid selection. Please try again.")
        return train_selection()

def chose_class():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, class_name FROM classes")
    classes = cursor.fetchall()
    if not classes:
        print("No classes available in database.")
        return None

    print("Available classes:")
    for i, (cls_id, name) in enumerate(classes, start=1):
        print(f"{i}. {name}")
    choice = int(input("Select a class by number: "))
    if 1 <= choice <= len(classes):
        selected_class_id, selected_class_name = classes[choice - 1]
        return selected_class_id
    else:
        print("Invalid selection. Please try again.")
        return chose_class()

def payment():
    print("Payment Options:")
    print("1. Credit Card")
    print("2. Debit Card")
    print("3. Net Banking")
    choice = int(input("Select a payment method by number: "))
    if choice in [1, 2, 3]:
        print("Payment successful!")
        return True
    else:
        print("Invalid selection. Please try again.")
        return payment()

def save_booking(username, passengers_list, train_id, class_id, booking_time):
    conn = connect_db()
    cursor = conn.cursor()

    # Get user ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_result = cursor.fetchone()
    if not user_result:
        print("User not found.")
        return
    user_id = user_result[0]

    # Insert booking
    cursor.execute("INSERT INTO bookings (user_id, train_id, class_id, booking_time) VALUES (?, ?, ?, ?)",
                   (user_id, train_id, class_id, booking_time))
    booking_id = cursor.lastrowid

    # Insert passengers
    for name, age in passengers_list:
        cursor.execute("INSERT INTO passengers (booking_id, name, age) VALUES (?, ?, ?)",
                       (booking_id, name, age))
    # Saving the Details to a text file 
    filename = f"{username}_booking.txt"
    with open(filename, "a") as file:
        file.write(f"\n----- Booking on {booking_time} -----\n")
        file.write(f"Username: {username}\n")
        file.write(f"Train: {train_id}\n")
        file.write(f"Class: {class_id}\n")
        file.write("Passengers:\n")
        for i, (name, age) in enumerate(passengers_list, start=1):
            file.write(f"  {i}. {name}, Age: {age}\n")
        file.write("----------------------------------------\n")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Booking details saved for {username}\n")


def view_past_bookings(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        print("User not found.")
        return
    user_id = user[0]

    query = """
    SELECT b.booking_time, t.name, c.class_name, p.name, p.age
    FROM bookings b
    JOIN trains t ON b.train_id = t.id
    JOIN classes c ON b.class_id = c.id
    JOIN passengers p ON b.id = p.booking_id
    WHERE b.user_id = ?
    ORDER BY b.booking_time DESC
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()

    if results:
        print(f"\nBooking history for {username}:")
        for booking_time, train, class_name, passenger_name, age in results:
            print(f"{booking_time}: {passenger_name} (Age {age}) - {train}, {class_name} class")
    else:
        print("No bookings found.")
    
   
    cursor.close()
    conn.close()

def delete_account(username):
    confirm = input(f"Are you sure you want to delete your account '{username}'? (yes/no): ").lower()
    if confirm == "yes":
        conn = connect_db()
        cursor = conn.cursor()

        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if not user:
            print("User not found.")
            return
        user_id = user[0]

        # Get booking IDs for this user
        cursor.execute("SELECT id FROM bookings WHERE user_id = ?", (user_id,))
        bookings = cursor.fetchall()

        # Delete passengers associated with bookings
        for booking in bookings:
            cursor.execute("DELETE FROM passengers WHERE booking_id = ?", (booking[0],))

        # Delete bookings
        cursor.execute("DELETE FROM bookings WHERE user_id = ?", (user_id,))
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        conn.commit()
        cursor.close()
        conn.close()

        print("Your account and all related bookings have been deleted successfully.")
    else:
        print("Account deletion cancelled.")

def main():
    print("Welcome to the Railway Reservation System!")
    username = account()

    print("\nWhat would you like to do?")
    print("1. View past bookings")
    print("2. Make a new booking")
    print("3. Delete your account")

    choice = input("Enter your choice (1/2/3): ")

    if choice == "1":
        view_past_bookings(username)
    elif choice == "2":
        passengers_list = passengers()
        train_id = train_selection()
        class_id = chose_class()
        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if payment():
            save_booking(username, passengers_list, train_id, class_id, booking_time)
            print("\nThank you for booking with us!")
        else:
            print("Payment failed. Please try again.")
    elif choice == "3":
        delete_account(username)
    else:
        print("Invalid choice. Please restart.")

    return "Process completed."

print(main())
