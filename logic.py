import tkinter as tk
from data import get_inventory, update_stock, save_inventory
from state import add_to_bill, remove_from_bill, get_bill_items, calculate_total, clear_bill

inventory_data = get_inventory()

def setup_variables(root):
    return {
        "customer_name_var": tk.StringVar(root),
        "customer_mobile_var": tk.StringVar(root),
        "product_entry_var": tk.StringVar(root),
        "quantity_var": tk.StringVar(root, value="1"),
        "price_type": tk.StringVar(root, value="Retail"),
        "price_var": tk.StringVar(root),
        "product_list_var": tk.StringVar(root, value=inventory_data["Name"].tolist()),
    }

def filter_inventory(product_entry_var, product_list_var):
    search = product_entry_var.get().lower()
    filtered = inventory_data[inventory_data["Name"].str.lower().str.contains(search)] if search else inventory_data
    product_list_var.set(filtered["Name"].tolist())

def select_item(product_listbox, product_entry_var, price_var, price_type):
    selected = product_listbox.curselection()
    if selected:
        name = product_listbox.get(selected)
        product_entry_var.set(name)
        update_price(name, price_type, price_var)

def update_price(name, price_type, price_var):
    item = inventory_data[inventory_data["Name"] == name]
    if not item.empty:
        price = item.iloc[0]["Retail Price"] if price_type.get() == "Retail" else item.iloc[0]["Wholesale Price"]
        price_var.set(f"{price:.2f}")

def find_existing_item(bill_tree, name):
    for item_id in bill_tree.get_children():
        values = bill_tree.item(item_id, "values")
        if values[0] == name:
            return item_id, values
    return None, None

def add_item(product_entry_var, quantity_var, price_var, bill_tree, total_label, price_type_var):
    try:
        name = product_entry_var.get().strip()
        if not name:
            total_label.config(text="❗ Enter a product name.")
            return

        price = float(price_var.get())
        quantity = int(quantity_var.get())

        item = inventory_data[inventory_data["Name"] == name]
        if item.empty:
            total_label.config(text="❌ Item not found in inventory.")
            return

        available_qty = item.iloc[0]["Quantity"]
        if quantity > available_qty:
            total_label.config(text=f"⚠️ Only {available_qty} in stock.")
            return

        if price_type_var.get() == "Wholesale" and quantity < 25:
            total_label.config(text="⚠️ Minimum 25 items for wholesale price.")
            return

        total = price * quantity

        # Check for duplicates
        existing_id, existing_values = find_existing_item(bill_tree, name)
        if existing_id:
            # Update quantity and total
            existing_qty = int(existing_values[2])
            new_qty = existing_qty + quantity
            new_total = float(price) * new_qty
            bill_tree.item(existing_id, values=(name, f"{price:.2f}", new_qty, f"{new_total:.2f}"))

            # Update state
            remove_from_bill((name, float(existing_values[1]), existing_qty, float(existing_values[3])))
            add_to_bill((name, price, new_qty, new_total))
        else:
            bill_tree.insert("", "end", values=(name, f"{price:.2f}", quantity, f"{total:.2f}"))
            add_to_bill((name, price, quantity, total))

        update_total(total_label)

    except ValueError:
        total_label.config(text="❗ Invalid quantity or price.")
    except Exception as e:
        total_label.config(text=f"Error: {e}")

def update_total(total_label):
    total_amount = calculate_total()
    total_label.config(text=f"Total: {total_amount:.2f}")

def delete_item(bill_tree, total_label):
    try:
        for item in bill_tree.selection():
            values = bill_tree.item(item, "values")
            remove_from_bill((values[0], float(values[1]), int(values[2]), float(values[3])))
            bill_tree.delete(item)
        update_total(total_label)
    except Exception as e:
        total_label.config(text=f"Error: {e}")
