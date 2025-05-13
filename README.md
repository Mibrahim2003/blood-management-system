# Blood Donation Management System

This project is a comprehensive blood donation management system that provides a graphical user interface (GUI) for managing donors, receivers, blood units, and blood requests. The system is built using Python with Tkinter for the GUI and PostgreSQL for data storage.

## Features

- **Donor Management**: Register donors, track donation history, and manage donor information
- **Receiver Management**: Register patients in need of blood transfusions
- **Blood Unit Management**: Track collected blood units with their types, collection dates, and expiry dates
- **Blood Request Management**: Manage blood transfusion requests with priority levels
- **Blood Assignment**: Match compatible blood units to pending requests
- **Status Tracking**: Monitor the status of blood requests (Pending, Processing, Fulfilled, Cancelled)

## Project Structure

```
blood_donation_system
├── src
│   ├── app.py                 # Main application entry point
│   ├── database
│   │   ├── __init__.py
│   │   ├── db_config.py       # Configuration for database connection
│   │   ├── connection.py       # Handles database connections
│   │   └── repositories
│   │       ├── __init__.py
│   │       ├── donor_repo.py   # Functions for donor management
│   │       ├── receiver_repo.py # Functions for receiver management
│   │       ├── blood_unit_repo.py # Functions for blood unit management
│   │       ├── blood_request_repo.py # Functions for blood request management
│   │       └── medical_conditions_repo.py # Functions for medical conditions management
│   ├── models
│   │   ├── __init__.py
│   │   ├── donor.py            # Donor model
│   │   ├── receiver.py         # Receiver model
│   │   ├── blood_unit.py       # Blood unit model
│   │   ├── blood_request.py     # Blood request model
│   │   ├── medical_condition.py  # Medical condition model
│   │   └── blood_type.py       # Blood type model
│   ├── views
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main GUI window
│   │   ├── donor_views.py      # Donor-related views
│   │   ├── receiver_views.py    # Receiver-related views
│   │   ├── blood_unit_views.py  # Blood unit-related views
│   │   ├── blood_request_views.py # Blood request-related views
│   │   └── reports_view.py     # Reports generation and display
│   └── utils
│       ├── __init__.py
│       └── validation.py       # Input validation utilities
├── database.ini                # Database configuration
├── blood_donation.sql          # SQL schema for the database
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Database Schema

The application uses a PostgreSQL database with the following structure:

- **Blood_Types**: Stores blood type information (A+, A-, B+, etc.)
- **Donors**: Stores donor personal details and medical information
- **Receivers**: Stores information about blood receivers, including hospital details
- **Blood_Units**: Tracks individual units of blood, including collection and expiry dates
- **Blood_Requests**: Manages requests for blood from receivers
- **Medical_Conditions**: Tracks medical conditions that may affect blood donation

## Setup Instructions

1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd blood_donation_system
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Configure Database**
   Update the `utils/database.ini` file with your PostgreSQL database credentials.

4. **Run the Application**
   Execute the main application using the provided launcher:
   ```
   python launch_app.py
   ```
   
   The application will automatically initialize the database tables on first run.

   **Command Line Options:**
   ```
   python launch_app.py --help                     # Show all available options
   python launch_app.py --run-db-fixes             # Run all database fixes 
   python launch_app.py --generate-test-data       # Generate 50 test blood units
   python launch_app.py --generate-test-data --test-units 100  # Generate 100 test blood units
   ```

## Usage

- The application allows users to manage donors, receivers, and blood requests through a user-friendly interface.
- Users can add, update, and delete records.

### Donors Management
- View a list of all donors in the system
- Search for donors by name, blood type, and other attributes
- Add new donors with personal and medical details
- Edit existing donor information
- Delete donors from the system

### Receivers Management
- View a list of all blood receivers
- Search for receivers with highlighted results matching the search term
- Add new receivers with comprehensive validation for all fields
- View detailed receiver information including personal, medical, and contact details
- Edit existing receiver information with field validation
- Delete receivers from the system with confirmation

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.