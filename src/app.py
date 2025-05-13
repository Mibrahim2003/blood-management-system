import tkinter as tk
from tkinter import ttk, messagebox
import sys # Added import for sys.exit
from database.connection import test_connection
from views.donor_views import DonorManagementFrame
from views.receiver_views import ReceiverManagementFrame
from views.blood_request_views import BloodRequestManagementFrame

class BloodDonationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blood Donation Management System")
        self.root.geometry("1200x800")
        self.setup_ui()
        
    def setup_ui(self):
        # Main header
        header_frame = tk.Frame(self.root, pady=10)
        header_frame.pack(fill="x")
        
        header_label = tk.Label(header_frame, text="Blood Donation Management System", 
                               font=("Arial", 24, "bold"))
        header_label.pack()
        
        # Test connection button
        test_btn = tk.Button(header_frame, text="Test Database Connection", 
                           command=self.test_db_connection)
        test_btn.pack(pady=5)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self.donors_tab = ttk.Frame(self.notebook)
        self.receivers_tab = ttk.Frame(self.notebook)
        self.blood_requests_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.donors_tab, text="Donors")
        self.notebook.add(self.receivers_tab, text="Receivers")
        self.notebook.add(self.blood_requests_tab, text="Blood Requests")
        
        # Set up individual tabs
        self.donor_management = DonorManagementFrame(self.donors_tab)
        self.setup_receivers_tab()
        self.setup_blood_requests_tab()
        
    def setup_receivers_tab(self):
        self.receiver_management = ReceiverManagementFrame(self.receivers_tab)
        
    def setup_blood_requests_tab(self):
        # Import blood request views and create the management frame
        
        # Run database fixes first
        from utils.fix_database import fix_blood_requests_table
        from utils.fix_blood_units import create_blood_units_table
        fix_blood_requests_table()
        create_blood_units_table()
        
        # Create a label to confirm the tab is active
        info_frame = tk.Frame(self.blood_requests_tab, pady=5)
        info_frame.pack(fill="x")
        
        info_label = tk.Label(info_frame, text="Blood Request Management", font=("Arial", 14, "bold"))
        info_label.pack(pady=(0, 10))
        
        # Initialize the blood request management frame
        try:
            self.request_management = BloodRequestManagementFrame(self.blood_requests_tab)
        except Exception as e:
            error_msg = f"Failed to load Blood Request Management: {str(e)}"
            error_label = tk.Label(self.blood_requests_tab, text=error_msg, fg="red")
            error_label.pack(pady=20)
            messagebox.showerror("Error", error_msg)
    
    def test_db_connection(self):
        if test_connection():
            messagebox.showinfo("Connection Test", "Database connection successful!")
        else:
            messagebox.showerror("Connection Test", "Failed to connect to database!")

def main():
    try:
        # Test database connection first
        from database.connection import get_connection
        connection = get_connection()
        if connection:
            print("Database connection successful")
            connection.close()
            
            # Initialize the database tables
            from utils.initialize_db import initialize_database
            initialize_database()
            
            # Fix database tables if needed
            from utils.fix_database import fix_blood_requests_table
            from utils.fix_blood_units import create_blood_units_table
            fix_blood_requests_table()
            create_blood_units_table()
        
        # Start the application
        root = tk.Tk()
        app = BloodDonationApp(root)
        root.mainloop()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showerror("Critical Error", f"Failed to start application: {str(e)}")
        sys.exit(1) # sys is now defined

if __name__ == "__main__":
    main()
