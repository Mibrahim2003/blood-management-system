import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database.repositories.donor_repo import DonorRepository

class DonorManagementFrame:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.donor_repo = DonorRepository()
        self.setup_ui()
        
    def setup_ui(self):
        # Clear the parent frame
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # Create a frame for donor management with left and right panels
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (donor list)
        left_frame = ttk.LabelFrame(main_frame, text="Donor List")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.search_donors)
        
        # Donor list
        columns = ("ID", "Name", "Blood Type", "Phone", "Last Donation")
        self.donor_tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.donor_tree.heading(col, text=col)
            width = 100 if col != "Name" else 150
            self.donor_tree.column(col, width=width)
            
        self.donor_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.donor_tree.bind("<<TreeviewSelect>>", self.on_donor_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.donor_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.donor_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Add Donor", command=self.show_add_donor_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_donors).pack(side="left", padx=5)
        
        # Right panel (donor details)
        self.right_frame = ttk.LabelFrame(main_frame, text="Donor Details")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Load donors from database
        self.load_donors()
    
    def load_donors(self):
        # Clear the tree
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
        
        # Get donors from repository
        try:
            donors = self.donor_repo.get_all_donors()
            
            for donor in donors:
                last_donation = donor["last_donation_date"] if donor["last_donation_date"] else "Never"
                name = f"{donor['first_name']} {donor['last_name']}"
                
                self.donor_tree.insert("", "end", values=(
                    donor["donor_id"],
                    name,
                    donor["blood_type"],
                    donor["phone_number"],
                    last_donation
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load donors: {e}")
    
    def search_donors(self, event=None):
        search_term = self.search_var.get().lower()
        
        # Clear the tree
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
        
        # Get donors from repository
        try:
            donors = self.donor_repo.search_donors(search_term)
            
            for donor in donors:
                last_donation = donor["last_donation_date"] if donor["last_donation_date"] else "Never"
                name = f"{donor['first_name']} {donor['last_name']}"
                
                self.donor_tree.insert("", "end", values=(
                    donor["donor_id"],
                    name,
                    donor["blood_type"],
                    donor["phone_number"],
                    last_donation
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search donors: {e}")
    
    def on_donor_select(self, event=None):
        # Clear the right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Get the selected item
        selected_item = self.donor_tree.selection()
        if not selected_item:
            return
            
        # Get the donor ID
        donor_id = self.donor_tree.item(selected_item[0])["values"][0]
        
        # Get the donor from repository
        try:
            donor = self.donor_repo.get_donor_by_id(donor_id)
            if donor:
                self.display_donor_details(donor)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load donor details: {e}")
    
    def display_donor_details(self, donor):
        # Create a frame for donor details
        details_frame = ttk.Frame(self.right_frame)
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Personal information section
        personal_frame = ttk.LabelFrame(details_frame, text="Personal Information")
        personal_frame.pack(fill="x", padx=5, pady=5)
        
        # Format the display in a grid
        row = 0
        for label, value in [
            ("ID:", donor["donor_id"]),
            ("Name:", f"{donor['first_name']} {donor['last_name']}"),
            ("Date of Birth:", donor["dob"]),
            ("Gender:", donor["gender"]),
            ("Blood Type:", donor["blood_type"]),
            ("Phone:", donor["phone_number"]),
            ("Email:", donor["email"]),
            ("Address:", donor["address"])
        ]:
            ttk.Label(personal_frame, text=label, width=15).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(personal_frame, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1
        
        # Donation information section
        donation_frame = ttk.LabelFrame(details_frame, text="Donation Information")
        donation_frame.pack(fill="x", padx=5, pady=5)
        
        row = 0
        for label, value in [
            ("Registration Date:", donor["registration_date"]),
            ("Last Donation:", donor["last_donation_date"] if donor["last_donation_date"] else "Never"),
        ]:
            ttk.Label(donation_frame, text=label, width=15).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(donation_frame, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            row += 1
        
        # Buttons frame
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Edit Donor", 
                 command=lambda: self.show_edit_donor_form(donor)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete Donor", 
                 command=lambda: self.delete_donor(donor)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Record Donation", 
                 command=lambda: self.record_donation(donor)).pack(side="left", padx=5)
    
    def show_add_donor_form(self):
        # Create a new window for adding a donor
        add_window = tk.Toplevel(self.parent)
        add_window.title("Add New Donor")
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
        phone_var = tk.StringVar()
        email_var = tk.StringVar()
        address_var = tk.StringVar()
        
        # Form fields
        ttk.Label(scrollable_frame, text="First Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=first_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Last Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=last_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=dob_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Gender:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        gender_combo = ttk.Combobox(scrollable_frame, textvariable=gender_var, width=27)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Blood Type:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        blood_type_combo = ttk.Combobox(scrollable_frame, textvariable=blood_type_var, width=27)
        blood_type_combo['values'] = ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
        blood_type_combo.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Phone Number:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=phone_var, width=30).grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Email:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=email_var, width=30).grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Address:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        address_entry = tk.Text(scrollable_frame, height=3, width=30)
        address_entry.grid(row=7, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_new_donor(
                first_name_var.get(),
                last_name_var.get(),
                dob_var.get(),
                gender_var.get(),
                blood_type_var.get(),
                phone_var.get(),
                email_var.get(),
                address_entry.get("1.0", "end-1c"),
                add_window
            )
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=add_window.destroy
        ).pack(side="left", padx=5)
    
    def save_new_donor(self, first_name, last_name, dob, gender, blood_type, phone, email, address, window):
        # Validate the form
        if not all([first_name, last_name, dob, gender, blood_type, phone]):
            messagebox.showerror("Validation Error", "Please fill in all required fields.")
            return
        
        # Validate date format
        try:
            datetime.datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return
        
        # Try to add the donor
        try:
            success = self.donor_repo.add_donor(
                first_name, last_name, dob, gender, blood_type, phone, email, address
            )
            
            if success:
                messagebox.showinfo("Success", "Donor added successfully.")
                window.destroy()
                self.load_donors()
            else:
                messagebox.showerror("Error", "Failed to add donor.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add donor: {e}")
    
    def show_edit_donor_form(self, donor):
        # Create a new window for editing a donor
        edit_window = tk.Toplevel(self.parent)
        edit_window.title(f"Edit Donor: {donor['first_name']} {donor['last_name']}")
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
        first_name_var = tk.StringVar(value=donor['first_name'])
        last_name_var = tk.StringVar(value=donor['last_name'])
        dob_var = tk.StringVar(value=donor['dob'])
        gender_var = tk.StringVar(value=donor['gender'])
        blood_type_var = tk.StringVar(value=donor['blood_type'])
        phone_var = tk.StringVar(value=donor['phone_number'])
        email_var = tk.StringVar(value=donor['email'] if donor['email'] else "")
        
        # Form fields
        ttk.Label(scrollable_frame, text="First Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=first_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Last Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=last_name_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Date of Birth (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=dob_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Gender:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        gender_combo = ttk.Combobox(scrollable_frame, textvariable=gender_var, width=27)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Blood Type:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        blood_type_combo = ttk.Combobox(scrollable_frame, textvariable=blood_type_var, width=27)
        blood_type_combo['values'] = ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')
        blood_type_combo.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Phone Number:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=phone_var, width=30).grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Email:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(scrollable_frame, textvariable=email_var, width=30).grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(scrollable_frame, text="Address:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        address_entry = tk.Text(scrollable_frame, height=3, width=30)
        address_entry.grid(row=7, column=1, padx=5, pady=5)
        address_entry.insert("1.0", donor['address'] if donor['address'] else "")
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Save Changes", 
            command=lambda: self.update_donor(
                donor['donor_id'],
                first_name_var.get(),
                last_name_var.get(),
                dob_var.get(),
                gender_var.get(),
                blood_type_var.get(),
                phone_var.get(),
                email_var.get(),
                address_entry.get("1.0", "end-1c"),
                edit_window
            )
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=edit_window.destroy
        ).pack(side="left", padx=5)
    
    def update_donor(self, donor_id, first_name, last_name, dob, gender, blood_type, phone, email, address, window):
        # Validate the form
        if not all([first_name, last_name, dob, gender, blood_type, phone]):
            messagebox.showerror("Validation Error", "Please fill in all required fields.")
            return
        
        # Validate date format
        try:
            datetime.datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return
        
        # Try to update the donor
        try:
            success = self.donor_repo.update_donor(
                donor_id, first_name, last_name, dob, gender, blood_type, phone, email, address
            )
            
            if success:
                messagebox.showinfo("Success", "Donor updated successfully.")
                window.destroy()
                self.load_donors()
                
                # Refresh the details view with updated info
                donor = self.donor_repo.get_donor_by_id(donor_id)
                if donor:
                    self.display_donor_details(donor)
            else:
                messagebox.showerror("Error", "Failed to update donor.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update donor: {e}")
    
    def delete_donor(self, donor):
        # Ask for confirmation
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {donor['first_name']} {donor['last_name']}?"):
            try:
                success = self.donor_repo.delete_donor(donor['donor_id'])
                
                if success:
                    messagebox.showinfo("Success", "Donor deleted successfully.")
                    self.load_donors()
                    
                    # Clear the right frame
                    for widget in self.right_frame.winfo_children():
                        widget.destroy()
                else:
                    messagebox.showerror("Error", "Failed to delete donor.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete donor: {e}")
    
    def record_donation(self, donor):
        # Create a window for recording a donation
        donation_window = tk.Toplevel(self.parent)
        donation_window.title(f"Record Donation: {donor['first_name']} {donor['last_name']}")
        donation_window.geometry("400x400")  # Made taller to fit buttons
        
        # Main frame with padding
        main_frame = ttk.Frame(donation_window, padding=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display donor information
        info_text = f"Recording donation for {donor['first_name']} {donor['last_name']} (ID: {donor['donor_id']})\n"
        info_text += f"Blood Type: {donor['blood_type']}"
        
        ttk.Label(main_frame, text=info_text, justify="center").pack(pady=10)
        
        # Date selection
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Donation Date (YYYY-MM-DD):").pack(side="left", padx=5)
        
        # Default to today's date
        today = datetime.date.today().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=today)
        date_entry = ttk.Entry(date_frame, textvariable=date_var, width=15)
        date_entry.pack(side="left", padx=5)
        
        # Volume selection
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(fill="x", pady=5)
        
        ttk.Label(volume_frame, text="Volume (ml):").pack(side="left", padx=5)
        
        volume_var = tk.StringVar(value="450")  # Default volume
        volume_entry = ttk.Entry(volume_frame, textvariable=volume_var, width=10)
        volume_entry.pack(side="left", padx=5)
        
        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor="w", pady=(10, 5))
        notes_entry = tk.Text(main_frame, height=4, width=40)
        notes_entry.pack(fill="x", expand=False, pady=5)
        
        # Create a separate frame for buttons at the bottom of the dialog
        bottom_frame = ttk.Frame(donation_window)
        bottom_frame.pack(fill="x", side="bottom", pady=10)
        
        # Add buttons to the bottom frame
        # Use more prominent styling for the buttons
        record_button = ttk.Button(
            bottom_frame, 
            text="Record Donation", 
            command=lambda: self.save_donation(
                donor['donor_id'],
                date_var.get(),
                volume_var.get(),
                notes_entry.get("1.0", "end-1c"),
                donation_window
            )
        )
        record_button.pack(side="left", padx=10)
        
        cancel_button = ttk.Button(
            bottom_frame, 
            text="Cancel", 
            command=donation_window.destroy
        )
        cancel_button.pack(side="right", padx=10)
    
    def save_donation(self, donor_id, donation_date, volume, notes, window):
        # Validate the form
        if not donation_date:
            messagebox.showerror("Validation Error", "Please enter a donation date.")
            return
        
        # Validate date format
        try:
            datetime.datetime.strptime(donation_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return
        
        # Validate volume
        try:
            volume_ml = int(volume)
            if volume_ml <= 0 or volume_ml > 550:
                messagebox.showerror("Validation Error", "Volume must be between 1 and 550 ml.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Volume must be a valid number.")
            return
        
        # Update last donation date and create blood unit
        try:
            # Get the donor
            donor = self.donor_repo.get_donor_by_id(donor_id)
            if not donor:
                messagebox.showerror("Error", "Donor not found.")
                return
            
            # Update the donor's last donation date
            success = self.donor_repo.update_donor(
                donor_id=donor_id,
                first_name=donor['first_name'],
                last_name=donor['last_name'],
                dob=donor['dob'],
                gender=donor['gender'],
                blood_type=donor['blood_type'],
                phone=donor['phone_number'],
                email=donor['email'],
                address=donor['address'],
                last_donation_date=donation_date  # Pass as named parameter
            )
            
            # Create a blood unit record
            from database.repositories.blood_unit_repo import BloodUnitRepository
            blood_unit_repo = BloodUnitRepository()
            
            # Get blood type ID
            blood_type_id = None
            for i, bt in enumerate(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']):
                if bt == donor['blood_type']:
                    blood_type_id = i + 1  # Blood type IDs are 1-based
                    break
            
            if not blood_type_id:
                messagebox.showwarning("Warning", "Blood type not recognized. Only donation date updated.")
            else:
                # Add a blood unit for this donation
                expiry_date = (datetime.datetime.strptime(donation_date, "%Y-%m-%d") + 
                              datetime.timedelta(days=42)).strftime("%Y-%m-%d")  # 6 weeks expiry
                
                # Add the blood unit with volume_ml parameter
                blood_unit_repo.add_blood_unit(
                    donor_id,
                    blood_type_id,
                    donation_date,
                    expiry_date,
                    'Available',
                    'Blood Bank Storage',
                    volume_ml  # Add the volume here
                )
            
            if success:
                messagebox.showinfo("Success", "Donation recorded successfully.")
                window.destroy()
                self.load_donors()
                
                # Refresh the details view with updated info
                donor = self.donor_repo.get_donor_by_id(donor_id)
                if donor:
                    self.display_donor_details(donor)
            else:
                messagebox.showerror("Error", "Failed to record donation.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record donation: {e}")