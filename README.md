# Blood Donation Management System

A comprehensive application for managing blood donation centers, built with Python, Tkinter, and PostgreSQL.

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
│   ├── app.py                  # Main application entry point
│   ├── database
│   │   ├── connection.py       # Handles database connections
│   │   ├── db_config.py        # Configuration for database connection
│   │   └── repositories        # Data access layer
│   │       ├── blood_request_repo.py
│   │       ├── blood_unit_repo.py
│   │       ├── donor_repo.py
│   │       ├── medical_conditions_repo.py
│   │       └── receiver_repo.py
│   ├── models                  # Data models
│   │   ├── blood_request.py
│   │   ├── blood_type.py
│   │   ├── blood_unit.py
│   │   ├── donor.py
│   │   ├── medical_condition.py
│   │   └── receiver.py
│   ├── utils                   # Utility functions
│   │   ├── fix_blood_units.py
│   │   ├── fix_database.py
│   │   ├── generate_test_data.py
│   │   ├── initialize_db.py
│   │   └── validation.py
│   └── views                   # User interface
│       ├── blood_request_views.py
│       ├── blood_unit_views.py
│       ├── donor_views.py
│       ├── enhanced_blood_unit_views.py
│       ├── main_window.py
│       ├── receiver_views.py
│       ├── reports_view.py
│       └── simplified_blood_unit_views.py
├── database.ini                # Database configuration file
├── blood_donation.sql          # SQL schema for the database
├── launch_app.py               # Entry point script
└── requirements.txt            # Python package dependencies
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
   git clone https://github.com/Mibrahim2003/blood-donation-system.git
   cd blood-donation-system
   ```

2. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure Database**
   
   Update the `database.ini` file with your PostgreSQL database credentials:
   ```ini
   [postgresql]
   host=localhost
   database=blood_donation
   user=your_username
   password=your_password
   ```

4. **Initialize Database**
   
   The application will automatically create the necessary tables on first run, or you can run:
   ```
   python -m src.utils.initialize_db
   ```

5. **Run the Application**
   ```
   python launch_app.py
   ```

   **Command Line Options:**
   ```
   python launch_app.py --help                     # Show all available options
   python launch_app.py --run-db-fixes             # Run all database fixes 
   python launch_app.py --generate-test-data       # Generate test data
   ```

## Usage

### Donor Management
- Register new donors with personal and medical details
- View and edit donor information
- Track donation history

### Blood Unit Management
- Record new blood units with collection date, expiry date, and status
- Track blood unit status (Available, Reserved, Used, Expired)
- View available blood units by type

### Blood Request Management
- Register new blood requests from receivers
- Set priority levels for requests
- Assign available blood units to requests
- Track request status (Pending, Processing, Fulfilled, Cancelled)

### Enhanced Features
- Automatic status updates when all requested blood units are fulfilled
- Validation of blood type compatibility during assignment
- Reports for blood inventory and usage statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.