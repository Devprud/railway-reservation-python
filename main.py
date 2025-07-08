# Railway Reservation Project - 08-07-2025
import mysql.connector
from datetime import datetime


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="prudhivi141008devesh*",
        database="railway_db"
    )

def greet():
    print("Welcome to the Railway Reservation System!")
    print("Please follow the prompts to book your tickets.")
    login = str(input("Do you have an account? (yes/no): "))
    return login.lower()

def account():
    conn = connect_db()
    cursor = conn.cursor()

    while True:
        login = input("Do you have an account? (yes/no): ").lower()

        if login == "yes":
            username = input("Enter your username: ")
            password = input("Enter your password: ")

            query = "SELECT * FROM users WHERE username = %s AND password = %s"
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
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username, password))
                conn.commit()
                print(f"Account created successfully for {username}!")
                break
            except mysql.connector.IntegrityError:
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
    print("Available trains:")
    trains = ["Train A", "Train B", "Train C"]
    for i, train in enumerate(trains, start=1):
        print(f"{i}. {train}")
    choice = int(input("Select a train by number: "))
    if 1 <= choice <= len(trains):
        selected_train = trains[choice - 1]
        print(f"You have selected {selected_train}.")
        return selected_train
    else:
        print("Invalid selection. Please try again.")
        return train_selection()

def chose_class():
    print("Available classes:")
    classes = ["Sleeper", "AC", "General"]
    for i, cls in enumerate(classes, start=1):
        print(f"{i}. {cls}")
    choice = int(input("Select a class by number: "))
    if 1 <= choice <= len(classes):
        selected_class = classes[choice - 1]
        print(f"You have selected {selected_class} class.")
        return selected_class
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
    
def save_booking_to_file(username, passengers_list, selected_train, selected_class, booking_time):
    filename = f"{username}_booking.txt"
    with open(filename, "a") as file:
        file.write(f"\n----- Booking on {booking_time} -----\n")
        file.write(f"Username: {username}\n")
        file.write(f"Train: {selected_train}\n")
        file.write(f"Class: {selected_class}\n")
        file.write("Passengers:\n")
        for i, (name, age) in enumerate(passengers_list, start=1):
            file.write(f"  {i}. {name}, Age: {age}\n")
        file.write("----------------------------------------\n")

def save_booking_to_database(username, passengers_list, selected_train, selected_class, booking_time):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO bookings (username, train, class, passenger_name, passenger_age, booking_time)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for passenger in passengers_list:
        name, age = passenger
        cursor.execute(query, (username, selected_train, selected_class, name, age, booking_time))

    conn.commit()
    cursor.close()
    conn.close()

def view_past_bookings(username):
    conn = connect_db()
    cursor = conn.cursor()
    
    query = "SELECT train, class, passenger_name, passenger_age, booking_time FROM bookings WHERE username = %s ORDER BY booking_time DESC"
    cursor.execute(query, (username,))
    results = cursor.fetchall()
    
    if results:
        print(f"\nBooking history for {username}:")
        for row in results:
            train, travel_class, name, age, time = row
            print(f"{time}: {name} (Age {age}) - {train}, {travel_class} class")
    else:
        print("No bookings found.")
    
    cursor.close()
    conn.close()

def delete_account(username):
    confirm = input(f"Are you sure you want to delete your account '{username}'? (yes/no): ").lower()
    if confirm == "yes":
        conn = connect_db()
        cursor = conn.cursor()

        # Delete from bookings table
        cursor.execute("DELETE FROM bookings WHERE username = %s", (username,))
        # Delete from users table
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))

        conn.commit()
        cursor.close()
        conn.close()

        print("Your account and all related bookings have been deleted successfully.")
    else:
        print("Account deletion cancelled.")


def main():
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
        selected_train = train_selection()
        selected_class = chose_class()
        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nBooking details for {username}:")
        print(f"Passengers: {passengers_list}")
        print(f"Selected Train: {selected_train}")
        print(f"Selected Class: {selected_class}")

        if payment():
            save_booking_to_file(username, passengers_list, selected_train, selected_class, booking_time)
            save_booking_to_database(username, passengers_list, selected_train, selected_class, booking_time)
            print("\nThank you for booking with us!")
        else:
            print("Payment failed. Please try again.")

    elif choice == "3":
        delete_account(username)

    else:
        print("Invalid choice. Please restart.")

    return "Process completed."

print(main())
