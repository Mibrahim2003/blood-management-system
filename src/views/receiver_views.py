import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database.repositories.receiver_repo import ReceiverRepository
from utils.validation_utils import validate_receiver_data

class ReceiverManagementFrame:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.receiver_repo = ReceiverRepository()
        self.setup_ui()
        
    def setup_ui(self):
        # Clear the parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # Create a frame for receiver management with left and right panels
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (receiver list)
        left_frame = ttk.LabelFrame(main_frame, text="Receiver List")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.search_receivers)
        
        # Receiver list
        columns = ("ID", "Name", "Blood Type", "Hospital", "Reason")
        self.receiver_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.receiver_tree.heading(col, text=col)
            width = 100 if col != "Name" else 150
            self.receiver_tree.column(col, width=width)
            
        self.receiver_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.receiver_tree.bind("<<TreeviewSelect>>", self.on_receiver_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.receiver_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.receiver_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Receiver", command=self.show_add_receiver_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_receivers).pack(side="left", padx=5)
        
        # Right panel (receiver details)
        self.right_frame = ttk.LabelFrame(main_frame, text="Receiver Details")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Load receivers from database
        self.load_receivers()
    
    def load_receivers(self):
        # Clear the tree
        for item in self.receiver_tree.get_children():
            self.receiver_tree.delete(item)
        
        # Get receivers from repository
        try:
            # Implement a get_all_receivers method in the ReceiverRepository class
            receivers = self.receiver_repo.get_all_receivers()
            
            for receiver in receivers:
                name = f"{receiver['first_name']} {receiver['last_name']}"
                
                # Get blood type - handle the case where it might be missing
                blood_type = receiver.get("blood_type", "Unknown")
                if not blood_type and "blood_type_id" in receiver:
                    # Map blood type ID to string if blood_type is not available
                    blood_type_map = {1: 'A+', 2: 'A-', 3: 'B+', 4: 'B-', 
                                     5: 'AB+', 6: 'AB-', 7: 'O+', 8: 'O-'}
                    blood_type = blood_type_map.get(receiver["blood_type_id"], "Unknown")
                
                self.receiver_tree.insert("", "end", values=(
                    receiver["receiver_id"],
                    name,
                    blood_type,
                    receiver["hospital_name"],
                    receiver["reason_for_transfusion"][:30] + "..." if len(receiver["reason_for_transfusion"]) > 30 else receiver["reason_for_transfusion"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receivers: {e}")
    
    def search_receivers(self, event=None):
        search_term = self.search_var.get().lower()
        
        # Clear the tree
        for item in self.receiver_tree.get_children():
            self.receiver_tree.delete(item)
        
        if not search_term:
            # If search is empty, just reload all receivers
            self.load_receivers()
            return
        
        # Get receivers from repository
        try:
            # Use the search_receivers method in the ReceiverRepository class
            receivers = self.receiver_repo.search_receivers(search_term)
            
            for receiver in receivers:
                name = f"{receiver['first_name']} {receiver['last_name']}"
                
                # Get blood type - handle the case where it might be missing
                blood_type = receiver.get("blood_type", "Unknown")
                if not blood_type and "blood_type_id" in receiver:
                    # Map blood type ID to string if blood_type is not available
                    blood_type_map = {1: 'A+', 2: 'A-', 3: 'B+', 4: 'B-', 
                                     5: 'AB+', 6: 'AB-', 7: 'O+', 8: 'O-'}
                    blood_type = blood_type_map.get(receiver["blood_type_id"], "Unknown")
                
                # Truncate long reason text
                reason_text = receiver["reason_for_transfusion"]
                if len(reason_text) > 30:
                    reason_text = reason_text[:30] + "..."
                
                # Insert the item in the tree
                item_id = self.receiver_tree.insert("", "end", values=(
                    receiver["receiver_id"],
                    name,
                    blood_type,
                    receiver["hospital_name"],
                    reason_text
                ))
                
                # Highlight the matching term in the tree if found in name, blood type, or hospital
                if (search_term in name.lower() or 
                    search_term in blood_type.lower() or 
                    search_term in receiver["hospital_name"].lower() or
                    search_term in receiver["reason_for_transfusion"].lower()):
                    # Set a highlight color (light yellow background)
                    self.receiver_tree.item(item_id, tags=('highlight',))
            
            # Configure tag for highlighting
            self.receiver_tree.tag_configure('highlight', background='#FFFF99')
            
            if not receivers:
                ttk.Label(self.right_frame, text="No matching receivers found.").pack(pady=20)
                
        except Exception as e:
            print(f"Error in search_receivers: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to search receivers: {e}")
    
    def on_receiver_select(self, event=None):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Get the selected item
        selected_item = self.receiver_tree.selection()
        if not selected_item:
            return
            
        # Get the receiver ID
        receiver_id = self.receiver_tree.item(selected_item[0])["values"][0]
        
        # Get the receiver from repository
        try:
            # Implement a get_receiver_by_id method in the ReceiverRepository class
            receiver = self.receiver_repo.get_receiver_by_id(receiver_id)
            if receiver:
                self.display_receiver_details(receiver)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receiver details: {e}")
    
    def display_receiver_details(self, receiver):
        # Create a frame for receiver details
        details_frame = ttk.Frame(self.right_frame)
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Personal information section
        personal_frame = ttk.LabelFrame(details_frame, text="Personal Information")
        personal_frame.pack(fill="x", padx=5, pady=5)
        
        # Get blood type - handle the case where it might be missing
        blood_type = receiver.get("blood_type", "Unknown")
        if not blood_type and "blood_type_id" in receiver:
            # Map blood type ID to string if blood_type is not available
            blood_type_map = {1: 'A+', 2: 'A-', 3: 'B+', 4: 'B-', 
                             5: 'AB+', 6: 'AB-', 7: 'O+', 8: 'O-'}
            blood_type = blood_type_map.get(receiver["blood_type_id"], "Unknown")
            
        # Format the display in a grid
        row = 0
        for label, value in [
            ("ID:", receiver["receiver_id"]),
            ("Name:", f"{receiver['first_name']} {receiver['last_name']}"),
            ("Date of Birth:", receiver["dob"]),
            ("Gender:", receiver["gender"]),
            ("Blood Type:", blood_type),
        ]:
            ttk.Label(personal_frame, text=label, width=15).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(personal_frame, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1
        
        # Medical information section
        medical_frame = ttk.LabelFrame(details_frame, text="Medical Information")
        medical_frame.pack(fill="x", padx=5, pady=5)
        
        row = 0
        for label, value in [
            ("Hospital:", receiver["hospital_name"]),
            ("Ward Details:", receiver["ward_details"]),
            ("Reason for Transfusion:", receiver["reason_for_transfusion"]),
        ]:
            ttk.Label(medical_frame, text=label, width=15).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(medical_frame, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1
        
        # Contact information section
        contact_frame = ttk.LabelFrame(details_frame, text="Contact Information")
        contact_frame.pack(fill="x", padx=5, pady=5)
        
        row = 0
        for label, value in [
            ("Contact Person:", receiver["contact_person_name"]),
            ("Contact Phone:", receiver["contact_person_phone"]),
            ("Registration Date:", receiver["registration_date"]),
        ]:
            ttk.Label(contact_frame, text=label, width=15).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(contact_frame, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1
        
        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Edit Receiver", 
                 command=lambda: self.show_edit_receiver_form(receiver)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Receiver", 
                 command=lambda: self.delete_receiver(receiver)).pack(side="left", padx=5)
    
    def show_add_receiver_form(self):
        # Create a new window for adding a receiver
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add New Receiver")
        add_window.geometry("500x600")
        
        # Form inside a scrollable frame
        main_frame = ttk.Frame(add_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variables for form fields
        first_name_var = tk.StringVar()
        last_name_var = tk.StringVar()
        dob_var = tk.StringVar()
        gender_var = tk.StringVar()
        blood_type_var = tk.StringVar()
        reason_var = tk.StringVar()
        hospital_var = tk.StringVar()
        ward_var = tk.StringVar()
        contact_name_var = tk.StringVar()
        contact_phone_var = tk.StringVar()
        
        # Personal information fields
        personal_frame = ttk.LabelFrame(scrollable_frame, text="Personal Information")
        personal_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(personal_frame, text="First Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=first_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Last Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=last_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=dob_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Gender:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        gender_combo = ttk.Combobox(personal_frame, textvariable=gender_var, width=27)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Blood Type:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        blood_type_combo = ttk.Combobox(personal_frame, textvariable=blood_type_var, width=27)
        blood_type_combo['values'] = ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
        blood_type_combo.grid(row=4, column=1, padx=5, pady=5)
        
        # Medical information fields
        medical_frame = ttk.LabelFrame(scrollable_frame, text="Medical Information")
        medical_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Reason for Transfusion:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        reason_entry = tk.Text(medical_frame, height=3, width=30)
        reason_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Hospital Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(medical_frame, textvariable=hospital_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Ward Details:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(medical_frame, textvariable=ward_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Contact information fields
        contact_frame = ttk.LabelFrame(scrollable_frame, text="Contact Information")
        contact_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(contact_frame, text="Contact Person Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(contact_frame, textvariable=contact_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contact_frame, text="Contact Person Phone:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(contact_frame, textvariable=contact_phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_new_receiver(
                first_name_var.get(),
                last_name_var.get(),
                dob_var.get(),
                gender_var.get(),
                blood_type_var.get(),
                reason_entry.get("1.0", "end-1c"),
                hospital_var.get(),
                ward_var.get(),
                contact_name_var.get(),
                contact_phone_var.get(),
                add_window
            )
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=add_window.destroy
        ).pack(side="left", padx=5)
    
    def save_new_receiver(self, first_name, last_name, dob, gender, blood_type, reason, hospital, ward, contact_name, contact_phone, window):
        # Use our centralized validation utility - create a data dictionary as expected by the function
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "gender": gender,
            "blood_type_id": blood_type,  # This will be converted to an ID later
            "reason_for_transfusion": reason,
            "hospital_name": hospital,
            "ward_details": ward,
            "contact_person_name": contact_name,
            "contact_person_phone": contact_phone
        }
        
        validation_errors = validate_receiver_data(data)
            
        # Show validation errors if any
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return
        
        # Try to add the receiver
        try:
            # Implement the blood type conversion to blood_type_id
            blood_type_id = self.get_blood_type_id(blood_type)
            
            success = self.receiver_repo.add_receiver(
                first_name, last_name, dob, gender, blood_type_id, reason, hospital, ward, contact_name, contact_phone
            )
            
            if success:
                messagebox.showinfo("Success", "Receiver added successfully.")
                window.destroy()
                self.load_receivers()
            else:
                messagebox.showerror("Error", "Failed to add receiver.")
        except Exception as e:
            print(f"Error in save_new_receiver: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to add receiver: {e}")
    
    def get_blood_type_id(self, blood_type):
        """Get the ID for a blood type from the database or a fallback mapping."""
        # Ensure the blood_type is not empty
        if not blood_type:
            print("Warning: Empty blood type provided, defaulting to 'A+'")
            return 1
            
        # Try to get the ID from the database first
        try:
            # Make sure we have a connection
            self.receiver_repo.connect()
            connection = self.receiver_repo.connection
                
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT blood_type_id FROM Blood_Types WHERE type_name = %s
                """, (blood_type,))
                result = cursor.fetchone()
                if result:
                    print(f"Found blood type ID {result[0]} for {blood_type}")
                    return result[0]
        except Exception as e:
            print(f"Error getting blood type ID from database: {e}")
            import traceback
            traceback.print_exc()
        
        # Fall back to the mapping if database lookup fails
        blood_type_map = {
            'A+': 1, 'A-': 2, 'B+': 3, 'B-': 4, 
            'AB+': 5, 'AB-': 6, 'O+': 7, 'O-': 8
        }
        blood_type_id = blood_type_map.get(blood_type, 1)  # Default to 1 if not found
        print(f"Using mapped blood type ID {blood_type_id} for {blood_type}")
        return blood_type_id
    
    def show_edit_receiver_form(self, receiver):
        # Create a new window for editing a receiver
        edit_window = tk.Toplevel(self.parent)
        edit_window.title(f"Edit Receiver: {receiver['first_name']} {receiver['last_name']}")
        edit_window.geometry("500x600")
        
        # Form inside a scrollable frame
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Variables for form fields with pre-filled values
        first_name_var = tk.StringVar(value=receiver['first_name'])
        last_name_var = tk.StringVar(value=receiver['last_name'])
        dob_var = tk.StringVar(value=receiver['dob'])
        gender_var = tk.StringVar(value=receiver['gender'])
        blood_type_var = tk.StringVar(value=receiver['blood_type'])
        hospital_var = tk.StringVar(value=receiver['hospital_name'])
        ward_var = tk.StringVar(value=receiver['ward_details'])
        contact_name_var = tk.StringVar(value=receiver['contact_person_name'])
        contact_phone_var = tk.StringVar(value=receiver['contact_person_phone'])
        
        # Personal information fields
        personal_frame = ttk.LabelFrame(scrollable_frame, text="Personal Information")
        personal_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(personal_frame, text="First Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=first_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Last Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=last_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(personal_frame, textvariable=dob_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Gender:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        gender_combo = ttk.Combobox(personal_frame, textvariable=gender_var, width=27)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(personal_frame, text="Blood Type:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        blood_type_combo = ttk.Combobox(personal_frame, textvariable=blood_type_var, width=27)
        blood_type_combo['values'] = ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
        blood_type_combo.grid(row=4, column=1, padx=5, pady=5)
        
        # Medical information fields
        medical_frame = ttk.LabelFrame(scrollable_frame, text="Medical Information")
        medical_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Reason for Transfusion:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        reason_entry = tk.Text(medical_frame, height=3, width=30)
        reason_entry.insert("1.0", receiver['reason_for_transfusion'])
        reason_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Hospital Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(medical_frame, textvariable=hospital_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(medical_frame, text="Ward Details:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(medical_frame, textvariable=ward_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Contact information fields
        contact_frame = ttk.LabelFrame(scrollable_frame, text="Contact Information")
        contact_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(contact_frame, text="Contact Person Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(contact_frame, textvariable=contact_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contact_frame, text="Contact Person Phone:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(contact_frame, textvariable=contact_phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_edited_receiver(
                receiver['receiver_id'],
                first_name_var.get(),
                last_name_var.get(),
                dob_var.get(),
                gender_var.get(),
                blood_type_var.get(),
                reason_entry.get("1.0", "end-1c"),
                hospital_var.get(),
                ward_var.get(),
                contact_name_var.get(),
                contact_phone_var.get(),
                edit_window
            )
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=edit_window.destroy
        ).pack(side="left", padx=5)
    
    def save_edited_receiver(self, receiver_id, first_name, last_name, dob, gender, blood_type, reason, 
                           hospital, ward, contact_name, contact_phone, window):
        # Use our centralized validation utility - create a data dictionary as expected by the function
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "gender": gender,
            "blood_type_id": blood_type,  # This will be converted to an ID later
            "reason_for_transfusion": reason,
            "hospital_name": hospital,
            "ward_details": ward,
            "contact_person_name": contact_name,
            "contact_person_phone": contact_phone
        }
        
        validation_errors = validate_receiver_data(data)
            
        # Show validation errors if any
        if validation_errors:
            messagebox.showerror("Validation Error", "\n".join(validation_errors))
            return
        
        # Try to update the receiver
        try:
            # Get the blood type ID
            blood_type_id = self.get_blood_type_id(blood_type)
            print(f"Converting blood type {blood_type} to ID: {blood_type_id}")
            
            success = self.receiver_repo.update_receiver(
                receiver_id, first_name, last_name, dob, gender, blood_type_id, reason, 
                hospital, ward, contact_name, contact_phone
            )
            
            if success:
                messagebox.showinfo("Success", "Receiver updated successfully.")
                window.destroy()
                self.load_receivers()
            else:
                messagebox.showerror("Error", "Failed to update receiver.")
        except Exception as e:
            print(f"Error in save_edited_receiver: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to update receiver: {e}")
    
    def delete_receiver(self, receiver):
        # Ask for confirmation
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {receiver['first_name']} {receiver['last_name']}?"):
            try:
                # Check if the receiver might be referenced by any blood requests
                # This would be a good place to add a check if there are foreign key constraints
                
                success = self.receiver_repo.delete_receiver(receiver['receiver_id'])
                
                if success:
                    messagebox.showinfo("Success", "Receiver deleted successfully.")
                    self.load_receivers()
                    
                    # Clear the right frame
                    for widget in self.right_frame.winfo_children():
                        widget.destroy()
                else:
                    messagebox.showerror("Error", "Failed to delete receiver. The receiver may be referenced by blood requests.")
            except Exception as e:
                print(f"Error in delete_receiver: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to delete receiver: {e}")

    def clear_entries(self):
        self.first_name_entry.delete(0, 'end')
        self.last_name_entry.delete(0, 'end')
        self.dob_entry.delete(0, 'end')
        self.gender_entry.delete(0, 'end')
        self.blood_type_id_entry.delete(0, 'end')