import tkinter as tk
from gui import create_gui
from database import create_connection

# Establish MySQL connection
connection = create_connection()

if __name__ == "__main__":
    # Create the main window for the billing system
    root = tk.Tk()
    root.title("Billing System")
    root.geometry("600x800")
    
    # Create the GUI and pass the necessary variables to it
    create_gui(root)
    
    # Start the Tkinter event loop to keep the application running
    root.mainloop()
