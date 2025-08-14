-- FinRisk Database Initialization Script
-- PostgreSQL schema for credit risk assessment and fraud detection

-- Create MLflow database
CREATE DATABASE mlflow_db;

-- Connect to main database
\c finrisk_db;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS finrisk;
CREATE SCHEMA IF NOT EXISTS mlflow;

-- Customer profiles table
CREATE TABLE finrisk.customer_profiles (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    date_of_birth DATE,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    postcode VARCHAR(10),
    employment_status VARCHAR(50),
    annual_income DECIMAL(12,2),
    credit_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit applications table
CREATE TABLE finrisk.credit_applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(50) REFERENCES finrisk.customer_profiles(customer_id),
    loan_amount DECIMAL(12,2) NOT NULL,
    loan_purpose VARCHAR(100),
    term_months INTEGER,
    debt_to_income_ratio DECIMAL(5,4),
    risk_score INTEGER,
    decision VARCHAR(20),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    model_version VARCHAR(50)
);

-- Credit bureau data table
CREATE TABLE finrisk.credit_bureau_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(50) REFERENCES finrisk.customer_profiles(customer_id),
    credit_score INTEGER,
    payment_history VARCHAR(100),
    credit_utilization DECIMAL(5,4),
    length_of_credit INTEGER,
    number_of_accounts INTEGER,
    derogatory_marks INTEGER,
    inquiries_last_6_months INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction data table
CREATE TABLE finrisk.transaction_data (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(50) REFERENCES finrisk.customer_profiles(customer_id),
    amount DECIMAL(12,2) NOT NULL,
    merchant_category VARCHAR(100),
    merchant_name VARCHAR(255),
    location VARCHAR(255),
    device_info VARCHAR(100),
    ip_address INET,
    fraud_probability DECIMAL(5,4),
    fraud_decision VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model predictions table
CREATE TABLE finrisk.model_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_type VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) REFERENCES finrisk.customer_profiles(customer_id),
    application_id UUID REFERENCES finrisk.credit_applications(application_id),
    transaction_id UUID REFERENCES finrisk.transaction_data(transaction_id),
    prediction_value DECIMAL(5,4),
    prediction_label VARCHAR(50),
    confidence_score DECIMAL(5,4),
    model_version VARCHAR(50),
    features JSONB,
    shap_values JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model performance tracking
CREATE TABLE finrisk.model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_type VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,6),
    dataset_type VARCHAR(20),
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data drift monitoring
CREATE TABLE finrisk.data_drift (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_name VARCHAR(100) NOT NULL,
    drift_score DECIMAL(5,4),
    p_value DECIMAL(10,6),
    reference_mean DECIMAL(10,6),
    current_mean DECIMAL(10,6),
    reference_std DECIMAL(10,6),
    current_std DECIMAL(10,6),
    drift_detected BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE finrisk.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id VARCHAR(50),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_customer_profiles_email ON finrisk.customer_profiles(email);
CREATE INDEX idx_credit_applications_customer_id ON finrisk.credit_applications(customer_id);
CREATE INDEX idx_credit_applications_created_at ON finrisk.credit_applications(created_at);
CREATE INDEX idx_transaction_data_customer_id ON finrisk.transaction_data(customer_id);
CREATE INDEX idx_transaction_data_created_at ON finrisk.transaction_data(created_at);
CREATE INDEX idx_model_predictions_model_type ON finrisk.model_predictions(model_type);
CREATE INDEX idx_model_predictions_created_at ON finrisk.model_predictions(created_at);
CREATE INDEX idx_data_drift_feature_name ON finrisk.data_drift(feature_name);
CREATE INDEX idx_data_drift_created_at ON finrisk.data_drift(created_at);

-- Create views for common queries
CREATE VIEW finrisk.credit_risk_summary AS
SELECT 
    cp.customer_id,
    cp.first_name,
    cp.last_name,
    cp.credit_score,
    cp.annual_income,
    COUNT(ca.application_id) as total_applications,
    AVG(ca.risk_score) as avg_risk_score,
    MAX(ca.created_at) as last_application_date
FROM finrisk.customer_profiles cp
LEFT JOIN finrisk.credit_applications ca ON cp.customer_id = ca.customer_id
GROUP BY cp.customer_id, cp.first_name, cp.last_name, cp.credit_score, cp.annual_income;

CREATE VIEW finrisk.fraud_risk_summary AS
SELECT 
    cp.customer_id,
    cp.first_name,
    cp.last_name,
    COUNT(td.transaction_id) as total_transactions,
    AVG(td.fraud_probability) as avg_fraud_probability,
    COUNT(CASE WHEN td.fraud_decision = 'BLOCK' THEN 1 END) as blocked_transactions,
    MAX(td.created_at) as last_transaction_date
FROM finrisk.customer_profiles cp
LEFT JOIN finrisk.transaction_data td ON cp.customer_id = td.customer_id
GROUP BY cp.customer_id, cp.first_name, cp.last_name;

-- Insert sample data for testing
INSERT INTO finrisk.customer_profiles (customer_id, first_name, last_name, email, phone, date_of_birth, address_line1, city, postcode, employment_status, annual_income, credit_score) VALUES
('CUST_001', 'John', 'Smith', 'john.smith@email.com', '+44123456789', '1985-03-15', '123 High Street', 'London', 'SW1A 1AA', 'Full-time', 45000.00, 720),
('CUST_002', 'Sarah', 'Johnson', 'sarah.johnson@email.com', '+44123456790', '1990-07-22', '456 Oak Avenue', 'Manchester', 'M1 1AA', 'Full-time', 38000.00, 680),
('CUST_003', 'Michael', 'Brown', 'michael.brown@email.com', '+44123456791', '1982-11-08', '789 Pine Road', 'Birmingham', 'B1 1AA', 'Self-employed', 52000.00, 750);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE finrisk_db TO finrisk;
GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO finrisk;
GRANT ALL PRIVILEGES ON SCHEMA finrisk TO finrisk;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA finrisk TO finrisk;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA finrisk TO finrisk;
