# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based diabetes prediction web application that uses machine learning to predict diabetes risk and provides role-based access for patients, doctors, and administrators.

## Architecture

### Core Components
- **app.py**: Main Flask application with all routes, authentication, and business logic
- **train_model.py**: ML model training script using scikit-learn LogisticRegression
- **diabetes.csv**: PIMA Indian Diabetes Dataset for training
- **diabetes_model.pkl & scaler.pkl**: Serialized ML model and feature scaler
- **diabetes.db**: SQLite database for user data and predictions
- **templates/**: HTML templates for all pages (14 templates including base.html)

### Database Schema
- **users**: User accounts with roles (patient/doctor), email, password hash, reset tokens
- **patients**: Prediction records with medical data and results
- **admin_logs**: Administrative action audit trail

### User Roles
- **Patient**: Can submit predictions, view history, share reports via email
- **Doctor**: Can view all patient records, search patients, access analytics dashboard
- **Admin**: Can manage users, view system statistics, delete accounts

### ML Pipeline
1. Features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
2. Preprocessing: StandardScaler normalization
3. Model: LogisticRegression with max_iter=500
4. Risk categorization: Normal, Pre-Diabetic, Type 1/2 Diabetes based on glucose and BMI thresholds

## Development Commands

### Running the Application
```bash
python3 app.py
```
- Starts Flask development server on localhost:5000
- Database is auto-initialized on first run

### Training ML Model
```bash
python3 train_model.py
```
- Requires diabetes.csv dataset
- Generates diabetes_model.pkl and scaler.pkl files
- Must run before starting the application

### Dependencies
This project uses standard Python libraries:
- Flask (web framework)
- scikit-learn (ML)
- pandas (data processing)
- sqlite3 (database)
- reportlab (PDF generation)
- joblib (model serialization)

Install missing packages with:
```bash
pip3 install flask scikit-learn pandas reportlab
```

## Configuration

### Security Settings (app.py lines 20-31)
- Flask secret key (change in production)
- Doctor registration secret key: "HEALTH2025"
- Admin credentials: admin/admin123 (change in production)
- Email SMTP configuration (requires setup for email features)

### File Dependencies
- ML model files (diabetes_model.pkl, scaler.pkl) must exist before predictions
- Application gracefully handles missing model files but disables prediction functionality
- SQLite database is created automatically if missing

## Key Features
- User authentication with password reset via email
- PDF report generation and email sharing
- Multi-role dashboard with different access levels
- Real-time diabetes risk assessment with staged recommendations
- Admin panel with user management and audit logs