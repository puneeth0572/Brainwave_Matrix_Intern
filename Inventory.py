import tkinter as tk
from tkinter import messagebox
import sqlite3

# Function to create and initialize the database (if not already created)
def initialize_database():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    # Create Users table (for authentication)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                 )''')

    # Create Products table (for product management)
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL
                 )''')

    conn.commit()
    conn.close()

# Initialize the database (run once)
initialize_database()

# Function to hash passwords (for user authentication)
import hashlib
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate the user (check credentials)
def authenticate_user(username, password):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    hashed_password = hash_password(password)
    
    # Check if the user exists and the password matches
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()

    return user is not None

# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    hashed_password = hash_password(password)
    
    # Insert user into the Users table
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Error", "Username already exists.")
    finally:
        conn.close()

# Function to add a product to the database
def add_product(name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

# Function to edit an existing product
def edit_product(product_id, name, quantity, price):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("UPDATE products SET name = ?, quantity = ?, price = ? WHERE id = ?", (name, quantity, price, product_id))
    conn.commit()
    conn.close()

# Function to delete a product by ID
def delete_product(product_id):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# Function to get all products in the inventory
def get_all_products():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

# Function to check for low stock products
def check_low_stock(threshold=5):
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE quantity < ?", (threshold,))
    low_stock_products = c.fetchall()
    conn.close()
    return low_stock_products

# Function to display all products in the listbox
def display_products():
    products = get_all_products()
    products_listbox.delete(0, tk.END)  # Clear existing list
    for product in products:
        products_listbox.insert(tk.END, f"ID: {product[0]} | Name: {product[1]} | Quantity: {product[2]} | Price: {product[3]}")

# Function to handle adding a new product from the GUI
def add_product_gui():
    name = product_name_entry.get()
    try:
        quantity = int(product_quantity_entry.get())
        price = float(product_price_entry.get())
        add_product(name, quantity, price)
        display_products()
        clear_product_form()
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid quantity and price.")

# Function to handle deleting a product from the GUI
def delete_product_gui():
    try:
        product_id = int(product_id_entry.get())
        delete_product(product_id)
        display_products()
        product_id_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid ID", "Please enter a valid product ID.")

# Function to handle editing a product from the GUI
def edit_product_gui():
    try:
        product_id = int(product_id_entry.get())
        name = product_name_entry.get()
        quantity = int(product_quantity_entry.get())
        price = float(product_price_entry.get())
        edit_product(product_id, name, quantity, price)
        display_products()
        clear_product_form()
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid product details.")

# Function to show low stock products
def show_low_stock():
    low_stock = check_low_stock()
    if low_stock:
        messagebox.showinfo("Low Stock", f"Low stock products:\n" + "\n".join([f"{product[1]} ({product[2]} units)" for product in low_stock]))
    else:
        messagebox.showinfo("Low Stock", "No low stock products.")

# Function to clear the product form inputs
def clear_product_form():
    product_name_entry.delete(0, tk.END)
    product_quantity_entry.delete(0, tk.END)
    product_price_entry.delete(0, tk.END)

# Function to handle login
def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    if authenticate_user(username, password):
        messagebox.showinfo("Login Successful", "Welcome to the Inventory System!")
        login_window.destroy()
        create_inventory_window()  # Open the inventory window after successful login
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Function to create the inventory window (after successful login)
def create_inventory_window():
    inventory_window = tk.Tk()
    inventory_window.title("Inventory Management System")

    # Product Entry Form
    tk.Label(inventory_window, text="Product Name").grid(row=0, column=0)
    global product_name_entry
    product_name_entry = tk.Entry(inventory_window)
    product_name_entry.grid(row=0, column=1)

    tk.Label(inventory_window, text="Product Quantity").grid(row=1, column=0)
    global product_quantity_entry
    product_quantity_entry = tk.Entry(inventory_window)
    product_quantity_entry.grid(row=1, column=1)

    tk.Label(inventory_window, text="Product Price").grid(row=2, column=0)
    global product_price_entry
    product_price_entry = tk.Entry(inventory_window)
    product_price_entry.grid(row=2, column=1)

    tk.Button(inventory_window, text="Add Product", command=add_product_gui).grid(row=3, column=0, columnspan=2)
    tk.Button(inventory_window, text="Edit Product", command=edit_product_gui).grid(row=4, column=0, columnspan=2)
    tk.Button(inventory_window, text="Delete Product", command=delete_product_gui).grid(row=5, column=0, columnspan=2)

    # Product List
    global products_listbox
    products_listbox = tk.Listbox(inventory_window, height=10, width=50)
    products_listbox.grid(row=6, column=0, columnspan=2)

    # Product ID to delete or edit
    tk.Label(inventory_window, text="Product ID to Edit/Delete").grid(row=7, column=0)
    global product_id_entry
    product_id_entry = tk.Entry(inventory_window)
    product_id_entry.grid(row=7, column=1)

    # Low Stock Button
    tk.Button(inventory_window, text="Check Low Stock", command=show_low_stock).grid(row=8, column=0, columnspan=2)

    # Display all products initially
    display_products()

    inventory_window.mainloop()

# Create the login window
login_window = tk.Tk()
login_window.title("Login")

tk.Label(login_window, text="Username").grid(row=0, column=0)
username_entry = tk.Entry(login_window)
username_entry.grid(row=0, column=1)

tk.Label(login_window, text="Password").grid(row=1, column=0)
password_entry = tk.Entry(login_window, show="*")
password_entry.grid(row=1, column=1)

tk.Button(login_window, text="Login", command=handle_login).grid(row=2, column=0, columnspan=2)

tk.Button(login_window, text="Register", command=lambda: register_user("admin", "admin")).grid(row=3, column=0, columnspan=2)

login_window.mainloop()
import csv

def export_sales_report():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    c.execute("SELECT * FROM sales")
    sales_data = c.fetchall()

    with open("sales_report.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Sale ID", "Product ID", "Quantity", "Sale Date", "Total Price"])
        writer.writerows(sales_data)

    conn.close()

    messagebox.showinfo("Export Successful", "Sales report exported to sales_report.csv.")

import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv

# Function to export the sales report to a CSV file
def export_sales_report():
    try:
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()

        # Query to get all sales data
        c.execute("SELECT id, product_id, quantity, sale_date, total_price FROM sales")
        sales_data = c.fetchall()

        if sales_data:
            # Create and write to CSV file
            with open("sales_report.csv", mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Sale ID", "Product ID", "Quantity", "Sale Date", "Total Price"])
                writer.writerows(sales_data)
            
            messagebox.showinfo("Export Successful", "Sales report exported to sales_report.csv.")
        else:
            messagebox.showwarning("No Sales Data", "No sales data to export.")
        
        conn.close()
    except Exception as e:
        messagebox.showerror("Export Failed", f"An error occurred: {e}")

# Function to create the inventory window and add the export button
def create_inventory_window():
    inventory_window = tk.Tk()
    inventory_window.title("Inventory Management")

    # Add a label and button to export sales report
    tk.Label(inventory_window, text="Inventory Management System").pack(pady=10)

    # Button to export sales report
    export_button = tk.Button(inventory_window, text="Export Sales Report", command=export_sales_report)
    export_button.pack(pady=20)

    # Other inventory management controls (e.g., add, edit, delete products, etc.)
    # You can add other widgets here based on your needs.

    inventory_window.mainloop()

# Call this function to start the application
create_inventory_window()
