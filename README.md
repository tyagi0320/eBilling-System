# eBilling System – Inventory & Billing Management

A full-featured, desktop-based inventory and billing system built using **Python**, **MySQL**, and **FPDF**. Designed to manage inventory, handle customers, and generate professional PDF invoices for retail or wholesale businesses.

---

## Features

- 📦 Add and manage inventory using CSV
- 👥 Add new customers (with duplicate prevention)
- 🧾 Generate printable PDF bills with itemized details
- 💾 Store all transactions in a MySQL database
- 🧮 Automatically update inventory upon billing
- 📊 Inventory turnover analysis
- 🥇 Identify top customers by purchase volume
- 📁 Save all bills and records in organized folders
- ✅ Simple, modular, and expandable codebase

---

## Tech Stack

| Layer        | Technology         |
|--------------|--------------------|
| GUI          | `Tkinter` (Python GUI) |
| Backend      | `Python`           |
| Database     | `MySQL`            |
| Reporting    | `FPDF`, `CSV`      |
| Analytics    | SQL queries        |

---

## Folder Structure

```bash
📁 ebilling-system/
├── main.py                # Main GUI entry point
├── database.py            # Handles MySQL connections & DB operations
├── pdf_utils.py           # PDF bill generation logic
├── data.py                # Inventory update & saving
├── state.py               # App-wide shared state (cart, items)
├── bill_records.csv       # Stores bill history
├── bills/                 # Folder for generated bills
├── inventory.csv          # Sample inventory import
├── README.md              # This file
```

---

## Database Schema

### Create Database

```sql
CREATE DATABASE ebilling_system;
USE ebilling_system;
```

### Tables

```sql
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(15),
    CONSTRAINT unique_customer UNIQUE (customer_name, mobile_number)
);

CREATE TABLE inventory (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100),
    retail_price DECIMAL(10,2),
    wholesale_price DECIMAL(10,2),
    quantity INT
);

CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    bill_number VARCHAR(50),
    total_amount DECIMAL(10,2),
    date DATETIME,
    pdf_path VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE bill_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    total DECIMAL(10,2),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (product_id) REFERENCES inventory(product_id)
);
```

---

## How to Run

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ebilling-system.git
cd ebilling-system
```

### 2. Install Dependencies

```bash
pip install mysql-connector-python fpdf
```

### 3. Configure MySQL

- Make sure MySQL is running.
- Update the credentials in `database.py` if needed:
  ```python
  mysql.connector.connect(
      host="localhost",
      user="root",
      password="mysql",
      database="ebilling_system"
  )
  ```

### 4. Run the App

```bash
python main.py
```

---

## Bonus Features

### Top Customers by Spend

```sql
SELECT c.customer_name, SUM(b.total_amount) AS total_spent
FROM customers c
JOIN bills b ON c.customer_id = b.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 5;
```

### Inventory Turnover Ratio

```sql
SELECT 
    i.product_name,
    SUM(bd.quantity) AS total_sold,
    i.quantity AS current_stock,
    ROUND(SUM(bd.quantity) / (i.quantity + SUM(bd.quantity)), 2) AS turnover_ratio
FROM bill_details bd
JOIN inventory i ON bd.product_id = i.product_id
GROUP BY i.product_id;
```

You can automate these as **buttons** in the GUI for real-time insights.

---

## Future Enhancements

- Login/role-based access
- Graphical dashboards for sales trends
- Export reports to Excel/CSV
- Cloud sync for backups
- Barcode scanner integration

---

## Author

📧 Email: tharshit03@gmail.com  
🔗 GitHub: [@tyagi0320](https://github.com/tyagi0320)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
