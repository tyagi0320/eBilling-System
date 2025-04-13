import os
import csv
from fpdf import FPDF
from datetime import datetime
from data import update_stock, save_inventory
from state import calculate_total
from database import insert_bill
from database import insert_bill_details


def save_bill_record(bill_number, customer_name, total_amount, pdf_path):
    bill_records_file = "bill_records.csv"
    os.makedirs("bills", exist_ok=True)
    file_exists = os.path.isfile(bill_records_file)

    with open(bill_records_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Bill ID", "Customer", "Date", "Total Amount", "PDF Link"])
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([bill_number, customer_name, date_str, total_amount, f'=HYPERLINK("{pdf_path}", "View Bill")'])

def save_bill_as_pdf(vars, items, total_label, reset_func):
    try:
        customer_name = vars["customer_name_var"].get().strip()
        customer_mobile = vars.get("customer_mobile_var").get().strip() if vars.get("customer_mobile_var") else ""

        if not customer_name:
            total_label.config(text="Enter customer name.")
            return

        folder = "bills2025"
        os.makedirs(folder, exist_ok=True)
        bill_number = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        pdf_path = os.path.join(folder, f"{bill_number}.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="AGARWAL PRODUCTS", ln=True, align="L")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 8, txt="Wholesale & Retail Supplier", ln=True, align="L")
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 8, txt="2/58, Block-B, Shipra Sun City", ln=True, align="L")
        pdf.cell(200, 8, txt="Indirapuram, Ghaziabad-201014", ln=True, align="L")
        pdf.ln(5)

        pdf.set_font("Arial", '', 11)
        now_str = datetime.now().strftime('%d-%m-%Y %I:%M %p')
        pdf.cell(100, 8, f"Bill No: {bill_number}", ln=False)
        pdf.cell(0, 8, f"Date: {now_str}", ln=True)

        pdf.cell(100, 8, f"Customer: {customer_name}", ln=False)
        if customer_mobile:
            pdf.cell(0, 8, f"Mobile: {customer_mobile}", ln=True)
        else:
            pdf.ln(8)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(70, 10, "Item", border=1, align="C", fill=True)
        pdf.cell(30, 10, "Price", border=1, align="C", fill=True)
        pdf.cell(30, 10, "Quantity", border=1, align="C", fill=True)
        pdf.cell(40, 10, "Total", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", '', 11)
        for item in items:
            name, price, qty, total = item
            pdf.cell(70, 10, str(name), border=1, align="L")
            pdf.cell(30, 10, f"{price:.2f}", border=1, align="R")
            pdf.cell(30, 10, str(qty), border=1, align="C")
            pdf.cell(40, 10, f"{total:.2f}", border=1, align="R")
            pdf.ln()
            update_stock(name, qty)

        total_amount = calculate_total()

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_x(60)  
        pdf.cell(40, 10, "Grand Total:", border=1, align="C")
        pdf.cell(40, 10, f"{total_amount:.2f}", border=1, align="C")

        pdf.ln(15)
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 8, "Thank you for your purchase!", ln=True, align="C")
        pdf.cell(200, 8, "For queries, contact us at: 98765-43210", ln=True, align="C")

        pdf.output(pdf_path)
        save_inventory()
        save_bill_record(bill_number, customer_name, total_amount, pdf_path)

        

        bill_id = insert_bill(bill_number, customer_name, total_amount, pdf_path)#Adding bills in DB before generating bill's PDF
        if bill_id:
         insert_bill_details(bill_id) # Adds all the items of the bill in DB
        else:
         total_label.config(text="Error: Failed to insert bill into database.")
        return


        total_label.config(text=f"Bill saved: {pdf_path}")
        reset_func()

    except Exception as e:
        total_label.config(text=f"Error generating bill: {e}")
