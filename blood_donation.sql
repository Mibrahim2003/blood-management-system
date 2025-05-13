-- Blood Donation Management System Database Schema

-- Drop blood unit related tables first since they've been removed from the system
DROP TABLE IF EXISTS Blood_Request_Units CASCADE;
DROP TABLE IF EXISTS Blood_Units CASCADE;

-- Create only tables that don't exist
DO $$
BEGIN
    -- Blood Types Table
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'blood_types') THEN
        CREATE TABLE Blood_Types (
            blood_type_id SERIAL PRIMARY KEY,
            type_name VARCHAR(5) NOT NULL UNIQUE
        );
        
        -- Insert default blood types
        INSERT INTO Blood_Types (type_name) VALUES 
            ('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-'), ('O+'), ('O-');
    END IF;
    
    -- Insert sample receivers if the receivers table exists but is empty
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'receivers') AND 
       NOT EXISTS (SELECT 1 FROM Receivers LIMIT 1) THEN
        INSERT INTO Receivers 
            (first_name, last_name, dob, gender, blood_type_id, reason_for_transfusion, 
             hospital_name, ward_details, contact_person_name, contact_person_phone)
        VALUES 
            ('Ahmed', 'Khan', '1985-05-15', 'Male', 1, 'Surgery recovery', 'City Hospital', 
             'Surgery Ward - Room 302', 'Fatima Khan', '+92-300-1234567'),
            ('Sara', 'Ali', '1990-08-22', 'Female', 3, 'Childbirth complications', 'Maternity Hospital', 
             'Maternity Ward - Room 105', 'Adil Ali', '+92-333-7654321'),
            ('Malik', 'Aslam', '1975-11-03', 'Male', 7, 'Accident injuries', 'Emergency Care Center', 
             'ICU - Bed 7', 'Nasreen Aslam', '+92-321-9876543'),
            ('Ayesha', 'Tariq', '1988-02-28', 'Female', 5, 'Anemia treatment', 'General Hospital', 
             'Medical Ward - Room 210', 'Tariq Ahmed', '+92-345-8765432'),
            ('Hassan', 'Mahmood', '1965-07-12', 'Male', 8, 'Heart surgery', 'Cardiac Center', 
             'Cardiac Ward - Room 401', 'Samina Mahmood', '+92-312-3456789');
    END IF;
    
    -- Donors Table
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'donors') THEN
        CREATE TABLE Donors (
            donor_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            dob DATE NOT NULL,
            gender VARCHAR(10) NOT NULL,
            blood_type_id INTEGER NOT NULL REFERENCES Blood_Types(blood_type_id),
            phone_number VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            address TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_donation_date DATE
        );
    END IF;
    
    -- Receivers Table
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'receivers') THEN
        CREATE TABLE Receivers (
            receiver_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            dob DATE NOT NULL,
            gender VARCHAR(10) NOT NULL,
            blood_type_id INTEGER NOT NULL REFERENCES Blood_Types(blood_type_id),
            reason_for_transfusion TEXT NOT NULL,
            hospital_name VARCHAR(100) NOT NULL,
            ward_details VARCHAR(100),
            contact_person_name VARCHAR(100) NOT NULL,
            contact_person_phone VARCHAR(20) NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;    -- Blood Units Table has been removed

    -- Blood Requests Table
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'blood_requests') THEN
        CREATE TABLE Blood_Requests (
            request_id SERIAL PRIMARY KEY,
            receiver_id INTEGER REFERENCES Receivers(receiver_id),
            blood_type_id INTEGER NOT NULL REFERENCES Blood_Types(blood_type_id),
            units_required INTEGER NOT NULL,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority VARCHAR(20) NOT NULL DEFAULT 'Normal',
            status VARCHAR(20) NOT NULL DEFAULT 'Pending',
            notes TEXT
        );
    END IF;    -- Blood Request Units (mapping between requests and assigned units) has been removed

    -- Medical Conditions (for donors)
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'medical_conditions') THEN
        CREATE TABLE Medical_Conditions (
            condition_id SERIAL PRIMARY KEY,
            donor_id INTEGER REFERENCES Donors(donor_id),
            condition_name VARCHAR(100) NOT NULL,
            diagnosis_date DATE,
            notes TEXT,
            affects_donation BOOLEAN DEFAULT FALSE
        );
    END IF;
END
$$;
