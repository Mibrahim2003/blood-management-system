"""
Reports View

This module provides the views for generating and displaying reports in the GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import List, Dict, Any

from database.connection import get_connection
from database.repositories.donor_repo import DonorRepo
from database.repositories.blood_request_repo import BloodRequestRepo

class ReportsView(ttk.Frame):
    """Frame for reports generation and display"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="Reports", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Reports buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        # Buttons for different reports
        ttk.Button(buttons_frame, text="Donor Activity Report", 
                  command=self.generate_donor_activity_report).pack(pady=5, fill="x")
        
        ttk.Button(buttons_frame, text="Blood Type Inventory", 
                  command=self.generate_blood_type_inventory).pack(pady=5, fill="x")
        
        ttk.Button(buttons_frame, text="Blood Request Summary", 
                  command=self.generate_blood_request_summary).pack(pady=5, fill="x")
        
        ttk.Button(buttons_frame, text="Monthly Donation Statistics", 
                  command=self.generate_monthly_statistics).pack(pady=5, fill="x")
        
        # Report display area
        self.report_frame = ttk.LabelFrame(main_frame, text="Report Results")
        self.report_frame.pack(fill="both", expand=True, pady=10)
        
        # Default message
        ttk.Label(self.report_frame, text="Select a report to generate", 
                 font=("Arial", 12)).pack(pady=20)
    
    def clear_report_frame(self):
        """Clear the report display area"""
        for widget in self.report_frame.winfo_children():
            widget.destroy()
    
    def generate_donor_activity_report(self):
        """Generate a report on donor activity"""
        try:
            self.clear_report_frame()
            
            # Get timeframe for the report
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Last year
            
            # Create a top level window for date selection
            date_window = tk.Toplevel(self.parent)
            date_window.title("Select Report Timeframe")
            date_window.geometry("400x200")
            date_window.transient(self.parent)
            
            # Date selection form
            form_frame = ttk.Frame(date_window, padding=20)
            form_frame.pack(fill="both", expand=True)
            
            ttk.Label(form_frame, text="Select Report Timeframe", 
                    font=("Arial", 12, "bold")).pack(pady=(0, 20))
            
            # Start date
            start_frame = ttk.Frame(form_frame)
            start_frame.pack(fill="x", pady=5)
            ttk.Label(start_frame, text="Start Date (YYYY-MM-DD):").pack(side="left")
            
            start_var = tk.StringVar(value=start_date.strftime("%Y-%m-%d"))
            ttk.Entry(start_frame, textvariable=start_var).pack(side="left", padx=5, fill="x", expand=True)
            
            # End date
            end_frame = ttk.Frame(form_frame)
            end_frame.pack(fill="x", pady=5)
            ttk.Label(end_frame, text="End Date (YYYY-MM-DD):").pack(side="left")
            
            end_var = tk.StringVar(value=end_date.strftime("%Y-%m-%d"))
            ttk.Entry(end_frame, textvariable=end_var).pack(side="left", padx=5, fill="x", expand=True)
            
            # Button frame
            button_frame = ttk.Frame(form_frame)
            button_frame.pack(fill="x", pady=20)
            
            def generate_report():
                """Generate the report with selected dates"""
                try:
                    start_date_str = start_var.get()
                    end_date_str = end_var.get()
                    
                    connection = get_connection()
                    try:
                        with connection:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    SELECT 
                                        d.donor_id, 
                                        d.first_name, 
                                        d.last_name, 
                                        bt.type_name as blood_type,
                                        COUNT(bu.unit_id) as donation_count
                                    FROM 
                                        Donors d
                                    JOIN 
                                        Blood_Types bt ON d.blood_type_id = bt.blood_type_id
                                    LEFT JOIN 
                                        Blood_Units bu ON d.donor_id = bu.donor_id AND 
                                        bu.collection_date BETWEEN %s AND %s
                                    GROUP BY 
                                        d.donor_id, d.first_name, d.last_name, bt.type_name
                                    ORDER BY 
                                        donation_count DESC, d.last_name, d.first_name
                                """, (start_date_str, end_date_str))
                                
                                columns = [desc[0] for desc in cursor.description]
                                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    finally:
                        connection.close()
                    
                    date_window.destroy()
                    self.display_donor_activity_report(results, start_date_str, end_date_str)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
            ttk.Button(button_frame, text="Generate", command=generate_report).pack(side="right", padx=5)
            ttk.Button(button_frame, text="Cancel", command=date_window.destroy).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up report: {str(e)}")
    
    def display_donor_activity_report(self, results: List[Dict[str, Any]], 
                                   start_date: str, end_date: str):
        """Display donor activity report results"""
        self.clear_report_frame()
        
        # Report header
        ttk.Label(self.report_frame, text=f"Donor Activity Report ({start_date} to {end_date})", 
                font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create a treeview to display results
        columns = ("Donor ID", "Donor Name", "Blood Type", "Donations")
        report_tree = ttk.Treeview(self.report_frame, columns=columns, show="headings")
        
        for col in columns:
            report_tree.heading(col, text=col)
            width = 100 if col in ("Donor ID", "Blood Type", "Donations") else 200
            report_tree.column(col, width=width)
        
        report_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=report_tree.yview)
        scrollbar.pack(side="right", fill="y")
        report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Add data rows
        total_donations = 0
        for donor in results:
            donor_name = f"{donor['first_name']} {donor['last_name']}"
            donations = donor['donation_count']
            total_donations += donations
            
            report_tree.insert("", "end", values=(
                donor["donor_id"],
                donor_name,
                donor["blood_type"],
                donations
            ))
        
        # Add summary information
        summary_frame = ttk.Frame(self.report_frame)
        summary_frame.pack(fill="x", pady=10)
        
        ttk.Label(summary_frame, text=f"Total Donors: {len(results)}",  
                font=("Arial", 10, "bold")).pack(side="left", padx=20)
        
        ttk.Label(summary_frame, text=f"Total Donations: {total_donations}", 
                font=("Arial", 10, "bold")).pack(side="left", padx=20)
        
        # Add export button
        ttk.Button(self.report_frame, text="Export Report", 
                  command=lambda: self.export_report("donor_activity")).pack(pady=10)
    
    def generate_blood_type_inventory(self):
        """Generate a report on current blood type inventory"""
        try:
            self.clear_report_frame()
            
            connection = get_connection()
            try:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                bt.type_name,
                                COUNT(CASE WHEN bu.status = 'Available' THEN 1 END) as available_units,
                                COUNT(CASE WHEN bu.status = 'Used' THEN 1 END) as used_units,
                                COUNT(CASE WHEN bu.status = 'Expired' THEN 1 END) as expired_units,
                                COUNT(bu.unit_id) as total_units
                            FROM 
                                Blood_Types bt
                            LEFT JOIN 
                                Blood_Units bu ON bt.blood_type_id = bu.blood_type_id
                            GROUP BY 
                                bt.type_name
                            ORDER BY 
                                bt.type_name
                        """)
                        
                        columns = [desc[0] for desc in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            finally:
                connection.close()
            
            # Report header
            today = datetime.now().strftime("%Y-%m-%d")
            ttk.Label(self.report_frame, text=f"Blood Type Inventory Report (as of {today})", 
                    font=("Arial", 14, "bold")).pack(pady=(0, 10))
            
            # Create a treeview to display results
            columns = ("Blood Type", "Available Units", "Used Units", "Expired Units", "Total Units")
            report_tree = ttk.Treeview(self.report_frame, columns=columns, show="headings")
            
            for col in columns:
                report_tree.heading(col, text=col)
                report_tree.column(col, width=120)
            
            report_tree.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=report_tree.yview)
            scrollbar.pack(side="right", fill="y")
            report_tree.configure(yscrollcommand=scrollbar.set)
            
            # Add data rows
            total_available = 0
            total_used = 0
            total_expired = 0
            grand_total = 0
            
            for item in results:
                available = item['available_units'] or 0
                used = item['used_units'] or 0
                expired = item['expired_units'] or 0
                total = item['total_units'] or 0
                
                total_available += available
                total_used += used
                total_expired += expired
                grand_total += total
                
                report_tree.insert("", "end", values=(
                    item["type_name"],
                    available,
                    used,
                    expired,
                    total
                ))
            
            # Add a separator
            report_tree.insert("", "end", values=("", "", "", "", ""))
            
            # Add total row
            report_tree.insert("", "end", values=(
                "TOTAL",
                total_available,
                total_used,
                total_expired,
                grand_total
            ))
            
            # Add export button
            ttk.Button(self.report_frame, text="Export Report", 
                      command=lambda: self.export_report("blood_inventory")).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_blood_request_summary(self):
        """Generate a summary report of blood requests"""
        try:
            self.clear_report_frame()
            
            # Get timeframe for the report
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days by default
            
            # Create a top level window for date selection
            date_window = tk.Toplevel(self.parent)
            date_window.title("Select Report Timeframe")
            date_window.geometry("400x200")
            date_window.transient(self.parent)
            
            # Date selection form
            form_frame = ttk.Frame(date_window, padding=20)
            form_frame.pack(fill="both", expand=True)
            
            ttk.Label(form_frame, text="Select Report Timeframe", 
                    font=("Arial", 12, "bold")).pack(pady=(0, 20))
            
            # Start date
            start_frame = ttk.Frame(form_frame)
            start_frame.pack(fill="x", pady=5)
            ttk.Label(start_frame, text="Start Date (YYYY-MM-DD):").pack(side="left")
            
            start_var = tk.StringVar(value=start_date.strftime("%Y-%m-%d"))
            ttk.Entry(start_frame, textvariable=start_var).pack(side="left", padx=5, fill="x", expand=True)
            
            # End date
            end_frame = ttk.Frame(form_frame)
            end_frame.pack(fill="x", pady=5)
            ttk.Label(end_frame, text="End Date (YYYY-MM-DD):").pack(side="left")
            
            end_var = tk.StringVar(value=end_date.strftime("%Y-%m-%d"))
            ttk.Entry(end_frame, textvariable=end_var).pack(side="left", padx=5, fill="x", expand=True)
            
            # Button frame
            button_frame = ttk.Frame(form_frame)
            button_frame.pack(fill="x", pady=20)
            
            def generate_report():
                """Generate the report with selected dates"""
                try:
                    start_date_str = start_var.get()
                    end_date_str = end_var.get()
                    
                    connection = get_connection()
                    try:
                        with connection:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    SELECT 
                                        bt.type_name,
                                        br.priority,
                                        br.status,
                                        COUNT(br.request_id) as request_count,
                                        SUM(br.units_required) as total_units_required
                                    FROM 
                                        Blood_Requests br
                                    JOIN 
                                        Blood_Types bt ON br.blood_type_id = bt.blood_type_id
                                    WHERE 
                                        br.request_date BETWEEN %s AND %s
                                    GROUP BY 
                                        bt.type_name, br.priority, br.status
                                    ORDER BY 
                                        bt.type_name, br.priority
                                """, (start_date_str, end_date_str))
                                
                                columns = [desc[0] for desc in cursor.description]
                                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    finally:
                        connection.close()
                    
                    date_window.destroy()
                    self.display_blood_request_summary(results, start_date_str, end_date_str)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
            ttk.Button(button_frame, text="Generate", command=generate_report).pack(side="right", padx=5)
            ttk.Button(button_frame, text="Cancel", command=date_window.destroy).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up report: {str(e)}")
    
    def display_blood_request_summary(self, results: List[Dict[str, Any]], 
                                    start_date: str, end_date: str):
        """Display blood request summary report results"""
        self.clear_report_frame()
        
        # Report header
        ttk.Label(self.report_frame, text=f"Blood Request Summary ({start_date} to {end_date})", 
                font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create a treeview to display results
        columns = ("Blood Type", "Priority", "Status", "Request Count", "Units Required")
        report_tree = ttk.Treeview(self.report_frame, columns=columns, show="headings")
        
        for col in columns:
            report_tree.heading(col, text=col)
            width = 100 if col in ("Blood Type", "Priority", "Status") else 120
            report_tree.column(col, width=width)
        
        report_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=report_tree.yview)
        scrollbar.pack(side="right", fill="y")
        report_tree.configure(yscrollcommand=scrollbar.set)
        
        # Add data rows
        total_requests = 0
        total_units = 0
        
        for item in results:
            request_count = item['request_count'] or 0
            units_required = item['total_units_required'] or 0
            
            total_requests += request_count
            total_units += units_required
            
            report_tree.insert("", "end", values=(
                item["type_name"],
                item["priority"],
                item["status"],
                request_count,
                units_required
            ))
        
        # Add a separator
        report_tree.insert("", "end", values=("", "", "", "", ""))
        
        # Add total row
        report_tree.insert("", "end", values=(
            "TOTAL",
            "",
            "",
            total_requests,
            total_units
        ))
        
        # Add export button
        ttk.Button(self.report_frame, text="Export Report", 
                  command=lambda: self.export_report("blood_requests")).pack(pady=10)
    
    def generate_monthly_statistics(self):
        """Generate monthly donation statistics report"""
        try:
            self.clear_report_frame()
            
            # Get timeframe for the report - default to last 12 months
            end_date = datetime.now()
            start_date = datetime(end_date.year - 1, end_date.month, 1)
            
            connection = get_connection()
            try:
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                DATE_TRUNC('month', bu.collection_date) as month,
                                COUNT(bu.unit_id) as donation_count,
                                COUNT(DISTINCT bu.donor_id) as unique_donors
                            FROM 
                                Blood_Units bu
                            WHERE 
                                bu.collection_date BETWEEN %s AND %s
                            GROUP BY 
                                DATE_TRUNC('month', bu.collection_date)
                            ORDER BY 
                                month
                        """, (start_date, end_date))
                        
                        columns = [desc[0] for desc in cursor.description]
                        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            finally:
                connection.close()
            
            # Report header
            ttk.Label(self.report_frame, text=f"Monthly Donation Statistics ({start_date.strftime('%b %Y')} to {end_date.strftime('%b %Y')})", 
                    font=("Arial", 14, "bold")).pack(pady=(0, 10))
            
            # Create a treeview to display results
            columns = ("Month", "Number of Donations", "Unique Donors")
            report_tree = ttk.Treeview(self.report_frame, columns=columns, show="headings")
            
            for col in columns:
                report_tree.heading(col, text=col)
                width = 200 if col == "Month" else 150
                report_tree.column(col, width=width)
            
            report_tree.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.report_frame, orient="vertical", command=report_tree.yview)
            scrollbar.pack(side="right", fill="y")
            report_tree.configure(yscrollcommand=scrollbar.set)
            
            # Add data rows
            total_donations = 0
            max_unique_donors = 0
            
            for item in results:
                month_str = item['month'].strftime("%B %Y")
                donations = item['donation_count'] or 0
                unique_donors = item['unique_donors'] or 0
                
                total_donations += donations
                max_unique_donors = max(max_unique_donors, unique_donors)
                
                report_tree.insert("", "end", values=(
                    month_str,
                    donations,
                    unique_donors
                ))
            
            # Add a separator
            report_tree.insert("", "end", values=("", "", ""))
            
            # Add total row
            report_tree.insert("", "end", values=(
                "TOTAL",
                total_donations,
                f"Max: {max_unique_donors}"
            ))
            
            # Add export button
            ttk.Button(self.report_frame, text="Export Report", 
                      command=lambda: self.export_report("monthly_statistics")).pack(pady=10)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def export_report(self, report_type: str):
        """Export the current report to a CSV file"""
        try:
            import csv
            from tkinter import filedialog
            import os
            
            # Get the date for filename
            today = datetime.now().strftime("%Y%m%d")
            default_filename = f"{report_type}_{today}.csv"
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=default_filename,
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Find the treeview in the report frame
            for widget in self.report_frame.winfo_children():
                if isinstance(widget, ttk.Treeview):
                    tree = widget
                    break
            else:
                messagebox.showerror("Error", "No report data found to export")
                return
            
            # Get the headers
            headers = [tree.heading(col)["text"] for col in tree["columns"]]
            
            # Get the data
            data = []
            for item_id in tree.get_children():
                values = tree.item(item_id, "values")
                if values and any(values):  # Skip empty rows
                    data.append(values)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            
            messagebox.showinfo("Export Successful", 
                              f"Report exported successfully to {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
