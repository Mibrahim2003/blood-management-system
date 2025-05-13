# Main application launcher for the Blood Donation System
# This script properly initializes all modules and launches the complete application

import os
import sys
import tkinter as tk
from tkinter import messagebox
import argparse

def launch_application():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Blood Donation Management System")
    parser.add_argument('--run-db-fixes', action='store_true', help='Run full database fixes')
    parser.add_argument('--generate-test-data', action='store_true', help='Generate test blood units')
    parser.add_argument('--test-units', type=int, default=50, help='Number of test blood units to generate (default: 50)')
    args = parser.parse_args()
    
    try:
        # Set up proper Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Test database connection
        from src.database.connection import get_connection
        print("Testing database connection...")
        connection = get_connection()
        if connection:
            print("Database connection successful")
            connection.close()
        else:
            print("Failed to connect to database")
            messagebox.showerror("Database Error", "Failed to connect to the database")
            return
        
        # Run database fixes if requested or by default
        if args.run_db_fixes:
            from src.utils.fix_database import fix_all_database_tables
            print("Running comprehensive database fixes...")
            fix_all_database_tables()
        else:
            # Just run the blood_requests fix by default
            from src.utils.fix_database import fix_blood_requests_table
            print("Running basic database fixes...")
            fix_blood_requests_table()
              # Initialize the database tables if needed
        from src.utils.initialize_db import initialize_database
        initialize_database()
        
        # Generate test data if requested
        if args.generate_test_data:
            from src.utils.generate_test_data import generate_test_blood_units
            print(f"Generating {args.test_units} test blood units...")
            success = generate_test_blood_units(args.test_units)
            if success:
                print("Test data generation complete!")
                # Prompt user to continue
                if not messagebox.askyesno("Test Data Generated", 
                                         f"Successfully generated {args.test_units} test blood units.\n\nDo you want to launch the application now?"):
                    print("Exiting after test data generation.")
                    return
            else:
                print("Failed to generate test data.")
                if not messagebox.askyesno("Test Data Error", 
                                         "Failed to generate test data.\n\nDo you want to continue launching the application?"):
                    print("Exiting after test data error.")
                    return
        
        # Import the main application
        from src.app import BloodDonationApp
        
        # Launch the application
        print("Starting Blood Donation System...")
        root = tk.Tk()
        app = BloodDonationApp(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch application: {str(e)}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_application()
