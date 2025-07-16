import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import mysql.connector

# ---------- Database Connection ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="prudhivi141008devesh*",
        database="railway_db"
    )

# ---------- Main GUI App ----------
class RailwayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Reservation System")
        self.username = None
        self.login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome to Railway Reservation System", font=("Helvetica", 16)).pack(pady=10)

        tk.Label(self.root, text="Username").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack()

        tk.Label(self.root, text="Password").pack()
        password_entry = tk.Entry(self.root, show='*')
        password_entry.pack()

        def login():
            username = username_entry.get()
            password = password_entry.get()
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            conn.close()
            if result:
                self.username = username
                self.main_menu()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        def register():
            username = username_entry.get()
            password = password_entry.get()
            conn = connect_db()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Account created! Please log in.")
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            conn.close()

        tk.Button(self.root, text="Login", command=login).pack(pady=5)
        tk.Button(self.root, text="Register", command=register).pack()

    def main_menu(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.username}", font=("Helvetica", 14)).pack(pady=10)
        tk.Button(self.root, text="View Past Bookings", width=30, command=self.view_bookings).pack(pady=5)
        tk.Button(self.root, text="Make a Booking", width=30, command=self.make_booking).pack(pady=5)
        tk.Button(self.root, text="Delete Account", width=30, command=self.delete_account).pack(pady=5)
        tk.Button(self.root, text="Logout", width=30, command=self.login_screen).pack(pady=5)

    def view_bookings(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT train, class, passenger_name, passenger_age, booking_time FROM bookings WHERE username = %s ORDER BY booking_time DESC", (self.username,))
        records = cursor.fetchall()
        conn.close()

        self.clear_screen()
        tk.Label(self.root, text="Booking History", font=("Helvetica", 14)).pack(pady=10)
        if records:
            for record in records:
                info = f"{record[4]}: {record[2]} (Age {record[3]}) - {record[0]}, {record[1]} class"
                tk.Label(self.root, text=info).pack()
        else:
            tk.Label(self.root, text="No bookings found.").pack()

        tk.Button(self.root, text="Back", command=self.main_menu).pack(pady=10)

    def make_booking(self):
        passengers_list = []
        num = simpledialog.askinteger("Passengers", "Enter number of passengers:")

        if not num: return

        for i in range(num):
            name = simpledialog.askstring("Passenger Name", f"Enter name of passenger {i + 1}:")
            age = simpledialog.askinteger("Passenger Age", f"Enter age of passenger {i + 1}:")
            passengers_list.append((name, age))

        trains = ["Train A", "Train B", "Train C"]
        selected_train = simpledialog.askinteger("Train Selection", "1. Train A\n2. Train B\n3. Train C\nSelect train (1/2/3):")
        if not selected_train or not (1 <= selected_train <= len(trains)):
            messagebox.showerror("Error", "Invalid train selected.")
            return
        train = trains[selected_train - 1]

        classes = ["Sleeper", "AC", "General"]
        selected_class = simpledialog.askinteger("Class", "1. Sleeper\n2. AC\n3. General\nSelect class (1/2/3):")
        if not selected_class or not (1 <= selected_class <= len(classes)):
            messagebox.showerror("Error", "Invalid class selected.")
            return
        cls = classes[selected_class - 1]

        pay = messagebox.askyesno("Payment", "Proceed with payment?")
        if pay:
            booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_booking_to_db(passengers_list, train, cls, booking_time)
            self.save_booking_to_file(passengers_list, train, cls, booking_time)
            messagebox.showinfo("Success", "Booking completed successfully.")
        else:
            messagebox.showinfo("Cancelled", "Booking cancelled.")

    def save_booking_to_db(self, passengers, train, cls, time):
        conn = connect_db()
        cursor = conn.cursor()
        query = "INSERT INTO bookings (username, train, class, passenger_name, passenger_age, booking_time) VALUES (%s, %s, %s, %s, %s, %s)"
        for p in passengers:
            cursor.execute(query, (self.username, train, cls, p[0], p[1], time))
        conn.commit()
        conn.close()

    def save_booking_to_file(self, passengers, train, cls, time):
        filename = f"{self.username}_booking.txt"
        with open(filename, "a") as file:
            file.write(f"\n----- Booking on {time} -----\n")
            file.write(f"Train: {train}\nClass: {cls}\nPassengers:\n")
            for i, (name, age) in enumerate(passengers, 1):
                file.write(f"  {i}. {name}, Age: {age}\n")
            file.write("----------------------------------------\n")

    def delete_account(self):
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete your account '{self.username}'?")
        if confirm:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE username = %s", (self.username,))
            cursor.execute("DELETE FROM users WHERE username = %s", (self.username,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Account and bookings deleted.")
            self.login_screen()


# ---------- Run App ----------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x500")
    app = RailwayApp(root)
    root.mainloop()
