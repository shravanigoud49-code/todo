import tkinter as tk
from tkinter import messagebox, filedialog
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
image_path = ""

# -------- FUNCTIONS -------- #

def add_product():
    name = entry_name.get()
    price = entry_price.get()
    qty = entry_qty.get()

    if name == "" or price == "" or qty == "":
        messagebox.showerror("Error", "Fill all fields")
        return

    cursor.execute(
        "INSERT INTO products (name, price, quantity, image) VALUES (%s,%s,%s,%s)",
        (name, float(price), int(qty), image_path)
    )
    db.commit()

    messagebox.showinfo("Success", "Product Added")


def view_products():
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()

    text_area.delete("1.0", tk.END)

    if not data:
        text_area.insert(tk.END, "No products found\n")
        return

    text_area.insert(tk.END, "ID | Name | Price | Qty\n")
    text_area.insert(tk.END, "-"*40 + "\n")

    for row in data:
        text_area.insert(tk.END, f"{row[0]} | {row[1]} | ₹{row[2]} | {row[3]}\n")


def delete_product():
    name = entry_name.get()
    cursor.execute("DELETE FROM products WHERE name=%s", (name,))
    db.commit()
    messagebox.showinfo("Deleted", "Product Deleted")


# -------- CART SYSTEM -------- #

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


def generate_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty")
        return

    text_area.delete("1.0", tk.END)

    total_bill = 0

    text_area.insert(tk.END, "====== GROCERY BILL ======\n\n")

    for item in cart:
        name, price, qty, total = item

        text_area.insert(tk.END, f"{name} x{qty} = ₹{total}\n")
        total_bill += total

        cursor.execute("UPDATE products SET quantity = quantity - %s WHERE name=%s",
                       (qty, name))

        cursor.execute("INSERT INTO sales (name, quantity, total) VALUES (%s,%s,%s)",
                       (name, qty, total))

    db.commit()

    text_area.insert(tk.END, "\n----------------------\n")
    text_area.insert(tk.END, f"TOTAL = ₹{total_bill}\n")
    text_area.insert(tk.END, "======================\n")
    text_area.insert(tk.END, "Thank You! 😊")

    cart.clear()


def search_product():
    name = entry_name.get()

    cursor.execute("SELECT * FROM products WHERE name LIKE %s", ('%' + name + '%',))
    data = cursor.fetchall()

    text_area.delete("1.0", tk.END)

    if data:
        for row in data:
            text_area.insert(tk.END, f"{row}\n")
    else:
        text_area.insert(tk.END, "No product found\n")


def low_stock():
    cursor.execute("SELECT * FROM products WHERE quantity < 5")
    data = cursor.fetchall()

    text_area.delete("1.0", tk.END)

    if data:
        text_area.insert(tk.END, "⚠️ Low Stock:\n")
        for row in data:
            text_area.insert(tk.END, f"{row}\n")
    else:
        text_area.insert(tk.END, "All products sufficient\n")


def choose_image():
    global image_path

    file = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
    )

    if file:
        image_path = file
        messagebox.showinfo("Selected", "Image Selected")


# -------- GUI -------- #

root = tk.Tk()
root.title("Grocery Management System")
root.geometry("700x550")

tk.Label(root, text="Grocery Management System",
         font=("Arial", 16, "bold"),
         bg="#34495e", fg="white").pack(fill="x")

frame = tk.Frame(root)
frame.pack(pady=20)

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

# Buttons
btn_frame = tk.Frame(frame)
btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

w = 15

tk.Button(btn_frame, text="Add Product", width=w, command=add_product).grid(row=0, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="View Products", width=w, command=view_products).grid(row=0, column=1, padx=5, pady=5)

tk.Button(btn_frame, text="Delete Product", width=w, command=delete_product).grid(row=1, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Add to Cart", width=w, command=add_to_cart).grid(row=1, column=1, padx=5, pady=5)

tk.Button(btn_frame, text="Generate Bill", width=w, command=generate_bill).grid(row=2, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Search", width=w, command=search_product).grid(row=2, column=1, padx=5, pady=5)

tk.Button(btn_frame, text="Low Stock", width=w, command=low_stock).grid(row=3, column=0, padx=5, pady=5)

# Image
tk.Button(frame, text="Select Image", command=choose_image).grid(row=4, column=0, columnspan=2, pady=5)

# Output
text_area = tk.Text(root, height=15, width=80)
text_area.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, command=text_area.yview)
scrollbar.pack(side="right", fill="y")

text_area.config(yscrollcommand=scrollbar.set)

# RUN
root.mainloop()