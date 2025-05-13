import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
from database.repositories.blood_request_repo import BloodRequestRepo
from database.repositories.receiver_repo import ReceiverRepository
from utils.validation_utils import is_valid_integer

class BloodRequestManagementFrame:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        try:
            # Run database fixes before initialization
            from utils.fix_database import fix_blood_requests_table
            fix_blood_requests_table()
            
            # Initialize repositories with proper error handling
            self.request_repo = BloodRequestRepo()
            self.receiver_repo = ReceiverRepository()
            from database.repositories.blood_unit_repo import BloodUnitRepository
            self.blood_unit_repo = BloodUnitRepository()
            self.selected_request_id = None
            self.setup_ui()
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_message = f"Failed to initialize Blood Request Management: {str(e)}"
            error_label = tk.Label(parent_frame, text=error_message, fg="red", wraplength=600)
            error_label.pack(pady=20)
            
            # Add a retry button
            retry_button = tk.Button(parent_frame, text="Retry", command=self.retry_initialization)
            retry_button.pack(pady=10)
    
    def retry_initialization(self):
        # Clear the parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Try to reinitialize
        try:
            self.request_repo = BloodRequestRepo()
            self.receiver_repo = ReceiverRepository()
            self.selected_request_id = None
            self.setup_ui()
        except Exception as e:
            error_message = f"Retry failed: {str(e)}"
            error_label = tk.Label(self.parent, text=error_message, fg="red", wraplength=600)
            error_label.pack(pady=20)
        
    def setup_ui(self):
        # Clear the parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # Create a frame for request management with left and right panels
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (request list)
        left_frame = ttk.LabelFrame(main_frame, text="Blood Request List")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.search_requests)
        
        # Filter by status
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter by status:").pack(side="left")
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                   values=["All", "Pending", "Processing", "Fulfilled", "Cancelled"])
        status_combo.pack(side="left", padx=5)
        status_combo.bind("<<ComboboxSelected>>", self.filter_by_status)
        
        # Requests list
        columns = ("ID", "Receiver", "Blood Type", "Units Required", "Status", "Priority", "Date")
        self.request_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.request_tree.heading(col, text=col)
            width = 70 if col == "ID" else 100
            if col == "Receiver":
                width = 150
            self.request_tree.column(col, width=width)
            
        self.request_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.request_tree.bind("<<TreeviewSelect>>", self.on_request_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.request_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.request_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="New Request", command=self.show_add_request_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_requests).pack(side="left", padx=5)
        
        # Right panel (request details)
        self.right_frame = ttk.LabelFrame(main_frame, text="Request Details")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Load requests from database
        self.load_requests()
    
    def load_requests(self):
        # Clear the tree
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        # Get requests from repository
        try:
            status = None if self.status_var.get() == "All" else self.status_var.get()
            requests = BloodRequestRepo.get_all_requests(status)
            
            for request in requests:
                # Format the date
                request_date = request["request_date"].strftime('%Y-%m-%d') if request["request_date"] else "N/A"
                
                self.request_tree.insert("", "end", values=(
                    request["request_id"],
                    request["receiver_name"],
                    request["blood_type"],
                    f"{request['units_required']}",
                    request["status"],
                    request["priority"],
                    request_date
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requests: {e}")
    
    def search_requests(self, event=None):
        search_term = self.search_var.get().lower()
        
        # Clear the tree
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        # Get requests from repository
        try:
            if search_term:
                requests = BloodRequestRepo.search_requests(search_term)
            else:
                status = None if self.status_var.get() == "All" else self.status_var.get()
                requests = BloodRequestRepo.get_all_requests(status)
            
            for request in requests:
                # Format the date
                request_date = request["request_date"].strftime('%Y-%m-%d') if request["request_date"] else "N/A"
                
                self.request_tree.insert("", "end", values=(
                    request["request_id"],
                    request["receiver_name"],
                    request["blood_type"],
                    f"{request['units_required']}",
                    request["status"],
                    request["priority"],
                    request_date
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search requests: {e}")
    
    def filter_by_status(self, event=None):
        self.load_requests()
    
    def on_request_select(self, event=None):
        # Get selected item
        selected_items = self.request_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        request_id = self.request_tree.item(item, "values")[0]
        self.selected_request_id = int(request_id)
        self.display_request_details(self.selected_request_id)
    
    def display_request_details(self, request_id):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get request details
            request = BloodRequestRepo.get_request_by_id(request_id)
            if not request:
                return
                
            # Debug information about the request
            print(f"Request ID: {request_id}")
            print(f"Status: {request.get('status', 'Unknown')}")
            print(f"Units Required: {request.get('units_required', 0)}")
            print(f"Units Fulfilled: {request.get('units_fulfilled', 0)}")
            print(f"Units Assigned: {request.get('units_assigned', 0)}")
            
            # Request information section
            info_frame = ttk.LabelFrame(self.right_frame, text="Request Information")
            info_frame.pack(fill="x", expand=False, padx=10, pady=5)
            
            # Create a grid for the details
            ttk.Label(info_frame, text="Request ID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=str(request["request_id"])).grid(row=0, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Receiver:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=request["receiver_name"]).grid(row=1, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Blood Type:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=request["blood_type"]).grid(row=2, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Units Required:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=str(request["units_required"])).grid(row=3, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Units Fulfilled:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
            units_fulfilled = request.get("units_fulfilled", request.get("units_assigned", 0))
            ttk.Label(info_frame, text=f"{units_fulfilled} / {request['units_required']}").grid(row=4, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Request Date:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
            date_str = request["request_date"].strftime('%Y-%m-%d %H:%M') if request["request_date"] else "N/A"
            ttk.Label(info_frame, text=date_str).grid(row=5, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Priority:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=request["priority"]).grid(row=6, column=1, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text="Status:").grid(row=7, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=request["status"]).grid(row=7, column=1, sticky="w", padx=5, pady=2)
            
            if request["notes"]:
                ttk.Label(info_frame, text="Notes:").grid(row=8, column=0, sticky="nw", padx=5, pady=2)
                notes_text = tk.Text(info_frame, height=3, width=30, wrap=tk.WORD)
                notes_text.grid(row=8, column=1, sticky="w", padx=5, pady=2)
                notes_text.insert(tk.END, request["notes"])
                notes_text.config(state="disabled")
            
            # Actions section
            actions_frame = ttk.LabelFrame(self.right_frame, text="Actions")
            actions_frame.pack(fill="x", expand=False, padx=10, pady=5)
            
            # Action buttons
            if request["status"] == "Pending":
                ttk.Button(actions_frame, text="Process Request", 
                          command=lambda: self.update_request_status("Processing")
                         ).pack(side="left", padx=5, pady=5)
            
            if request["status"] in ["Pending", "Processing"]:
                ttk.Button(actions_frame, text="Cancel Request", 
                          command=lambda: self.update_request_status("Cancelled")
                         ).pack(side="left", padx=5, pady=5)
                
                # Add the "Assign Blood" button for Pending or Processing requests
                ttk.Button(actions_frame, text="Assign Blood", 
                          command=lambda: self.assign_blood_to_request(request)
                         ).pack(side="left", padx=5, pady=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display request details: {e}")
    
    def show_add_request_form(self):
        # Create a top level window for the form
        add_window = tk.Toplevel(self.parent)
        add_window.title("Create New Blood Request")
        add_window.geometry("500x500")
        add_window.transient(self.parent)
        add_window.grab_set()
        
        # Create a form frame
        form_frame = ttk.Frame(add_window, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        # Form fields
        ttk.Label(form_frame, text="Select Receiver:").grid(row=0, column=0, sticky="w", pady=10)
        
        # Receiver selection combobox
        receiver_frame = ttk.Frame(form_frame)
        receiver_frame.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Get all receivers
        receivers = self.receiver_repo.get_all_receivers()
        receiver_list = []
        receiver_map = {}
        for receiver in receivers:
            display_name = f"{receiver['first_name']} {receiver['last_name']} ({receiver['receiver_id']})"
            receiver_list.append(display_name)
            receiver_map[display_name] = receiver
        
        self.selected_receiver_var = tk.StringVar()
        receiver_combo = ttk.Combobox(receiver_frame, textvariable=self.selected_receiver_var, width=30)
        receiver_combo['values'] = receiver_list
        receiver_combo.pack(side="left", fill="x", expand=True)
        
        # Blood type information will be automatically determined based on receiver
        
        ttk.Label(form_frame, text="Blood Type:").grid(row=1, column=0, sticky="w", pady=10)
        self.blood_type_label = ttk.Label(form_frame, text="")
        self.blood_type_label.grid(row=1, column=1, sticky="w", pady=10)
        
        # Update blood type when receiver is selected
        def on_receiver_select(event=None):
            selected = self.selected_receiver_var.get()
            if selected and selected in receiver_map:
                receiver = receiver_map[selected]
                blood_type = receiver.get('blood_type', '')
                if not blood_type:
                    blood_type_id = receiver.get('blood_type_id', 0)
                    blood_type_map = {1: 'A+', 2: 'A-', 3: 'B+', 4: 'B-', 
                                     5: 'AB+', 6: 'AB-', 7: 'O+', 8: 'O-'}
                    blood_type = blood_type_map.get(blood_type_id, 'Unknown')
                self.blood_type_label.config(text=blood_type)
                
        receiver_combo.bind("<<ComboboxSelected>>", on_receiver_select)
        
        # Units required
        ttk.Label(form_frame, text="Units Required:").grid(row=2, column=0, sticky="w", pady=10)
        self.units_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.units_var, width=10).grid(row=2, column=1, sticky="w", pady=10)
        
        # Priority
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky="w", pady=10)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var, width=15)
        priority_combo['values'] = ["Low", "Medium", "High", "Urgent"]
        priority_combo.grid(row=3, column=1, sticky="w", pady=10)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=4, column=0, sticky="nw", pady=10)
        self.notes_text = tk.Text(form_frame, height=5, width=30)
        self.notes_text.grid(row=4, column=1, sticky="w", pady=10)
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Create Request", command=lambda: self.create_request(add_window)).pack(side="left", padx=10)
        ttk.Button(buttons_frame, text="Cancel", command=add_window.destroy).pack(side="left")
    
    def create_request(self, window):
        # Get form values
        selected_receiver = self.selected_receiver_var.get()
        units_required = self.units_var.get()
        priority = self.priority_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Validate
        if not selected_receiver:
            messagebox.showerror("Validation Error", "Please select a receiver")
            return
        
        if not is_valid_integer(units_required) or int(units_required) <= 0:
            messagebox.showerror("Validation Error", "Units required must be a positive number")
            return
        
        try:
            # Extract receiver ID from the selected string
            receiver_id = int(selected_receiver.split('(')[-1].replace(')', ''))
            
            # Get receiver details to find blood type ID
            receiver = self.receiver_repo.get_receiver_by_id(receiver_id)
            blood_type_id = receiver["blood_type_id"]
            
            # Create request
            request_id = BloodRequestRepo.create_request(
                receiver_id=receiver_id,
                blood_type_id=blood_type_id,
                units_required=int(units_required),
                priority=priority,
                notes=notes
            )
            
            # Close the window and refresh the list
            window.destroy()
            messagebox.showinfo("Success", f"Blood request #{request_id} created successfully")
            self.load_requests()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create request: {e}")
    
    def update_request_status(self, new_status):
        if not self.selected_request_id:
            return
        
        try:
            BloodRequestRepo.update_request_status(self.selected_request_id, new_status)
            messagebox.showinfo("Success", f"Request status updated to {new_status}")
            self.load_requests()
            self.display_request_details(self.selected_request_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update request status: {e}")
    
    def show_assign_blood_units(self):
        if not self.selected_request_id:
            return
        
        try:
            # Get request details
            request = BloodRequestRepo.get_request_by_id(self.selected_request_id)
            if not request:
                messagebox.showerror("Error", f"Could not find request with ID {self.selected_request_id}")
                return
                
            # Check if all units are already assigned
            if request["units_assigned"] >= request["units_required"]:
                messagebox.showinfo("Info", "All required blood units have already been assigned to this request")
                return
                
            # Get compatible blood units
            try:
                compatible_units = BloodRequestRepo.get_compatible_blood_units(request["blood_type_id"])
                
                if not compatible_units:
                    messagebox.showwarning("No Units", f"No compatible blood units available for blood type {request['blood_type']}")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to find compatible blood units: {str(e)}")
                return
            
            # Create a top level window for unit selection
            assign_window = tk.Toplevel(self.parent)
            assign_window.title("Assign Blood Units")
            assign_window.geometry("600x500")  # Increased height to ensure buttons are visible
            assign_window.minsize(600, 500)    # Set minimum size to prevent buttons from being hidden
            assign_window.transient(self.parent)
            assign_window.grab_set()
            
            # Create main frame with padding and layout management
            main_frame = ttk.Frame(assign_window, padding=10)
            main_frame.pack(fill="both", expand=True)
            
            # Make sure the main frame uses the proper pack configuration
            assign_window.update_idletasks()  # Force geometry calculation
            
            # Request info
            info_frame = ttk.LabelFrame(main_frame, text="Request Information")
            info_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Label(info_frame, text=f"Request #{request['request_id']} - {request['receiver_name']}").grid(
                row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(info_frame, text=f"Blood Type: {request['blood_type']}").grid(
                row=0, column=1, padx=5, pady=5, sticky="w")
            ttk.Label(info_frame, text=f"Units Required: {request['units_required']}").grid(
                row=1, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(info_frame, text=f"Units Assigned: {request['units_assigned']}").grid(
                row=1, column=1, padx=5, pady=5, sticky="w")
            
            # Available units
            units_frame = ttk.LabelFrame(main_frame, text="Available Compatible Blood Units")
            units_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add status label at the top
            status_text = f"Found {len(compatible_units)} compatible units for blood type {request['blood_type']}"
            ttk.Label(units_frame, text=status_text).pack(anchor="w", padx=5, pady=(5, 0))
            
            # Create scrollable container BEFORE creating the tree
            tree_container = ttk.Frame(units_frame)
            tree_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Units list - Create the treeview inside the container with donor information
            columns = ("Unit ID", "Donor Name", "Blood Type", "Collection Date", "Expiry Date", "Volume (ml)", "Location")
            unit_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=10)
            
            # Configure the column headings
            for col in columns:
                unit_tree.heading(col, text=col)
                if col == "Donor Name":
                    width = 150  # Make donor name column wider
                elif col in ["Unit ID", "Blood Type"]:
                    width = 80
                else:
                    width = 100
                unit_tree.column(col, width=width)
                
            # Create scrollbar
            scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=unit_tree.yview)
            
            # Configure the tree to use the scrollbar
            unit_tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar first
            scrollbar.pack(side="right", fill="y")
            
            # Pack the tree AFTER the scrollbar
            unit_tree.pack(side="left", fill="both", expand=True)
            
            # Debug information
            print(f"Found {len(compatible_units)} compatible blood units for blood type {request['blood_type']}")
            
            # Process and insert the compatible units
            count = 0
            for unit in compatible_units:
                try:
                    # Debug info
                    print(f"Processing unit ID: {unit.get('unit_id', 'unknown')} of type {unit.get('type_name', 'unknown')}")
                    
                    # Determine the date column name (could be donation_date or collection_date)
                    date_column = next((col for col in unit.keys() if col.endswith('_date') and col != 'expiry_date'), None)
                    print(f"  Found date column: {date_column}")
                    
                    # Format dates for display
                    collection_date = "N/A"
                    if date_column and unit[date_column]:
                        collection_date = unit[date_column].strftime('%Y-%m-%d')
                    
                    expiry_date = unit["expiry_date"].strftime('%Y-%m-%d') if unit["expiry_date"] else "N/A"
                    
                    # Determine location column name (could be location or storage_location)
                    location_column = "location"  # Default to 'location'
                    if "storage_location" in unit:
                        location_column = "storage_location"
                    
                    print(f"  Using location column: {location_column}")
                    print(f"  Location value: {unit.get(location_column, 'Unknown')}")
                    
                    # Get donor name
                    donor_name = unit.get("donor_name", "Unknown Donor")
                    print(f"  Donor: {donor_name}")
                    
                    # Create the values tuple for the treeview item including donor information
                    values = (
                        unit["unit_id"],
                        donor_name,
                        unit["type_name"],
                        collection_date,
                        expiry_date,
                        unit["volume_ml"],
                        unit.get(location_column, "Unknown")
                    )
                    
                    print(f"  Inserting values: {values}")
                    unit_tree.insert("", "end", values=values)
                    count += 1
                except Exception as e:
                    import traceback
                    print(f"Error displaying unit: {e}")
                    traceback.print_exc()
                    continue
                    
            # Update status after insertion
            if count > 0:
                ttk.Label(units_frame, text=f"{count} units displayed", foreground="blue").pack(anchor="e", padx=5)
            
            # Limit the tree view height to ensure buttons are visible
            unit_tree.configure(height=10)  # Limit to 10 rows
            
            # Button frame - place at bottom of main frame
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", padx=5, pady=10, side="bottom")
            
            def assign_selected_unit():
                selected_items = unit_tree.selection()
                if not selected_items:
                    messagebox.showwarning("No Selection", "Please select a blood unit to assign")
                    return
                
                unit_id = unit_tree.item(selected_items[0], "values")[0]
                
                try:
                    # Show a processing indicator
                    status_label = ttk.Label(assign_window, text="Processing assignment...", foreground="blue")
                    status_label.pack(pady=5)
                    assign_window.update()
                    
                    # Attempt the assignment
                    BloodRequestRepo.assign_blood_unit(self.selected_request_id, int(unit_id))
                    
                    # Success notification
                    status_label.config(text="Assignment successful!", foreground="green")
                    assign_window.update()
                    
                    # Show success message
                    messagebox.showinfo("Success", f"Blood unit #{unit_id} assigned to request #{self.selected_request_id}")
                    
                    # Check if all units are now assigned
                    updated_request = BloodRequestRepo.get_request_by_id(self.selected_request_id)
                    if updated_request["units_assigned"] >= updated_request["units_required"]:
                        assign_window.destroy()
                        self.load_requests()
                        self.display_request_details(self.selected_request_id)
                    else:
                        # Remove the assigned unit from the list
                        unit_tree.delete(selected_items[0])
                        status_label.destroy()
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Assignment error: {e}\n{error_details}")
                    
                    # Show user-friendly error message
                    if "not available" in str(e).lower():
                        messagebox.showerror("Unit Not Available", 
                            "This blood unit is no longer available. It may have been assigned to another request.")
                    elif "already assigned" in str(e).lower():
                        messagebox.showerror("Already Assigned", 
                            "This blood unit has already been assigned to a request.")
                    else:
                        messagebox.showerror("Assignment Error", 
                            f"Failed to assign blood unit: {e}")
                    
                    # Refresh the units list to show current availability
                    try:
                        # Get updated list of compatible units
                        compatible_units = BloodRequestRepo.get_compatible_blood_units(request["blood_type_id"])
                        
                        # Clear the existing tree
                        unit_tree.delete(*unit_tree.get_children())
                        
                        # Re-insert all units
                        count = 0
                        for unit in compatible_units:
                            try:
                                # Determine the date column name (could be donation_date or collection_date)
                                date_column = next((col for col in unit.keys() if col.endswith('_date') and col != 'expiry_date'), None)
                                
                                # Format dates for display
                                collection_date = "N/A"
                                if date_column and unit[date_column]:
                                    collection_date = unit[date_column].strftime('%Y-%m-%d')
                                
                                expiry_date = unit["expiry_date"].strftime('%Y-%m-%d') if unit["expiry_date"] else "N/A"
                                
                                # Determine location column name
                                location_column = "location"  # Default
                                if "storage_location" in unit:
                                    location_column = "storage_location"
                                
                                # Get donor name
                                donor_name = unit.get("donor_name", "Unknown Donor")
                                
                                # Insert the values into the treeview with donor information
                                unit_tree.insert("", "end", values=(
                                    unit["unit_id"],
                                    donor_name,
                                    unit["type_name"],
                                    collection_date,
                                    expiry_date,
                                    unit["volume_ml"],
                                    unit.get(location_column, "Unknown")
                                ))
                                count += 1
                            except Exception as e:
                                print(f"Error displaying refreshed unit: {e}")
                                continue
                        
                        # Update status label
                        status_text = f"Found {count} compatible units for blood type {request['blood_type']}"
                        for child in units_frame.winfo_children():
                            if isinstance(child, ttk.Label):
                                child.destroy()
                        
                        ttk.Label(units_frame, text=status_text).pack(anchor="w", padx=5, pady=(5, 0))
                        
                    except Exception as e:
                        print(f"Error refreshing units: {e}")
                        # If refreshing fails, don't worry about it
                        pass
            
            # Create more prominent buttons for better visibility
            assign_button = ttk.Button(button_frame, text="Assign Selected Unit", 
                                     command=assign_selected_unit)
            assign_button.pack(side="left", padx=5, pady=5)
            
            close_button = ttk.Button(button_frame, text="Close", 
                                    command=assign_window.destroy)
            close_button.pack(side="right", padx=5, pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open unit assignment: {e}")
            
    def assign_blood_to_request(self, request):
        """Assign available blood units to the selected request."""
        if not request or not request.get("request_id"):
            messagebox.showwarning("No Selection", "Please select a request first.")
            return
        
        try:
            # Get blood type ID for this request
            blood_type_id = request.get("blood_type_id")
            units_required = request.get("units_required", 0)
            units_fulfilled = request.get("units_fulfilled", 0)
            units_needed = units_required - units_fulfilled
            
            if units_needed <= 0:
                messagebox.showinfo("Information", "This request already has all required units fulfilled.")
                return
            
            # Get matching available blood units
            available_units = self.blood_unit_repo.get_available_blood_units_by_type(blood_type_id)
            
            if not available_units:
                messagebox.showwarning("No Units Available", 
                                     f"No matching blood units of type {request.get('blood_type')} are available.")
                return
            
            # Create a new window for blood unit selection
            window = tk.Toplevel()
            window.title("Assign Blood Units")
            window.geometry("600x500")
            window.grab_set()  # Make the window modal
            
            # Request information
            info_frame = ttk.Frame(window, padding=10)
            info_frame.pack(fill="x")
            
            ttk.Label(info_frame, text=f"Request ID: {request['request_id']}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Receiver: {request['receiver_name']}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Blood Type: {request['blood_type']}").pack(anchor="w")
            
            ttk.Label(info_frame, text=f"Units Required: {units_required}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Units Fulfilled: {units_fulfilled}").pack(anchor="w")
            ttk.Label(info_frame, text=f"Units Needed: {units_needed}").pack(anchor="w")
            
            # Available blood units list
            units_frame = ttk.LabelFrame(window, text=f"Available {request['blood_type']} Blood Units", padding=10)
            units_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create a list with checkboxes
            scroll_frame = ttk.Frame(units_frame)
            scroll_frame.pack(fill="both", expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(scroll_frame)
            scrollbar.pack(side="right", fill="y")
            
            # Listbox for blood units
            blood_units_list = tk.Listbox(scroll_frame, selectmode="multiple", yscrollcommand=scrollbar.set)
            blood_units_list.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=blood_units_list.yview)
            
            # Add units to listbox
            unit_map = {}  # Map listbox index to blood unit data
            for i, unit in enumerate(available_units):
                # Format: Unit ID | Donor | Collection Date | Expiration Date
                collection_date = unit["collection_date"].strftime('%Y-%m-%d') if unit["collection_date"] else "Unknown"
                expiry_date = unit["expiration_date"].strftime('%Y-%m-%d') if unit["expiration_date"] else "Unknown"
                
                display_text = f"Unit #{unit['unit_id']} | {unit['donor_name']} | Collected: {collection_date} | Expires: {expiry_date}"
                blood_units_list.insert(tk.END, display_text)
                unit_map[i] = unit
            
            # Buttons frame
            buttons_frame = ttk.Frame(window, padding=10)
            buttons_frame.pack(fill="x")
            
            def assign_selected_units():
                selected_indices = blood_units_list.curselection()
                if not selected_indices:
                    messagebox.showwarning("No Selection", "Please select at least one blood unit to assign.")
                    return
                    
                # Limit selection to only what's needed
                if len(selected_indices) > units_needed:
                    messagebox.showwarning("Too Many Selected", 
                                         f"You've selected {len(selected_indices)} units but only {units_needed} more are needed. Please select fewer units.")
                    return
                    
                # Update the status of the selected blood units
                units_assigned = 0
                for idx in selected_indices:
                    unit = unit_map[idx]
                    try:
                        self.blood_unit_repo.update_blood_unit_status(unit["unit_id"], "Assigned")
                        units_assigned += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to assign unit #{unit['unit_id']}: {e}")
                
                # Update the request's units_fulfilled count
                if units_assigned > 0:
                    new_fulfilled = units_fulfilled + units_assigned
                    try:
                        print(f"Updating request {request['request_id']} with {new_fulfilled} fulfilled units")
                        print(f"Original fulfilled: {units_fulfilled}, New assigned: {units_assigned}")
                        BloodRequestRepo.update_units_fulfilled(request["request_id"], new_fulfilled)
                        
                        # Get the updated request
                        updated_request = BloodRequestRepo.get_request_by_id(request["request_id"])
                        print(f"After assignment - Status: {updated_request['status']}, Units fulfilled: {updated_request.get('units_fulfilled', 0)}")
                        
                        messagebox.showinfo("Success", f"Successfully assigned {units_assigned} blood units to this request.")
                        
                        # Close the window and refresh the UI
                        window.destroy()
                        self.load_requests()
                        self.display_request_details(request["request_id"])
                    except Exception as e:
                        print(f"Error updating request: {e}")
                        messagebox.showerror("Error", f"Failed to update request: {e}")
            
            ttk.Button(buttons_frame, text="Assign Selected Units", command=assign_selected_units).pack(side="right", padx=5)
            ttk.Button(buttons_frame, text="Cancel", command=window.destroy).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to assign blood units: {e}")
    
