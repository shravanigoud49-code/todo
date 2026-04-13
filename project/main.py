import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# -------- DATABASE -------- #
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8309802080",
    database="grocery_db"
)
cursor = db.cursor(buffered=True)

# -------- GLOBALS -------- #
cart = []

# -------- FUNCTIONS -------- #

def clear_table():
    for item in table.get_children():
        table.delete(item)


def add_product():
    name = entry_name.get()
    price = entry_price.get()
    qty = entry_qty.get()

    if name == "" or price == "" or qty == "":
        messagebox.showerror("Error", "Fill all fields")
        return

    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (%s,%s,%s)",
        (name, float(price), int(qty))
    )
    db.commit()

    messagebox.showinfo("Success", "Product Added")

    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_qty.delete(0, tk.END)


# -------- VIEW PRODUCTS -------- #

def view_products():
    clear_table()

    table["columns"] = ("Name", "Price", "Quantity")
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)
        table.column(col, width=150)

    cursor.execute("SELECT name, price, quantity FROM products")

    for row in cursor.fetchall():
        table.insert("", "end", values=row)


def delete_product():
    name = entry_name.get()
    cursor.execute("DELETE FROM products WHERE name=%s", (name,))
    db.commit()
    messagebox.showinfo("Deleted", "Product Deleted")


# -------- CART -------- #

def add_to_cart():
    name = entry_name.get()
    qty = entry_qty.get()

    if name == "" or qty == "":
        messagebox.showerror("Error", "Enter product & quantity")
        return

    qty = int(qty)

    cursor.execute("SELECT price, quantity FROM products WHERE name=%s", (name,))
    result = cursor.fetchone()

    if result:
        price, stock = result

        if qty > stock:
            messagebox.showerror("Error", "Not enough stock")
            return

        total = price * qty
        cart.append((name, price, qty, total))

        messagebox.showinfo("Added", f"{name} added to cart")
    else:
        messagebox.showerror("Error", "Product not found")


def view_cart():
    clear_table()

    table["columns"] = ("Name", "Price", "Qty", "Total")
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)

    for item in cart:
        table.insert("", "end", values=item)


# -------- BILLING + CUSTOMER -------- #

def generate_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    phone = entry_phone.get()

    if phone == "":
        messagebox.showerror("Error", "Enter phone number")
        return

    total_bill = 0

    for item in cart:
        name, price, qty, total = item
        total_bill += total

        cursor.execute(
            "UPDATE products SET quantity = quantity - %s WHERE name=%s",
            (qty, name)
        )

        cursor.execute(
            "INSERT INTO sales (name, quantity, total, date) VALUES (%s,%s,%s,NOW())",
            (name, qty, total)
        )

        cursor.execute(
            "INSERT INTO customers (phone, product, quantity, total) VALUES (%s,%s,%s,%s)",
            (phone, name, qty, total)
        )

    db.commit()

    messagebox.showinfo("Bill Generated", f"Total Bill = ₹{total_bill}")

    cart.clear()


# -------- SALES -------- #

def view_sales():
    clear_table()

    table["columns"] = ("Name", "Quantity", "Total", "Date")
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)

    cursor.execute("SELECT name, quantity, total, date FROM sales ORDER BY date DESC")

    for row in cursor.fetchall():
        table.insert("", "end", values=row)


# -------- CUSTOMER HISTORY -------- #

def view_customer_history():
    phone = entry_phone.get()

    if phone == "":
        messagebox.showerror("Error", "Enter phone number")
        return

    clear_table()

    table["columns"] = ("Product", "Qty", "Total", "Date")
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)

    cursor.execute(
        "SELECT product, quantity, total, date FROM customers WHERE phone=%s",
        (phone,)
    )

    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("Info", "No history found")

    for row in data:
        table.insert("", "end", values=row)


# -------- SEARCH -------- #

def search_product():
    name = entry_name.get()

    clear_table()

    table["columns"] = ("Name", "Price", "Quantity")
    table["show"] = "headings"

    for col in table["columns"]:
        table.heading(col, text=col)

    cursor.execute(
        "SELECT name, price, quantity FROM products WHERE name LIKE %s",
        ('%' + name + '%',)
    )

    for row in cursor.fetchall():
        table.insert("", "end", values=row)


# -------- LOW STOCK -------- #

def check_low_stock_auto():
    cursor.execute("SELECT name FROM products WHERE quantity < 5")
    items = cursor.fetchall()

    if items:
        names = [i[0] for i in items]
        messagebox.showwarning("Low Stock!", f"Low items: {', '.join(names)}")

    root.after(15000, check_low_stock_auto)


# -------- GUI -------- #

root = tk.Tk()
root.title("Grocery Management System")
root.geometry("900x600")

tk.Label(root, text="Grocery Management System",
         font=("Arial", 16, "bold"),
         bg="#2c3e50", fg="white").pack(fill="x")

frame = tk.Frame(root)
frame.pack(pady=10)

# Inputs
tk.Label(frame, text="Product Name").grid(row=0, column=0)
entry_name = tk.Entry(frame)
entry_name.grid(row=0, column=1)

tk.Label(frame, text="Price").grid(row=1, column=0)
entry_price = tk.Entry(frame)
entry_price.grid(row=1, column=1)

tk.Label(frame, text="Quantity").grid(row=2, column=0)
entry_qty = tk.Entry(frame)
entry_qty.grid(row=2, column=1)

tk.Label(frame, text="Phone Number").grid(row=3, column=0)
entry_phone = tk.Entry(frame)
entry_phone.grid(row=3, column=1)

# Buttons
btn_frame = tk.Frame(frame)
btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

w = 15

tk.Button(btn_frame, text="Add Product", width=w, command=add_product).grid(row=0, column=0)
tk.Button(btn_frame, text="View Products", width=w, command=view_products).grid(row=0, column=1)

tk.Button(btn_frame, text="Delete", width=w, command=delete_product).grid(row=1, column=0)
tk.Button(btn_frame, text="Add to Cart", width=w, command=add_to_cart).grid(row=1, column=1)

tk.Button(btn_frame, text="View Cart", width=w, command=view_cart).grid(row=2, column=0)
tk.Button(btn_frame, text="Generate Bill", width=w, command=generate_bill).grid(row=2, column=1)

tk.Button(btn_frame, text="Search", width=w, command=search_product).grid(row=3, column=0)
tk.Button(btn_frame, text="Sales Report", width=w, command=view_sales).grid(row=3, column=1)

tk.Button(btn_frame, text="Customer History", width=w,
          command=view_customer_history).grid(row=4, column=0)

# Table
table = ttk.Treeview(root)
table.pack(fill="both", expand=True)

# Style
style = ttk.Style()
style.configure("Treeview", rowheight=28, font=("Arial", 11))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

# Auto alert
check_low_stock_auto()

root.mainloop()