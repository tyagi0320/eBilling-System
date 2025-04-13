import csv
import mysql.connector
from state import get_bill_items

def create_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",  
            user="root",       
            password="mysql", 
            database="ebilling_system"  
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def insert_inventory_from_csv(csv_file_path):
    """Insert inventory data from a CSV file into the inventory table."""
    connection = create_connection()
    cursor = connection.cursor()

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            # Extract values from each row (skip Item ID as it's auto-generated)
            product_name = row[1]  
            quantity = int(row[2])  
            retail_price = float(row[3])  
            wholesale_price = float(row[4])  
            query = "INSERT INTO inventory (product_name, retail_price, wholesale_price, quantity) VALUES (%s, %s, %s, %s)"
            values = (product_name, retail_price, wholesale_price, quantity)

            try:
                cursor.execute(query, values)
                connection.commit()
                print(f"Product {product_name} added successfully")
            except mysql.connector.Error as err:
                print(f"Error: {err}")

    cursor.close()
    connection.close()

def insert_customer(customer_name, mobile_number):
    """Insert customer data into the 'customers' table only if it doesn't exist."""
    connection = create_connection()
    cursor = connection.cursor()

    # Check if the customer already exists
    check_query = """
        SELECT customer_id FROM customers
        WHERE customer_name = %s AND mobile_number = %s;
    """
    cursor.execute(check_query, (customer_name, mobile_number))
    existing = cursor.fetchone()

    if existing:
        print(f"Customer '{customer_name}' already exists with ID {existing[0]}")
    else:
        try:
            insert_query = """
                INSERT INTO customers (customer_name, mobile_number)
                VALUES (%s, %s);
            """
            cursor.execute(insert_query, (customer_name, mobile_number))
            connection.commit()
            print(f"Customer '{customer_name}' added successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    cursor.close()
    connection.close()


def insert_bill(bill_number, customer_name, total_amount, pdf_path):
    """Insert a bill record into the 'bills' table and return its bill_id."""
    connection = create_connection()
    cursor = connection.cursor()

    # Get the customer ID from the database
    cursor.execute("SELECT customer_id FROM customers WHERE customer_name = %s", (customer_name,))
    customer_id_result = cursor.fetchone()

    if customer_id_result:
        customer_id = customer_id_result[0]

        cursor.nextset()  # Just in case previous query has leftover result sets

        query = """
            INSERT INTO bills (customer_id, bill_number, total_amount, date, pdf_path)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s);
        """
        values = (customer_id, bill_number, total_amount, pdf_path)

        try:
            cursor.execute(query, values)
            connection.commit()
            bill_id = cursor.lastrowid  # 👈 This is what you need
            print(f"✅ Bill {bill_number} inserted with ID {bill_id}.")
            return bill_id  # ✅ RETURN it
        except mysql.connector.Error as err:
            print(f"❌ Error inserting bill: {err}")
        finally:
            cursor.close()
            connection.close()
    else:
        print(f"⚠️ Customer {customer_name} not found.")
        cursor.close()
        connection.close()
        return None



def insert_bill_details(bill_id):
    """Insert detailed bill items into the 'bill_details' table."""
    connection = create_connection()
    cursor = connection.cursor()

    bill_items = get_bill_items()  # List of tuples: (name, price, qty, total)

    for item in bill_items:
        product_name, price, quantity, total = item

        # Get product_id from inventory
        cursor.execute("SELECT product_id FROM inventory WHERE product_name = %s", (product_name,))
        result = cursor.fetchone()

        if result:
            product_id = result[0]
            try:
                query = """
                    INSERT INTO bill_details (bill_id, product_id, quantity, price, total)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (bill_id, product_id, quantity, price, total)
                cursor.execute(query, values)
                print(f"✅ Inserted '{product_name}' x{quantity} into bill_details.")
            except mysql.connector.Error as err:
                print(f"❌ Error inserting {product_name} into bill_details: {err}")
        else:
            print(f"⚠️ Product '{product_name}' not found in inventory.")

    connection.commit()
    cursor.close()
    connection.close()
