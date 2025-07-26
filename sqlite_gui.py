# GUI version of the Railway Reservation System using Tkinter + ttkbootstrap
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb

# --------- Database Setup Functions ---------
def connect_db():
    conn = sqlite3.connect("railway.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_trains():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM trains")
    trains = cursor.fetchall()
    conn.close()
    return trains

def get_classes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, class_name FROM classes")
    classes = cursor.fetchall()
    conn.close()
    return classes

# --------- Tkinter GUI Setup ---------
class RailwayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Reservation System")
        self.username = None
        self.build_login_screen()

    def build_login_screen(self):
        self.clear_window()
        tb.Label(self.root, text="Login / Register", font=("Arial", 16)).pack(pady=10)

        self.username_entry = tb.Entry(self.root, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "Username")

        self.password_entry = tb.Entry(self.root, show='*', width=30)
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Password")

        tb.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tb.Button(self.root, text="Register", command=self.register).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.username = username
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.build_menu()
        else:
            messagebox.showerror("Error", "Invalid login credentials")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    def build_menu(self):
        self.clear_window()
        tb.Label(self.root, text=f"Welcome, {self.username}", font=("Arial", 16)).pack(pady=10)
        tb.Button(self.root, text="Book Ticket", command=self.book_ticket).pack(pady=5)
        tb.Button(self.root, text="View Past Bookings", command=self.view_bookings).pack(pady=5)
        tb.Button(self.root, text="Delete Account", command=self.delete_account).pack(pady=5)
        tb.Button(self.root, text="Logout", command=self.build_login_screen).pack(pady=5)

    def book_ticket(self):
        self.clear_window()
        self.passenger_entries = []

        tb.Label(self.root, text="Number of Passengers:").pack()
        self.num_passengers = tb.Entry(self.root)
        self.num_passengers.pack()

        tb.Button(self.root, text="Continue", command=self.fill_passenger_details).pack(pady=10)

    def fill_passenger_details(self):
        try:
            num = int(self.num_passengers.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.passenger_entries = []
        for i in range(num):
            tb.Label(self.root, text=f"Passenger {i+1} Name").pack()
            name_entry = tb.Entry(self.root)
            name_entry.pack()
            tb.Label(self.root, text=f"Passenger {i+1} Age").pack()
            age_entry = tb.Entry(self.root)
            age_entry.pack()
            self.passenger_entries.append((name_entry, age_entry))

        self.trains = get_trains()
        self.classes = get_classes()

        tb.Label(self.root, text="Select Train:").pack()
        self.train_var = tk.StringVar()
        self.train_menu = ttk.Combobox(self.root, textvariable=self.train_var, values=[name for _, name in self.trains])
        self.train_menu.pack()

        tb.Label(self.root, text="Select Class:").pack()
        self.class_var = tk.StringVar()
        self.class_menu = ttk.Combobox(self.root, textvariable=self.class_var, values=[name for _, name in self.classes])
        self.class_menu.pack()

        tb.Button(self.root, text="Confirm Booking", command=self.confirm_booking).pack(pady=10)

    def confirm_booking(self):
        passengers = []
        try:
            for name_entry, age_entry in self.passenger_entries:
                name = name_entry.get()
                age = int(age_entry.get())
                passengers.append((name, age))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid passenger details")
            return

        train_id = self.trains[self.train_menu.current()][0]
        class_id = self.classes[self.class_menu.current()][0]
        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO bookings (user_id, train_id, class_id, booking_time) VALUES (?, ?, ?, ?)",
                       (user_id, train_id, class_id, booking_time))
        booking_id = cursor.lastrowid

        for name, age in passengers:
            cursor.execute("INSERT INTO passengers (booking_id, name, age) VALUES (?, ?, ?)", (booking_id, name, age))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Booking confirmed!")
        self.build_menu()

    def view_bookings(self):
        self.clear_window()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.booking_time, t.name, c.class_name, p.name, p.age
        FROM bookings b
        JOIN trains t ON b.train_id = t.id
        JOIN classes c ON b.class_id = c.id
        JOIN passengers p ON b.id = p.booking_id
        JOIN users u ON b.user_id = u.id
        WHERE u.username = ?
        ORDER BY b.booking_time DESC
        """, (self.username,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Info", "No bookings found.")
            self.build_menu()
            return

        for row in rows:
            tb.Label(self.root, text=f"{row[0]} - {row[3]} (Age {row[4]}) - {row[1]} - {row[2]}").pack()

        tb.Button(self.root, text="Back", command=self.build_menu).pack(pady=10)

    def delete_account(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete your account?")
        if not confirm:
            return
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("DELETE FROM passengers WHERE booking_id IN (SELECT id FROM bookings WHERE user_id = ?)", (user_id,))
        cursor.execute("DELETE FROM bookings WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Account deleted successfully.")
        self.build_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# --------- Launch the GUI ---------
if __name__ == '__main__':
    app_root = tb.Window(themename="superhero")  # You can choose from: superhero, flatly, minty, etc.
    app = RailwayApp(app_root)
    app_root.mainloop()
