import tkinter as tk
from tkinter import ttk, messagebox
from database import insert_customer

from logic import (
    setup_variables,
    filter_inventory,
    select_item,
    update_price,
    add_item,
    update_total,
    delete_item
)
from state import get_bill_items, clear_bill
from pdf_utils import save_bill_as_pdf

def create_gui(root):
    vars = setup_variables(root)

    root.title("eBilling System")
    root.geometry("800x700")

    # Themes
    light_theme = {
        "bg": "#f0f4f8", "fg": "#333",
        "button_bg": "#007acc", "button_fg": "white",
        "tree_heading_bg": "#007acc", "tree_heading_fg": "white",
    }
    dark_theme = {
        "bg": "#1e1e1e", "fg": "#f0f0f0",
        "button_bg": "#444", "button_fg": "#f0f0f0",
        "tree_heading_bg": "#2d2d2d", "tree_heading_fg": "#00d2ff",
    }
    current_theme = {"theme": light_theme}

    label_font = ("Arial", 12)
    entry_font = ("Arial", 12)
    button_font = ("Arial", 14, "bold")

    # Layout frames
    form_frame = tk.Frame(root)
    tree_frame = tk.Frame(root)
    button_frame = tk.Frame(root)

    form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    tree_frame.grid(row=1, column=0, sticky="nsew", padx=10)
    button_frame.grid(row=2, column=0, pady=10)

    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Variable traces
    vars["product_entry_var"].trace("w", lambda *args: filter_inventory(vars["product_entry_var"], vars["product_list_var"]))
    vars["price_type"].trace("w", lambda *args: update_price(vars["product_entry_var"].get(), vars["price_type"], vars["price_var"]))

    def styled_label(text, row):
        lbl = tk.Label(form_frame, text=text, font=label_font)
        lbl.grid(row=row, column=0, sticky="w", pady=5)
        return lbl

    def styled_entry(var, row):
        entry = ttk.Entry(form_frame, textvariable=var, font=entry_font, width=30)
        entry.grid(row=row, column=1, sticky="w", pady=5)
        return entry

    # Labels and Inputs
    labels = [
        styled_label("Customer Name:", 0),
        styled_label("Customer Mobile:", 1),
        styled_label("Product Name:", 2),
        styled_label("Price Type:", 4),
        styled_label("Price:", 5),
        styled_label("Quantity:", 6),
    ]
    styled_entry(vars["customer_name_var"], 0)
    styled_entry(vars["customer_mobile_var"], 1)
    styled_entry(vars["product_entry_var"], 2)

    # Product List
    product_listbox = tk.Listbox(form_frame, listvariable=vars["product_list_var"], height=5, font=entry_font, width=30)
    product_listbox.grid(row=3, column=1, sticky="w", pady=5)
    product_listbox.bind("<<ListboxSelect>>", lambda e: select_item(product_listbox, vars["product_entry_var"], vars["price_var"], vars["price_type"]))

    ttk.Combobox(form_frame, textvariable=vars["price_type"], values=["Retail", "Wholesale"], font=entry_font, width=28).grid(row=4, column=1, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=vars["price_var"], font=entry_font, width=30).grid(row=5, column=1, sticky="w", pady=5)
    tk.Spinbox(form_frame, from_=1, to=1000, textvariable=vars["quantity_var"], font=entry_font, width=28).grid(row=6, column=1, sticky="w", pady=5)

    # Treeview for bill
    columns = ("Name", "Price", "Quantity", "Total")
    style = ttk.Style()
    style.theme_use("default")
    bill_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
    for col in columns:
        bill_tree.heading(col, text=col)
        bill_tree.column(col, anchor="center", width=150)
    bill_tree.pack(fill="both", expand=True)

    # Total Label
    total_label = tk.Label(root, text="Total: 0.00", font=("Arial", 14, "bold"))
    total_label.grid(row=3, column=0, pady=(5, 20))

    def reset():
        for item in bill_tree.get_children():
            bill_tree.delete(item)
        for key in ["product_entry_var", "price_var", "customer_name_var", "customer_mobile_var"]:
            vars[key].set("")
        vars["quantity_var"].set("1")
        vars["price_type"].set("Retail")
        vars["product_list_var"].set([])
        clear_bill()
        update_total(total_label)

    def validate_and_save():
        name = vars["customer_name_var"].get().strip()
        mobile = vars["customer_mobile_var"].get().strip()
        items = get_bill_items()

        if not name or not mobile:
            messagebox.showwarning("Missing Info", "Please enter both customer name and mobile number.")
            return

        if not mobile.isdigit() or len(mobile) != 10:
            messagebox.showerror("Invalid Mobile", "Mobile number must be exactly 10 digits and numeric.")
            return

        if not items:
            messagebox.showinfo("No Items", "Please add at least one item to the bill before saving.")
            return
        
        insert_customer(name, mobile) #Adding customer details in DB after verification

        save_bill_as_pdf(vars, items, total_label, reset)

    def themed_button(text, command, col):
        btn = tk.Button(button_frame, text=text, font=button_font, width=18, command=command)
        btn.grid(row=0, column=col, padx=10)
        return btn

    buttons = [
        themed_button("Add Item to Bill", lambda: add_item(
            vars["product_entry_var"], vars["quantity_var"], vars["price_var"], bill_tree, total_label, vars["price_type"]
        ), 0),
        themed_button("Delete Selected Item", lambda: delete_item(bill_tree, total_label), 1),
        themed_button("Save Bill as PDF", validate_and_save, 2)
    ]

    def toggle_theme():
        current_theme["theme"] = dark_theme if current_theme["theme"] == light_theme else light_theme
        apply_theme()

    theme_toggle_btn = tk.Button(root, text="Switch Theme", font=("Arial", 12, "bold"), command=toggle_theme)
    theme_toggle_btn.grid(row=4, column=0, pady=(0, 20))

    def apply_theme():
        theme = current_theme["theme"]
        root.configure(bg=theme["bg"])
        form_frame.configure(bg=theme["bg"])
        tree_frame.configure(bg=theme["bg"])
        button_frame.configure(bg=theme["bg"])
        total_label.configure(bg=theme["bg"], fg=theme["fg"])
        theme_toggle_btn.configure(bg=theme["button_bg"], fg=theme["button_fg"])

        for lbl in labels:
            lbl.configure(bg=theme["bg"], fg=theme["fg"])

        product_listbox.configure(
            bg="white" if theme == light_theme else "#2b2b2b",
            fg=theme["fg"]
        )

        for btn in buttons:
            btn.configure(
                bg=theme["button_bg"],
                fg=theme["button_fg"],
                activebackground=theme["tree_heading_bg"]
            )

        style.configure("Treeview.Heading", font=("Arial", 12, "bold"),
                        background=theme["tree_heading_bg"],
                        foreground=theme["tree_heading_fg"])
        style.configure("Treeview", font=("Arial", 11),
                        background="white" if theme == light_theme else "#2e2e2e",
                        fieldbackground="white" if theme == light_theme else "#2e2e2e",
                        foreground=theme["fg"])

    apply_theme()
