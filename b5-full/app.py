from flask import Flask, render_template, request, redirect, session, url_for, make_response, flash, jsonify
import sqlite3
import joblib
import numpy as np
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Translations
translations = {
    "en": {
        "app_name": "Diabetes Health App",
        "login": "Login",
        "register": "Register",
        "home": "Home",
        "dashboard": "Dashboard",
        "logout": "Logout",
        "welcome": "Welcome",
        "history": "History",
        "submit": "Submit",
        "result": "Result",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "role": "Role",
        "patient": "Patient",
        "doctor": "Doctor",
        "admin": "Admin",
        "predict_diabetes": "Predict Diabetes",
        "pregnancies": "Pregnancies",
        "glucose": "Glucose",
        "blood_pressure": "Blood Pressure",
        "skin_thickness": "Skin Thickness",
        "insulin": "Insulin",
        "bmi": "BMI",
        "dpf": "Diabetes Pedigree Function",
        "age": "Age",
        "predict": "Predict",
        "reset": "Reset",
        "cancel": "Cancel",
        "status": "Status",
        "actions": "Actions",
        "date": "Date",
        "view": "View",
        "delete": "Delete",
        "search": "Search",
        "show": "Show",
        "entries": "entries",
        "previous": "Previous",
        "next": "Next",
        "copyright": "© 2025 Diabetes Health App. All rights reserved.",
        "enter_username": "Enter Username",
        "enter_email": "Enter Email",
        "enter_password": "Enter Password",
        "generated_report": "Generated Report",
        "diagnosis": "Diagnosis",
        "suggestion": "Suggestion",
        "back_to_dashboard": "Back to Dashboard",
        "print_report": "Print Report",
        "email_report": "Email Report",
        "risk_stage": "Risk Stage",
        "normal": "Normal",
        "pre_diabetic": "Pre-Diabetic",
        "type_1": "Type 1 Diabetes",
        "type_2": "Type 2 Diabetes",
        "forgot_password": "Forgot Password?",
        "dont_have_account": "Don't have an account?",
        "already_have_account": "Already have an account?",
        "click_here": "Click here",
        "verify_email": "Verify Email",
        "sign_in_text": "Sign in to access your dashboard",
        "create_account": "Create Account",
        "admin_portal": "Admin Portal",
        "doctor_portal": "Doctor Portal",
        "patient_portal": "Patient Portal",
        "secret_key": "Secret Key",
        "enter_secret_key": "Enter Doctor Secret Key",
        "total_tests": "Total Tests",
        "avg_glucose": "Average Glucose",
        "avg_bmi": "Average BMI",
        "avg_bp": "Average BP",
        "health_trends": "Health Trends Over Time",
        "last_5_tests": "Last 5 Tests",
        "export_csv": "Export CSV",
        "search_placeholder": "Search by name, email...",
        "no_records": "No records found",
        "showing": "Showing",
        "of": "of",
        "features": "Features",
        "about": "About",
        "how_it_works": "How It Works",
        "get_started": "Get Started",
        "start_free_analysis": "Start Free Analysis",
        "learn_more": "Learn More",
        "ai_powered_analytics": "AI-Powered Health Analytics",
        "landing_hero_title": "Predict Diabetes Risk",
        "landing_hero_subtitle": "Before It's Too Late",
        "landing_hero_short": "Multi-Model AI System • 75% Ensemble Accuracy • Instant Results",
        "welcome_prediction": "Welcome to Diabetes Prediction",
        "fill_details": "Fill in your health details to predict your diabetes risk.",
        "name": "Name",
        "tooltip_age": "Your current age in years",
        "tooltip_pregnancies": "Number of times pregnant (0 if male or never pregnant)",
        "tooltip_glucose": "Blood glucose concentration (Normal: 70-100 mg/dL fasting, <140 mg/dL after meals)",
        "tooltip_bp": "Diastolic blood pressure (Normal: 60-80 mmHg, Ideal: <80 mmHg)",
        "welcome_prediction": "Welcome to Diabetes Prediction",
        "fill_details": "Fill in your health details to predict your diabetes risk.",
        "name": "Name",
        "tooltip_age": "Your current age in years",
        "tooltip_pregnancies": "Number of times pregnant (0 if male or never pregnant)",
        "tooltip_glucose": "Blood glucose concentration (Normal: 70-100 mg/dL fasting, <140 mg/dL after meals)",
        "tooltip_bp": "Diastolic blood pressure (Normal: 60-80 mmHg, Ideal: <80 mmHg)",
        "tooltip_skin": "Triceps skin fold thickness in mm (Normal range: 10-50 mm)",
        "tooltip_insulin": "2-Hour serum insulin level (Normal: 16-166 µU/mL)",
        "tooltip_bmi": "Body Mass Index = weight(kg) / height(m)² (Normal: 18.5-24.9, Overweight: 25-29.9, Obese: ≥30)",
        "tooltip_dpf": "Genetic factor showing diabetes likelihood based on family history",
        "welcome_back": "Welcome Back",
        "login_subtitle": "Login to access your health insights",
        "username_or_email": "Username or Email",
        "login_action": "Login to Account",
        "logging_in": "Logging in...",
        "join_platform": "Join our AI-powered health platform",
        "password_min_8": "Password (min 8 characters)",
        "select_account_type": "Select Account Type",
        "health_predictions": "Health predictions & insights",
        "healthcare_pro": "Healthcare Pro",
        "patient_analytics": "Patient analytics dashboard",
        "doctor_verification_key": "Doctor Verification Key",
        "key_required_note": "Required for healthcare professional registration (Key: HEALTH2025)",
        "creating_account": "Creating Account...",
        "login_here": "Login Here",
        "create_new_account": "Create New Account",
        "prediction_results": "Prediction Results",
        "prediction_result": "Prediction Result",
        "health_stage": "Health Stage",
        "multi_model_analysis": "Multi-Model AI Analysis",
        "model_agreement": "Model Agreement",
        "prediction_label": "Prediction",
        "final_prediction_note": "Final prediction is based on ensemble voting from all three models",
        "personalized_recommendations": "Personalized Recommendations",
        "download_pdf_report": "Download PDF Report",
        "share_email": "Share via Email",
        "view_history": "View History",
        "new_test": "New Test",
        "medical_disclaimer": "Medical Disclaimer",
        "disclaimer_text": "This prediction is for informational purposes only and should not replace professional medical advice.",
        "share_modal_title": "Share Medical Report via Email",
        "recipient_email": "Recipient Email Address",
        "report_includes_note": "The complete PDF report will be sent to this email address",
        "report_contents": "Report Contents",
        "final_result": "Final Result",
        "ai_analysis": "AI Analysis",
        "multi_model_report_includes": "Multi-Model AI Report Includes",
        "indiv_predictions": "Individual predictions from 3 AI models",
        "conf_scores": "Confidence scores for each model",
        "model_agreement_indicators": "Model agreement indicators",
        "health_recs": "Personalized health recommendations",
        "privacy_notice": "Privacy Notice",
        "privacy_text": "This report contains sensitive health information.",
        "send_report_now": "Send Report Now",
        "cancel": "Cancel",
        "your_medical_history": "Your Medical History",
        "no_records_found": "No Medical Records Found",
        "take_first_test": "Take Your First Test",
        "recent_health_metrics": "Recent Health Metrics Trend",
        "admin_dashboard": "Admin Dashboard",
        "system_overview": "System Overview & User Management",
        "total_users": "Total Users",
        "healthcare_professionals": "Healthcare Professionals",
        "total_predictions": "Total Predictions",
        "recent_users": "Recent Users",
        "registered": "Registered",
        "admin_activity_log": "Admin Activity Log",
        "admin_user": "Admin User",
        "action": "Action",
        "target_user": "Target User",
        "quick_actions": "Quick Actions",
        "main_site": "Main Site",
        "refresh_data": "Refresh Data",
        "export_data": "Export Data",
        "privacy_notice_history": "You can only view your own medical records for security and privacy.",
        "patient_name": "Patient Name",
        "doctor_dashboard": "Doctor Dashboard",
        "analytics_patients": "Analytics of all registered patients",
        "total_patients": "Total Patients",
        "diabetic": "Diabetic",
        "non_diabetic": "Non-Diabetic",
        "avg_glucose_bmi": "Avg Glucose / BMI",
        "patient_records": "Patient Records",
        "showing_records": "Showing records",
        "export_csv": "Export CSV",
        "search_placeholder": "Search by name, username, result, or stage",
        "search_button": "Search",
        "clear": "Clear",
        "search_results": "Search Results",
        "found_patients": "Found patient(s)",
        "prev": "Previous",
        "next": "Next",
        "page_of": "Page of",
        "total_records_text": "total records",
        "landing_hero_long": "Harness cutting-edge artificial intelligence with our 3-model ensemble system to assess your diabetes risk in seconds. Our clinically-validated AI combines Logistic Regression, Random Forest, and XGBoost to analyze 8 key health parameters, providing personalized insights, model agreement indicators, and actionable recommendations for a healthier future.",
        "landing_context_title": "Why Diabetes Prediction Matters",
        "landing_context_subtitle": "Understanding the global diabetes crisis and how AI is changing prevention",
        "context_epidemic_title": "The Diabetes Epidemic",
        "context_epidemic_text": "Over 463 million adults worldwide live with diabetes, and this number is expected to reach 700 million by 2045. What's more alarming? Nearly 50% of people with diabetes are undiagnosed, silently suffering from a condition that can lead to heart disease, kidney failure, blindness, and limb amputation. Early detection is the key to prevention and better outcomes.",
        "context_prevention_title": "Prevention Saves Lives",
        "context_prevention_text": "Studies show that lifestyle changes can reduce diabetes risk by up to 58% in high-risk individuals. But you can't prevent what you don't know about. Our AI-powered tool provides instant risk assessment based on the PIMA Indian Diabetes Dataset — a gold-standard medical dataset used in over 10,000 research studies. Know your risk today, change your life tomorrow.",
        "context_how_works_title": "How Our Multi-Model AI Works",
        "context_how_works_text": "Our advanced system combines 3 powerful AI models — Logistic Regression, Random Forest, and XGBoost — trained on 768 clinical records with 8 critical health parameters: glucose levels, BMI, blood pressure, insulin, age, pregnancy history, skin thickness, and genetic factors. Using ensemble voting, the system achieves 75.3% prediction accuracy with model agreement indicators for enhanced reliability.",
        "context_validated_title": "Clinically Validated",
        "context_validated_text": "Built on the renowned PIMA Indian Diabetes Dataset from the National Institute of Diabetes and Digestive and Kidney Diseases. Our predictions classify risk into 4 stages: Normal, Pre-Diabetic, Type 1, and Type 2 Diabetes — each with personalized health recommendations.",
        "context_privacy_title": "Your Privacy, Guaranteed",
        "context_privacy_text": "Your health data is encrypted, secure, and never sold. We follow strict HIPAA-compliant security protocols. All predictions are processed locally, and you have full control over your data — view history, download reports, or delete anytime.",
        "stats_accuracy": "% Ensemble Accuracy",
        "stats_people": "Million People with Diabetes",
        "stats_risk_reduction": "% Risk Reduction Possible",
        "stats_params": "Health Parameters Analyzed",
        "features_title": "Powerful Features for Better Health",
        "features_subtitle": "Everything you need for comprehensive diabetes risk assessment",
        "feature_ensemble_title": "3-Model AI Ensemble",
        "feature_ensemble_desc": "Logistic Regression, Random Forest, and XGBoost work together with majority voting. See individual model predictions, confidence scores, and agreement indicators for transparent, reliable results.",
        "feature_instant_title": "Instant Predictions",
        "feature_instant_desc": "Get AI-powered diabetes risk assessment in under 3 seconds. No waiting, no appointments — just instant, actionable insights powered by machine learning.",
        "feature_trends_title": "Health Trends & Analytics",
        "feature_trends_desc": "Track your health journey over time with beautiful visualizations. Monitor glucose, BMI, and blood pressure trends to see how lifestyle changes impact your risk.",
        "feature_pdf_title": "Detailed PDF Reports",
        "feature_pdf_desc": "Download professional health reports with multi-model AI analysis, stage classification, and personalized recommendations to share with your doctor.",
        "feature_email_title": "Email Report Sharing",
        "feature_email_desc": "Instantly share your comprehensive health reports via email with doctors or family members. Includes all 3 model predictions, confidence scores, and medical recommendations.",
        "feature_stages_title": "4-Stage Risk Classification",
        "feature_stages_desc": "Precise classification into Normal, Pre-Diabetic, Type 1, or Type 2 Diabetes with specific health recommendations tailored to each risk level.",
        "feature_doctor_title": "Doctor Dashboard",
        "feature_doctor_desc": "Healthcare professionals get advanced analytics, patient search, pagination, CSV exports, and comprehensive patient management tools.",
        "feature_security_title": "Bank-Level Security",
        "feature_security_desc": "Your data is protected with enterprise-grade encryption, secure authentication, and HIPAA-compliant privacy standards. Your health, your control.",
        "how_it_works_title": "How It Works",
        "how_it_works_subtitle": "Get your diabetes risk assessment in 3 simple steps",
        "step_1_title": "Enter Your Health Data",
        "step_1_desc": "Register for free and input 8 key health parameters: age, glucose level, BMI, blood pressure, insulin, pregnancy history, skin thickness, and diabetes pedigree function. Each field includes helpful guidance and validation to ensure accurate predictions.",
        "step_2_title": "Multi-Model AI Analyzes Your Risk",
        "step_2_desc": "Our advanced 3-model ensemble system — trained on 768 clinical records — instantly processes your data through Logistic Regression, Random Forest, and XGBoost algorithms with StandardScaler normalization. Each model provides independent predictions with confidence scores, and the final result uses majority voting for maximum reliability, achieving 75.3% ensemble accuracy with model agreement indicators.",
        "step_3_title": "Receive Actionable Insights",
        "step_3_desc": "Get instant results with your risk classification (Normal, Pre-Diabetic, Type 1, or Type 2), personalized health recommendations, trend analysis, and downloadable PDF reports. Share with your doctor or track your progress over time.",
        "footer_desc": "Empowering healthier lives through artificial intelligence and early detection.",
        "footer_dataset": "Built on the PIMA Indian Diabetes Dataset\nResearch-backed • Clinically validated • Privacy-first",
        "footer_rights": "2025 DiabetesAI. All rights reserved.",
        "footer_dev": "Developed with ❤️ for better healthcare",
        "footer_disclaimer": "This tool is for educational purposes and should not replace professional medical advice.",
        "admin_portal": "Admin Portal",
        "medical_history_title": "Your Medical History",
        "stage_label": "Stage",
        "model_lr": "Logistic Regression",
        "model_rf": "Random Forest",
        "model_xgb": "XGBoost",
        "agree_all": "All Models Agree (100%)",
        "agree_majority": "Majority Consensus (67%)",
        "models_ensemble": "3 Models + Ensemble",
        "final_diagnosis": "Final Diagnosis",
        "privacy_warning": "Only share with trusted healthcare providers or authorized family members.",
        "rec_maintain_diet": "Maintain healthy diet",
        "rec_exercise_30": "Exercise 30 min daily",
        "rec_annual_checkup": "Annual checkup",
        "rec_reduce_sugar": "Reduce sugar",
        "rec_exercise_5": "Exercise 5 days/week",
        "rec_monitor_3": "Monitor glucose 3 months",
        "rec_consult_insulin": "Consult doctor for insulin",
        "rec_monitor_glucose": "Blood glucose monitoring",
        "rec_balanced_meals": "Balanced meals",
        "rec_medication": "Strict medication & diet",
        "rec_weight": "Weight management",
        "rec_consult": "Consult doctor",
        "health_trends_title": "Your Health Trends",
        "privacy_notice_history": "Privacy Notice: You can only view your own medical records for security and privacy.",
        "years": "years"
    },
    "kn": {
        "app_name": "ಮಧುಮೇಹ ಆರೋಗ್ಯ ಅಪ್ಲಿಕೇಶನ್",
        "login": "ಲಾಗಿನ್",
        "register": "ನೋಂದಣಿ",
        "home": "ಮುಖಪುಟ",
        "dashboard": "ಡ್ಯಾಶ್ಬೋರ್ಡ್",
        "logout": "ಲಾಗೌಟ್",
        "welcome": "ಸ್ವಾಗತ",
        "submit": "ಸಲ್ಲಿಸಿ",
        "predicting": "ಊಹಿಸಲಾಗುತ್ತಿದೆ...",
        "result": "ಫಲಿತಾಂಶ",
        "accuracy": "ನಿಖರತೆ",
        "history": "ಇತಿಹಾಸ",
        "username": "ಬಳಕೆದಾರರ ಹೆಸರು",
        "email": "ಇಮೇಲ್",
        "password": "ಪಾಸ್‌ವರ್ಡ್",
        "confirm_password": "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
        "role": "ಪಾತ್ರ",
        "patient": "ರೋಗಿ",
        "doctor": "ವೈದ್ಯರು",
        "admin": "ನಿರ್ವಾಹಕರು",
        "predict_diabetes": "ಮಧುಮೇಹ ಮುನ್ಸೂಚನೆ",
        "pregnancies": "ಗರ್ಭಧಾರಣೆಗಳು",
        "glucose": "ಗ್ಲೂಕೋಸ್",
        "blood_pressure": "ರಕ್ತದೊತ್ತಡ",
        "skin_thickness": "ಚರ್ಮದ ದಪ್ಪ",
        "insulin": "ಇನ್ಸುಲಿನ್",
        "bmi": "ಬಿಎಂಐ",
        "dpf": "ಮಧುಮೇಹ ವಂಶಾವಳಿ ಕಾರ್ಯ",
        "age": "ವಯಸ್ಸು",
        "predict": "ಊಹಿಸಿ",
        "reset": "ಮರುಹೊಂದಿಸಿ",
        "cancel": "ರದ್ದುಮಾಡಿ",
        "status": "ಸ್ಥಿತಿ",
        "actions": "ಕ್ರಮಗಳು",
        "date": "ದಿನಾಂಕ",
        "view": "ವೀಕ್ಷಿಸಿ",
        "delete": "ಅಳಿಸಿ",
        "search": "ಹುಡುಕಿ",
        "show": "ತೋರಿಸಿ",
        "entries": "ನಮೂದುಗಳು",
        "previous": "ಹಿಂದಿನ",
        "next": "ಮುಂದಿನ",
        "copyright": "© 2025 ಮಧುಮೇಹ ಆರೋಗ್ಯ ಅಪ್ಲಿಕೇಶನ್. ಎಲ್ಲಾ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ.",
        "enter_username": "ಬಳಕೆದಾರರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ",
        "enter_email": "ಇಮೇಲ್ ನಮೂದಿಸಿ",
        "enter_password": "ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ",
        "generated_report": "ರಚಿಸಿದ ವರದಿ",
        "diagnosis": "ರೋಗನಿರ್ಣಯ",
        "suggestion": "ಸಲಹೆ",
        "back_to_dashboard": "ಡ್ಯಾಶ್ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",
        "print_report": "ವರದಿಯನ್ನು ಮುದ್ರಿಸಿ",
        "email_report": "ವರದಿಯನ್ನು ಇಮೇಲ್ ಮಾಡಿ",
        "risk_stage": "ಅಪಾಯದ ಹಂತ",
        "normal": "ಸಾಮಾನ್ಯ",
        "pre_diabetic": "ಪೂರ್ವ-ಮಧುಮೇಹ",
        "type_1": "ಟೈಪ್ 1 ಮಧುಮೇಹ",
        "type_2": "ಟೈಪ್ 2 ಮಧುಮೇಹ",
        "forgot_password": "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?",
        "dont_have_account": "ಖಾತೆ ಇಲ್ಲವೇ?",
        "already_have_account": "ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?",
        "click_here": "ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ",
        "verify_email": "ಇಮೇಲ್ ಪರಿಶೀಲಿಸಿ",
        "sign_in_text": "ನಿಮ್ಮ ಡ್ಯಾಶ್ಬೋರ್ಡ್ ಪ್ರವೇಶಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ",
        "create_account": "ಖಾತೆ ತೆರೆಯಿರಿ",
        "admin_portal": "ನಿರ್ವಾಹಕ ಪೋರ್ಟಲ್",
        "doctor_portal": "ವೈದ್ಯರ ಪೋರ್ಟಲ್",
        "patient_portal": "ರೋಗಿಗಳ ಪೋರ್ಟಲ್",
        "secret_key": "ಗೌಪ್ಯ ಕೀ",
        "enter_secret_key": "ವೈದ್ಯರ ಗೌಪ್ಯ ಕೀಲಿಯನ್ನು ನಮೂದಿಸಿ",
        "total_tests": "ಒಟ್ಟು ಪರೀಕ್ಷೆಗಳು",
        "avg_glucose": "ಸರಾಸರಿ ಗ್ಲೂಕೋಸ್",
        "avg_bmi": "ಸರಾಸರಿ ಬಿಎಂಐ",
        "avg_bp": "ಸರಾಸರಿ ರಕ್ತದೊತ್ತಡ",
        "health_trends": "ಆರೋಗ್ಯ ಪ್ರವೃತ್ತಿಗಳು",
        "last_5_tests": "ಕೊನೆಯ 5 ಪರೀಕ್ಷೆಗಳು",
        "export_csv": "CSV ರಫ್ತು ಮಾಡಿ",
        "search_placeholder": "ಹೆಸರು, ಇಮೇಲ್ ಮೂಲಕ ಹುಡುಕಿ...",
        "no_records": "ಯಾವುದೇ ದಾಖಲೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        "showing": "ತೋರಿಸಲಾಗುತ್ತಿದೆ",
        "of": "ರಲ್ಲಿ",
        "features": "ವೈಶಿಷ್ಟ್ಯಗಳು",
        "about": "ಬಗ್ಗೆ",
        "how_it_works": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
        "get_started": "ಪ್ರಾರಂಭಿಸಿ",
        "start_free_analysis": "ಉಚಿತ ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
        "learn_more": "ಇನ್ನಷ್ಟು ತಿಳಿಯಿರಿ",
        "ai_powered_analytics": "ಎಐ-ಚಾಲಿತ ಆರೋಗ್ಯ ವಿಶ್ಲೇಷಣೆ",
        "landing_hero_title": "ಮಧುಮೇಹ ಅಪಾಯವನ್ನು ಊಹಿಸಿ",
        "landing_hero_subtitle": "ತುಂಬಾ ತಡವಾಗುವ ಮೊದಲು",
        "landing_hero_short": "ಬಹು-ಮಾದರಿ ಎಐ ವ್ಯವಸ್ಥೆ • 75% ನಿಖರತೆ • ತಕ್ಷಣದ ಫಲಿತಾಂಶಗಳು",
        "landing_hero_long": "ಸೆಕೆಂಡುಗಳಲ್ಲಿ ನಿಮ್ಮ ಮಧುಮೇಹದ ಅಪಾಯವನ್ನು ನಿರ್ಣಯಿಸಲು ನಮ್ಮ 3-ಮಾದರಿ ಸಮೂಹ ವ್ಯವಸ್ಥೆಯೊಂದಿಗೆ ಅತ್ಯಾಧುನಿಕ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯನ್ನು ಬಳಸಿಕೊಳ್ಳಿ. ನಮ್ಮ ಪ್ರಾಯೋಗಿಕವಾಗಿ ಮೌಲ್ಯೀಕರಿಸಿದ ಎಐ ಲಾಜಿಸ್ಟಿಕ್ ರಿಗ್ರೆಶನ್, ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಮತ್ತು ಎಕ್ಸ್‌ಜಿಬೂಸ್ಟ್ ಅನ್ನು ಸಂಯೋಜಿಸಿ 8 ಪ್ರಮುಖ ಆರೋಗ್ಯ ನಿಯತಾಂಕಗಳನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ, ವೈಯಕ್ತೀಕರಿಸಿದ ಒಳನೋಟಗಳು, ಮಾದರಿ ಒಪ್ಪಂದದ ಸೂಚಕಗಳು ಮತ್ತು ಆರೋಗ್ಯಕರ ಭವಿಷ್ಯಕ್ಕಾಗಿ ಕ್ರಿಯಾಾತ್ಮಕ ಶಿಫಾರಸುಗಳನ್ನು ನೀಡುತ್ತದೆ.",
        "welcome_prediction": "ಮಧುಮೇಹ ಮುನ್ಸೂಚನೆಗೆ ಸ್ವಾಗತ",
        "fill_details": "ನಿಮ್ಮ ಮಧುಮೇಹ ಅಪಾಯವನ್ನು ಊಹಿಸಲು ನಿಮ್ಮ ಆರೋಗ್ಯ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.",
        "name": "ಹೆಸರು",
        "tooltip_age": "ವರ್ಷಗಳಲ್ಲಿ ನಿಮ್ಮ ಪ್ರಸ್ತುತ ವಯಸ್ಸು",
        "tooltip_pregnancies": "ಗರ್ಭಿಣಿಯಾದ ಬಾರಿ (ಪುರುಷರಾಗಿದ್ದರೆ ಅಥವಾ ಗರ್ಭಿಣಿಯಾಗದಿದ್ದರೆ 0)",
        "tooltip_glucose": "ರಕ್ತದ ಗ್ಲೂಕೋಸ್ ಸಾಂದ್ರತೆ (ಸಾಮಾನ್ಯ: 70-100 mg/dL ಉಪವಾಸ, <140 mg/dL ಊಟದ ನಂತರ)",
        "tooltip_bp": "ಡಯಾಸ್ಟೊಲಿಕ್ ರಕ್ತದೊತ್ತಡ (ಸಾಮಾನ್ಯ: 60-80 mmHg, ಆದರ್ಶ: <80 mmHg)",
        "tooltip_skin": "ಟ್ರೈಸ್ಪ್ಸ್ ಚರ್ಮದ ಮಡಿಕೆ ದಪ್ಪ ಮಿಮೀ (ಸಾಮಾನ್ಯ ಶ್ರೇಣಿ: 10-50 ಮಿಮೀ)",
        "tooltip_insulin": "2-ಗಂಟೆಗಳ ಸೀರಮ್ ಇನ್ಸುಲಿನ್ ಮಟ್ಟ (ಸಾಮಾನ್ಯ: 16-166 µU/mL)",
        "tooltip_bmi": "ದೇಹದ ದ್ರವ್ಯರಾಶಿ ಸೂಚ್ಯಂಕ = ತೂಕ(kg) / ಎತ್ತರ(m)² (ಸಾಮಾನ್ಯ: 18.5-24.9)",
        "tooltip_dpf": "ಕುಟುಂಬದ ಇತಿಹಾಸದ ಆಧಾರದ ಮೇಲೆ ಮಧುಮೇಹದ ಸಾಧ್ಯತೆಯನ್ನು ತೋರಿಸುವ ಆನುವಂಶಿಕ ಅಂಶ",
        "welcome_back": "ಮತ್ತೆ ಸುಸ್ವಾಗತ",
        "login_subtitle": "ನಿಮ್ಮ ಆರೋಗ್ಯದ ಒಳನೋಟಗಳನ್ನು ಪಡೆಯಲು ಲಾಗಿನ್ ಮಾಡಿ",
        "username_or_email": "ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಇಮೇಲ್",
        "login_action": "ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ",
        "logging_in": "ಲಾಗಿನ್ ಆಗುತ್ತಿದೆ...",
        "join_platform": "ನಮ್ಮ AI- ಚಾಲಿತ ಆರೋಗ್ಯ ವೇದಿಕೆಗೆ ಸೇರಿ",
        "password_min_8": "ಪಾಸ್‌ವರ್ಡ್ (ಕನಿಷ್ಠ 8 ಅಕ್ಷರಗಳು)",
        "select_account_type": "ಖಾತೆ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "health_predictions": "ಆರೋಗ್ಯ ಮುನ್ಸೂಚನೆಗಳು & ಒಳನೋಟಗಳು",
        "healthcare_pro": "ಆರೋಗ್ಯ ವೃತ್ತಿಪರ",
        "patient_analytics": "ರೋಗಿಗಳ ವಿಶ್ಲೇಷಣೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "doctor_verification_key": "ವೈದ್ಯರ ಪರಿಶೀಲನೆ ಕೀ",
        "key_required_note": "ವೈದ್ಯಕೀಯ ವೃತ್ತಿಪರ ನೋಂದಣಿಗೆ ಅಗತ್ಯವಿದೆ (ಕೀ: HEALTH2025)",
        "creating_account": "ಖಾತೆ ರಚಿಸಲಾಗುತ್ತಿದೆ...",
        "login_here": "ಇಲ್ಲಿ ಲಾಗಿನ್ ಮಾಡಿ",
        "create_new_account": "ಹೊಸ ಖಾತೆಯನ್ನು ರಚಿಸಿ",
        "prediction_results": "ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶಗಳು",
        "prediction_result": "ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶ",
        "health_stage": "ಆರೋಗ್ಯ ಹಂತ",
        "multi_model_analysis": "ಬಹು-ಮಾದರಿ AI ವಿಶ್ಲೇಷಣೆ",
        "model_agreement": "ಮಾದರಿ ಒಪ್ಪಂದ",
        "prediction_label": "ಮುನ್ಸೂಚನೆ",
        "final_prediction_note": "ಅಂತಿಮ ಮುನ್ಸೂಚನೆಯು ಮೂರು ಮಾದರಿಗಳ ಮತದಾನವನ್ನು ಆಧರಿಸಿದೆ",
        "personalized_recommendations": "ವೈಯಕ್ತೀಕರಿಸಿದ ಶಿಫಾರಸುಗಳು",
        "download_pdf_report": "PDF ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        "share_email": "ಇಮೇಲ್ ಮೂಲಕ ಹಂಚಿಕೊಳ್ಳಿ",
        "view_history": "ಇತಿಹಾಸವನ್ನು ವೀಕ್ಷಿಸಿ",
        "new_test": "ಹೊಸ ಪರೀಕ್ಷೆ",
        "medical_disclaimer": "ವೈದ್ಯಕೀಯ ಹಕ್ಕು ನಿರಾಕರಣೆ",
        "disclaimer_text": "ಈ ಮುನ್ಸೂಚನೆಯು ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ ಮತ್ತು ವೃತ್ತಿಪರ ವೈದ್ಯಕೀಯ ಸಲಹೆಯನ್ನು ಬದಲಿಸಬಾರದು.",
        "share_modal_title": "ಇಮೇಲ್ ಮೂಲಕ ವೈದ್ಯಕೀಯ ವರದಿಯನ್ನು ಹಂಚಿಕೊಳ್ಳಿ",
        "recipient_email": "ಸ್ವೀಕರಿಸುವವರ ಇಮೇಲ್ ವಿಳಾಸ",
        "report_includes_note": "ಸಂಪೂರ್ಣ PDF ವರದಿಯನ್ನು ಈ ಇಮೇಲ್ ವಿಳಾಸಕ್ಕೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ",
        "report_contents": "ವರದಿ ವಿಷಯಗಳು",
        "final_result": "ಅಂತಿಮ ಫಲಿತಾಂಶ",
        "ai_analysis": "AI ವಿಶ್ಲೇಷಣೆ",
        "multi_model_report_includes": "ಬಹು-ಮಾದರಿ AI ವರದಿ ಒಳಗೊಂಡಿದೆ",
        "indiv_predictions": "3 AI ಮಾದರಿಗಳಿಂದ ವೈಯಕ್ತಿಕ ಮುನ್ಸೂಚನೆಗಳು",
        "conf_scores": "ಪ್ರತಿ ಮಾದರಿಗೆ ವಿಶ್ವಾಸಾರ್ಹ ಅಂಕಗಳು",
        "model_agreement_indicators": "ಮಾದರಿ ಒಪ್ಪಂದದ ಸೂಚಕಗಳು",
        "health_recs": "ವೈಯಕ್ತೀಕರಿಸಿದ ಆರೋಗ್ಯ ಶಿಫಾರಸುಗಳು",
        "privacy_notice": "ಗೌಪ್ಯತೆ ಸೂಚನೆ",
        "privacy_text": "ಈ ವರದಿಯು ಸೂಕ್ಷ್ಮ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ಒಳಗೊಂಡಿದೆ.",
        "send_report_now": "ಈಗ ವರದಿಯನ್ನು ಕಳುಹಿಸಿ",
        "your_medical_history": "ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ",
        "no_records_found": "ಯಾವುದೇ ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        "take_first_test": "ನಿಮ್ಮ ಮೊದಲ ಪರೀಕ್ಷೆಯನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ",
        "recent_health_metrics": "ಇತ್ತೀಚಿನ ಆರೋಗ್ಯ ಮೆಟ್ರಿಕ್ಸ್ ಟ್ರೆಂಡ್",
        "admin_dashboard": "ಆಡಳಿತ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "system_overview": "ಸಿಸ್ಟಮ್ ಅವಲೋಕನ ಮತ್ತು ಬಳಕೆದಾರ ನಿರ್ವಹಣೆ",
        "total_users": "ಒಟ್ಟು ಬಳಕೆದಾರರು",
        "healthcare_professionals": "ಆರೋಗ್ಯ ವೃತ್ತಿಪರರು",
        "total_predictions": "ಒಟ್ಟು ಮುನ್ಸೂಚನೆಗಳು",
        "recent_users": "ಇತ್ತೀಚಿನ ಬಳಕೆದಾರರು",
        "registered": "ನೋಂದಾಯಿಸಲಾಗಿದೆ",
        "admin_activity_log": "ಆಡಳಿತ ಚಟುವಟಿಕೆ ಲಾಗ್",
        "admin_user": "ಆಡಳಿತ ಬಳಕೆದಾರ",
        "action": "ಕ್ರಿಯೆ",
        "target_user": "ಗುರಿ ಬಳಕೆದಾರ",
        "quick_actions": "ತ್ವರಿತ ಕ್ರಿಯೆಗಳು",
        "main_site": "ಮುಖ್ಯ ಸೈಟ್",
        "refresh_data": "ಡೇಟಾವನ್ನು ರಿಫ್ರೆಶ್ ಮಾಡಿ",
        "export_data": "ಡೇಟಾವನ್ನು ರಫ್ತು ಮಾಡಿ",
        "privacy_notice_history": "ಭದ್ರತೆ ಮತ್ತು ಗೌಪ್ಯತೆಗಾಗಿ ನೀವು ನಿಮ್ಮ ಸ್ವಂತ ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳನ್ನು ಮಾತ್ರ ವೀಕ್ಷಿಸಬಹುದು.",
        "patient_name": "ರೋಗಿಯ ಹೆಸರು",
        "doctor_dashboard": "ವೈದ್ಯರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "analytics_patients": "ಎಲ್ಲಾ ನೋಂದಾಯಿತ ರೋಗಿಗಳ ವಿಶ್ಲೇಷಣೆ",
        "total_patients": "ಒಟ್ಟು ರೋಗಿಗಳು",
        "diabetic": "ಮಧುಮೇಹಿ",
        "non_diabetic": "ಮಧುಮೇಹಿ ಅಲ್ಲದವರು",
        "avg_glucose_bmi": "ಸರಾಸರಿ ಗ್ಲೂಕೋಸ್ / BMI",
        "patient_records": "ರೋಗಿಯ ದಾಖಲೆಗಳು",
        "showing_records": "ದಾಖಲೆಗಳನ್ನು ತೋರಿಸಲಾಗುತ್ತಿದೆ",
        "export_csv": "CSV ರಫ್ತು ಮಾಡಿ",
        "search_placeholder": "ಹೆಸರು, ಬಳಕೆದಾರ ಹೆಸರು, ಫಲಿತಾಂಶ ಅಥವಾ ಹಂತದ ಮೂಲಕ ಹುಡುಕಿ",
        "search_button": "ಹುಡುಕಿ",
        "clear": "ಅಳಿಸಿ",
        "search_results": "ಹುಡುಕಾಟ ಫಲಿತಾಂಶಗಳು",
        "found_patients": "ಕಂಡುಬಂದ ರೋಗಿ(ಗಳು)",
        "prev": "ಹಿಂದಿನ",
        "next": "ಮುಂದಿನ",
        "page_of": "ಪುಟ",
        "total_records_text": "ಒಟ್ಟು ದಾಖಲೆಗಳು",
        "landing_context_title": "ಮಧುಮೇಹ ಮುನ್ಸೂಚನೆ ಏಕೆ ಮುಖ್ಯ?",
        "landing_context_subtitle": "ಜಾಗತಿಕ ಮಧುಮೇಹ ಬಿಕ್ಕಟ್ಟು ಮತ್ತು ಎಐ ತಡೆಗಟ್ಟುವಿಕೆಯನ್ನು ಹೇಗೆ ಬದಲಾಯಿಸುತ್ತಿದೆ ಎಂಬುದನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು",
        "context_epidemic_title": "ಮಧುಮೇಹ ಸಾಂಕ್ರಾಮಿಕ",
        "context_epidemic_text": "ಪ್ರಪಂಚದಾದ್ಯಂತ 463 ದಶಲಕ್ಷಕ್ಕೂ ಹೆಚ್ಚು ವಯಸ್ಕರು ಮಧುಮೇಹದಿಂದ ಬಳಲುತ್ತಿದ್ದಾರೆ ಮತ್ತು ಈ ಸಂಖ್ಯೆ 2045 ರ ವೇಳೆಗೆ 700 ದಶಲಕ್ಷವನ್ನು ತಲುಪುವ ನಿರೀಕ್ಷೆಯಿದೆ. ಹೆಚ್ಚು ಆತಂಕಕಾರಿ ಸಂಗತಿಯೆಂದರೆ? ಮಧುಮೇಹ ಹೊಂದಿರುವ ಸುಮಾರು 50% ಜನರು ರೋಗನಿರ್ಣಯ ಮಾಡಲ್ಪಟ್ಟಿಲ್ಲ, ಹೃದಯ ಕಾಯಿಲೆ, ಮೂತ್ರಪಿಂಡ ವೈಫಲ್ಯ, ಕುರುಡುತನ ಮತ್ತು ಅಂಗಾಂಗಗಳ ಛೇದನಕ್ಕೆ ಕಾರಣವಾಗುವ ಸ್ಥಿತಿಯಿಂದ ಮೌನವಾಗಿ ಬಳಲುತ್ತಿದ್ದಾರೆ. ಆರಂಭಿಕ ಪತ್ತೆಯೇ ತಡೆಗಟ್ಟುವಿಕೆ ಮತ್ತು ಉತ್ತಮ ಫಲಿತಾಂಶಗಳಿಗೆ ಪ್ರಮುಖವಾಗಿದೆ.",
        "context_prevention_title": "ತಡೆಗಟ್ಟುವಿಕೆ ಜೀವಗಳನ್ನು ಉಳಿಸುತ್ತದೆ",
        "context_prevention_text": "ಜೀವನಶೈಲಿಯ ಬದಲಾವಣೆಗಳು ಹೆಚ್ಚಿನ ಅಪಾಯದ ವ್ಯಕ್ತಿಗಳಲ್ಲಿ ಮಧುಮೇಹದ ಅಪಾಯವನ್ನು 58% ರಷ್ಟು ಕಡಿಮೆ ಮಾಡಬಹುದು ಎಂದು ಅಧ್ಯಯನಗಳು ತೋರಿಸುತ್ತವೆ. ಆದರೆ ನಿಮಗೆ ತಿಳಿದಿಲ್ಲದಿದ್ದರೆ ತಡೆಯಲು ಸಾಧ್ಯವಿಲ್ಲ. ನಮ್ಮ ಎಐ-ಚಾಲಿತ ಉಪಕರಣವು ಪಿಮಾ ಇಂಡಿಯನ್ ಡಯಾಬಿಟಿಸ್ ಡೇಟಾಸೆಟ್ ಆಧಾರಿತ ತ್ವರಿತ ಅಪಾಯದ ಮೌಲ್ಯಮಾಪನವನ್ನು ಒದಗಿಸುತ್ತದೆ - ಇದು 10,000 ಕ್ಕೂ ಹೆಚ್ಚು ಸಂಶೋಧನಾ ಅಧ್ಯಯನಗಳಲ್ಲಿ ಬಳಸಲಾದ ಗೋಲ್ಡ್-ಸ್ಟ್ಯಾಂಡರ್ಡ್ ವೈದ್ಯಕೀಯ ಡೇಟಾಸೆಟ್. ಇಂದು ನಿಮ್ಮ ಅಪಾಯವನ್ನು ತಿಳಿಯಿರಿ, ನಾಳೆ ನಿಮ್ಮ ಜೀವನವನ್ನು ಬದಲಾಯಿಸಿ.",
        "context_how_works_title": "ನಮ್ಮ ಬಹು-ಮಾದರಿ ಎಐ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
        "context_how_works_text": "ನಮ್ಮ ಸುಧಾರಿತ ವ್ಯವಸ್ಥೆಯು 3 ಪ್ರಬಲ ಎಐ ಮಾದರಿಗಳನ್ನು ಸಂಯೋಜಿಸುತ್ತದೆ - ಲಾಜಿಸ್ಟಿಕ್ ರಿಗ್ರೆಶನ್, ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಮತ್ತು ಎಕ್ಸ್‌ಜಿಬೂಸ್ಟ್ - 8 ನಿರ್ಣಾಯಕ ಆರೋಗ್ಯ ನಿಯತಾಂಕಗಳೊಂದಿಗೆ 768 ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳ ಮೇಲೆ ತರಬೇತಿ ನೀಡಲಾಗಿದೆ: ಗ್ಲೂಕೋಸ್ ಮಟ್ಟಗಳು, ಬಿಎಂಐ, ರಕ್ತದೊತ್ತಡ, ಇನ್ಸುಲಿನ್, ವಯಸ್ಸು, ಗರ್ಭಧಾರಣೆಯ ಇತಿಹಾಸ, ಚರ್ಮದ ದಪ್ಪ ಮತ್ತು ಆನುವಂಶಿಕ ಅಂಶಗಳು. ಎನ್ಸೆಂಬಲ್ ಮತದಾನವನ್ನು ಬಳಸಿಕೊಂಡು, ಈ ವ್ಯವಸ್ಥೆಯು 75.3% ಮುನ್ಸೂಚನೆ ನಿಖರತೆಯನ್ನು ಸಾಧಿಸುತ್ತದೆ ಮತ್ತು ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆಗಾಗಿ ಮಾದರಿ ಒಪ್ಪಂದದ ಸೂಚಕಗಳನ್ನು ಒದಗಿಸುತ್ತದೆ.",
        "context_validated_title": "ವೈದ್ಯಕೀಯವಾಗಿ ಮೌಲ್ಯೀಕರಿಸಲಾಗಿದೆ",
        "context_validated_text": "ನ್ಯಾಷನಲ್ ಇನ್‌ಸ್ಟಿಟ್ಯೂಟ್ ಆಫ್ ಡಯಾಬಿಟಿಸ್ ಮತ್ತು ಡೈಜೆಸ್ಟಿವ್ ಮತ್ತು ಕಿಡ್ನಿ ಕಾಯಿಲೆಗಳಿಂದ ಪ್ರಸಿದ್ಧ ಪಿಮಾ ಇಂಡಿಯನ್ ಡಯಾಬಿಟಿಸ್ ಡೇಟಾಸೆಟ್ ಮೇಲೆ ನಿರ್ಮಿಸಲಾಗಿದೆ. ನಮ್ಮ ಮುನ್ಸೂಚನೆಗಳು ಅಪಾಯವನ್ನು 4 ಹಂತಗಳಾಗಿ ವರ್ಗೀಕರಿಸುತ್ತವೆ: ಸಾಮಾನ್ಯ, ಪೂರ್ವ-ಮಧುಮೇಹ, ಟೈಪ್ 1 ಮತ್ತು ಟೈಪ್ 2 ಮಧುಮೇಹ - ಪ್ರತಿಯೊಂದಕ್ಕೂ ವೈಯಕ್ತೀಕರಿಸಿದ ಆರೋಗ್ಯ ಶಿಫಾರಸುಗಳಿವೆ.",
        "context_privacy_title": "ನಿಮ್ಮ ಗೌಪ್ಯತೆ, ಖಾತರಿ",
        "context_privacy_text": "ನಿಮ್ಮ ಆರೋಗ್ಯ ಡೇಟಾವನ್ನು ಎನ್‌ಕ್ರಿಪ್ಟ್ ಮಾಡಲಾಗಿದೆ, ಸುರಕ್ಷಿತವಾಗಿದೆ ಮತ್ತು ಎಂದಿಗೂ ಮಾರಾಟ ಮಾಡಲಾಗುವುದಿಲ್ಲ. ನಾವು ಕಟ್ಟುನಿಟ್ಟಾದ HIPAA-ಕಂಪ್ಲೈಂಟ್ ಭದ್ರತಾ ಪ್ರೋಟೋಕಾಲ್‌ಗಳನ್ನು ಅನುಸರಿಸುತ್ತೇವೆ. ಎಲ್ಲಾ ಮುನ್ಸೂಚನೆಗಳನ್ನು ಸ್ಥಳೀಯವಾಗಿ ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತದೆ, ಮತ್ತು ನಿಮ್ಮ ಡೇಟಾವನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ನೀವು ನಿಯಂತ್ರಿಸುತ್ತೀರಿ - ಇತಿಹಾಸವನ್ನು ವೀಕ್ಷಿಸಿ, ವರದಿಗಳನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಯಾವಾಗ ಬೇಕಾದರೂ ಅಳಿಸಿ.",
        "stats_accuracy": "% ಎನ್ಸೆಂಬಲ್ ನಿಖರತೆ",
        "stats_people": "ದಶಲಕ್ಷ ಜನರು ಮಧುಮೇಹದೊಂದಿಗೆ",
        "stats_risk_reduction": "% ಅಪಾಯ ಕಡಿತ ಸಾಧ್ಯ",
        "stats_params": "ವಿಶ್ಲೇಷಿಸಲಾದ ಆರೋಗ್ಯ ನಿಯತಾಂಕಗಳು",
        "features_title": "ಉತ್ತಮ ಆರೋಗ್ಯಕ್ಕಾಗಿ ಶಕ್ತಿಶಾಲಿ ವೈಶಿಷ್ಟ್ಯಗಳು",
        "features_subtitle": "ಸಮಗ್ರ ಮಧುಮೇಹ ಅಪಾಯದ ಮೌಲ್ಯಮಾಪನಕ್ಕಾಗಿ ನಿಮಗೆ ಬೇಕಾಗಿರುವುದು",
        "feature_ensemble_title": "3-ಮಾದರಿ ಎಐ ಎನ್ಸೆಂಬಲ್",
        "feature_ensemble_desc": "ಲಾಜಿಸ್ಟಿಕ್ ರಿಗ್ರೆಶನ್, ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಮತ್ತು ಎಕ್ಸ್‌ಜಿಬೂಸ್ಟ್ ಬಹುಮತದ ಮತದಾನದೊಂದಿಗೆ ಒಟ್ಟಾಗಿ ಕೆಲಸ ಮಾಡುತ್ತವೆ. ಪಾರದರ್ಶಕ, ವಿಶ್ವಾಸಾರ್ಹ ಫಲಿತಾಂಶಗಳಿಗಾಗಿ ವೈಯಕ್ತಿಕ ಮಾದರಿ ಮುನ್ಸೂಚನೆಗಳು, ವಿಶ್ವಾಸಾರ್ಹ ಅಂಕಗಳು ಮತ್ತು ಒಪ್ಪಂದದ ಸೂಚಕಗಳನ್ನು ನೋಡಿ.",
        "feature_instant_title": "ತಕ್ಷಣದ ಮುನ್ಸೂಚನೆಗಳು",
        "feature_instant_desc": "3 ಸೆಕೆಂಡುಗಳಲ್ಲಿ ಎಐ-ಚಾಲಿತ ಮಧುಮೇಹ ಅಪಾಯದ ಮೌಲ್ಯಮಾಪನವನ್ನು ಪಡೆಯಿರಿ. ಕಾಯುವಿಕೆ ಇಲ್ಲ, ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್‌ಗಳಿಲ್ಲ - ಯಂತ್ರ ಕಲಿಯುವಿಕೆಯಿಂದ ಚಾಲಿತವಾದ ತಕ್ಷಣದ, ಕ್ರಿಯಾಾತ್ಮಕ ಒಳನೋಟಗಳು.",
        "feature_trends_title": "ಆರೋಗ್ಯ ಪ್ರವೃತ್ತಿಗಳು ಮತ್ತು ವಿಶ್ಲೇಷಣೆ",
        "feature_trends_desc": "ಸುಂದರವಾದ ದೃಶ್ಯೀಕರಣಗಳೊಂದಿಗೆ ಕಾಲಾನಂತರದಲ್ಲಿ ನಿಮ್ಮ ಆರೋಗ್ಯ ಪ್ರಯಾಣವನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ. ಜೀವನಶೈಲಿಯ ಬದಲಾವಣೆಗಳು ನಿಮ್ಮ ಅಪಾಯದ ಮೇಲೆ ಹೇಗೆ ಪರಿಣಾಮ ಬೀರುತ್ತವೆ ಎಂಬುದನ್ನು ನೋಡಲು ಗ್ಲೂಕೋಸ್, ಬಿಎಂಐ ಮತ್ತು ರಕ್ತದೊತ್ತಡದ ಪ್ರವೃತ್ತಿಗಳನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ.",
        "feature_pdf_title": "ವಿವರವಾದ PDF ವರದಿಗಳು",
        "feature_pdf_desc": "ನಿಮ್ಮ ವೈದ್ಯರೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಲು ಬಹು-ಮಾದರಿ ಎಐ ವಿಶ್ಲೇಷಣೆ, ಹಂತದ ವರ್ಗೀಕರಣ ಮತ್ತು ವೈಯಕ್ತೀಕರಿಸಿದ ಶಿಫಾರಸುಗಳೊಂದಿಗೆ ವೃತ್ತಿಪರ ಆರೋಗ್ಯ ವರದಿಗಳನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ.",
        "feature_email_title": "ಇಮೇಲ್ ವರದಿ ಹಂಚಿಕೆ",
        "feature_email_desc": "ನಿಮ್ಮ ಸಮಗ್ರ ಆರೋಗ್ಯ ವರದಿಗಳನ್ನು ಇಮೇಲ್ ಮೂಲಕ ವೈದ್ಯರು ಅಥವಾ ಕುಟುಂಬ ಸದಸ್ಯರೊಂದಿಗೆ ತಕ್ಷಣ ಹಂಚಿಕೊಳ್ಳಿ. ಎಲ್ಲಾ 3 ಮಾದರಿ ಮುನ್ಸೂಚನೆಗಳು, ವಿಶ್ವಾಸಾರ್ಹ ಅಂಕಗಳು ಮತ್ತು ವೈದ್ಯಕೀಯ ಶಿಫಾರಸುಗಳನ್ನು ಒಳಗೊಂಡಿದೆ.",
        "feature_stages_title": "4-ಹಂತದ ಅಪಾಯದ ವರ್ಗೀಕರಣ",
        "feature_stages_desc": "ಪ್ರತಿ ಅಪಾಯದ ಮಟ್ಟಕ್ಕೆ ಅನುಗುಣವಾಗಿ ನಿರ್ದಿಷ್ಟ ಆರೋಗ್ಯ ಶಿಫಾರಸುಗಳೊಂದಿಗೆ ಸಾಮಾನ್ಯ, ಪೂರ್ವ-ಮಧುಮೇಹ, ಟೈಪ್ 1 ಅಥವಾ ಟೈಪ್ 2 ಮಧುಮೇಹ ಎಂದು ನಿಖರವಾದ ವರ್ಗೀಕರಣ.",
        "feature_doctor_title": "ವೈದ್ಯರ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "feature_doctor_desc": "ಆರೋಗ್ಯ ವೃತ್ತಿಪರರು ಸುಧಾರಿತ ವಿಶ್ಲೇಷಣೆ, ರೋಗಿಗಳ ಹುಡುಕಾಟ, ಪುಟವಿನ್ಯಾಸ, CSV ರಫ್ತುಗಳು ಮತ್ತು ಸಮಗ್ರ ರೋಗಿ ನಿರ್ವಹಣಾ ಸಾಧನಗಳನ್ನು ಪಡೆಯುತ್ತಾರೆ.",
        "feature_security_title": "ಬ್ಯಾಂಕ್-ಮಟ್ಟದ ಭದ್ರತೆ",
        "feature_security_desc": "ನಿಮ್ಮ ಡೇಟಾವನ್ನು ಎಂಟರ್‌ಪ್ರೈಸ್-ಗ್ರೇಡ್ ಎನ್‌ಕ್ರಿಪ್ಶನ್, ಸುರಕ್ಷಿತ ದೃಢೀಕರಣ ಮತ್ತು HIPAA-ಕಂಪ್ಲೈಂಟ್ ಗೌಪ್ಯತೆ ಮಾನದಂಡಗಳೊಂದಿಗೆ ರಕ್ಷಿಸಲಾಗಿದೆ. ನಿಮ್ಮ ಆರೋಗ್ಯ, ನಿಮ್ಮ ನಿಯಂತ್ರಣ.",
        "how_it_works_title": "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
        "how_it_works_subtitle": "3 ಸರಳ ಹಂತಗಳಲ್ಲಿ ನಿಮ್ಮ ಮಧುಮೇಹ ಅಪಾಯದ ಮೌಲ್ಯಮಾಪನವನ್ನು ಪಡೆಯಿರಿ",
        "step_1_title": "ನಿಮ್ಮ ಆರೋಗ್ಯ ಡೇಟಾವನ್ನು ನಮೂದಿಸಿ",
        "step_1_desc": "ಉಚಿತವಾಗಿ ನೋಂದಾಯಿಸಿ ಮತ್ತು 8 ಪ್ರಮುಖ ಆರೋಗ್ಯ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ: ವಯಸ್ಸು, ಗ್ಲೂಕೋಸ್ ಮಟ್ಟ, ಬಿಎಂಐ, ರಕ್ತದೊತ್ತಡ, ಇನ್ಸುಲಿನ್, ಗರ್ಭಧಾರಣೆಯ ಇತಿಹಾಸ, ಚರ್ಮದ ದಪ್ಪ ಮತ್ತು ಮಧುಮೇಹ ವಂಶಾವಳಿ ಕಾರ್ಯ. ನಿಖರವಾದ ಮುನ್ಸೂಚನೆಗಳನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಲು ಪ್ರತಿ ಕ್ಷೇತ್ರವು ಸಹಾಯಕವಾದ ಮಾರ್ಗದರ್ಶನ ಮತ್ತು ಮೌಲ್ಯೀಕರಣವನ್ನು ಒಳಗೊಂಡಿದೆ.",
        "step_2_title": "ಬಹು-ಮಾದರಿ ಎಐ ನಿಮ್ಮ ಅಪಾಯವನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ",
        "step_2_desc": "ನಮ್ಮ ಸುಧಾರಿತ 3-ಮಾದರಿ ಎನ್ಸೆಂಬಲ್ ವ್ಯವಸ್ಥೆ - 768 ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳ ಮೇಲೆ ತರಬೇತಿ ನೀಡಲಾಗಿದೆ - ಸ್ಟ್ಯಾಂಡರ್ಡ್ ಸ್ಕೇಲರ್ ಸಾಮಾನ್ಯೀಕರಣದೊಂದಿಗೆ ಲಾಜಿಸ್ಟಿಕ್ ರಿಗ್ರೆಶನ್, ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಮತ್ತು ಎಕ್ಸ್‌ಜಿಬೂಸ್ಟ್ ಅಲ್ಗಾರಿದಮ್‌ಗಳ ಮೂಲಕ ನಿಮ್ಮ ಡೇಟಾವನ್ನು ತಕ್ಷಣ ಪ್ರಕ್ರಿಯೆಗೊಳಿಸುತ್ತದೆ. ಪ್ರತಿ ಮಾದರಿಯು ವಿಶ್ವಾಸಾರ್ಹ ಅಂಕಗಳೊಂದಿಗೆ ಸ್ವತಂತ್ರ ಮುನ್ಸೂಚನೆಗಳನ್ನು ನೀಡುತ್ತದೆ, ಮತ್ತು ಅಂತಿಮ ಫಲಿತಾಂಶವು ಗರಿಷ್ಠ ವಿಶ್ವಾಸಾರ್ಹತೆಗಾಗಿ ಬಹುಮತದ ಮತದಾನವನ್ನು ಬಳಸುತ್ತದೆ, ಮಾದರಿ ಒಪ್ಪಂದದ ಸೂಚಕಗಳೊಂದಿಗೆ 75.3% ಎನ್ಸೆಂಬಲ್ ನಿಖರತೆಯನ್ನು ಸಾಧಿಸುತ್ತದೆ.",
        "step_3_title": "ಕ್ರಿಯಾತ್ಮಕ ಒಳನೋಟಗಳನ್ನು ಪಡೆಯಿರಿ",
        "step_3_desc": "ನಿಮ್ಮ ಅಪಾಯದ ವರ್ಗೀಕರಣ (ಸಾಮಾನ್ಯ, ಪೂರ್ವ-ಮಧುಮೇಹ, ಟೈಪ್ 1, ಅಥವಾ ಟೈಪ್ 2), ವೈಯಕ್ತೀಕರಿಸಿದ ಆರೋಗ್ಯ ಶಿಫಾರಸುಗಳು, ಪ್ರವೃತ್ತಿ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಡೌನ್‌ಲೋಡ್ ಮಾಡಬಹುದಾದ PDF ವರದಿಗಳೊಂದಿಗೆ ತಕ್ಷಣದ ಫಲಿತಾಂಶಗಳನ್ನು ಪಡೆಯಿರಿ. ನಿಮ್ಮ ವೈದ್ಯರೊಂದಿಗೆ ಹಂಚಿಕೊಳ್ಳಿ ಅಥವಾ ಕಾಲಾನಂತರದಲ್ಲಿ ನಿಮ್ಮ ಪ್ರಗತಿಯನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ.",
        "footer_desc": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಮತ್ತು ಆರಂಭಿಕ ಪತ್ತೆಯ ಮೂಲಕ ಆರೋಗ್ಯಕರ ಜೀವನವನ್ನು ಸಶಕ್ತಗೊಳಿಸುವುದು.",
        "footer_dataset": "ಪಿಮಾ ಇಂಡಿಯನ್ ಡಯಾಬಿಟಿಸ್ ಡೇಟಾಸೆಟ್ ಮೇಲೆ ನಿರ್ಮಿಸಲಾಗಿದೆ<br>ಸಂಶೋಧನೆ-ಬೆಂಬಲಿತ • ವೈದ್ಯಕೀಯವಾಗಿ ಮೌಲ್ಯೀಕರಿಸಲಾಗಿದೆ • ಗೌಪ್ಯತೆ-ಮೊದಲು",
        "footer_rights": "2025 DiabetesAI. ಎಲ್ಲಾ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ.",
        "footer_dev": "ಉತ್ತಮ ಆರೋಗ್ಯ ರಕ್ಷಣೆಗಾಗಿ ❤️ ನೊಂದಿಗೆ ಅಭಿವೃದ್ಧಿಪಡಿಸಲಾಗಿದೆ",
        "footer_disclaimer": "ಈ ಉಪಕರಣವು ಶೈಕ್ಷಣಿಕ ಉದ್ದೇಶಗಳಿಗಾಗಿ ಮಾತ್ರ ಮತ್ತು ವೃತ್ತಿಪರ ವೈದ್ಯಕೀಯ ಸಲಹೆಯನ್ನು ಬದಲಿಸಬಾರದು.",
        "medical_history_title": "ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ",
        "stage_label": "ಹಂತ",
        "model_lr": "ಲಾಜಿಸ್ಟಿಕ್ ರಿಗ್ರೆಷನ್",
        "model_rf": "ರ್ಯಾಂಡಮ್ ಫಾರೆಸ್ಟ್",
        "model_xgb": "ಎಕ್ಸ್‌ಜಿಬೂಸ್ಟ್",
        "agree_all": "ಎಲ್ಲಾ ಮಾದರಿಗಳು ಒಪ್ಪುತ್ತವೆ (100%)",
        "agree_majority": "ಬಹುಮತದ ಒಮ್ಮತ (67%)",
        "models_ensemble": "3 ಮಾದರಿಗಳು + ಎನ್ಸೆಂಬಲ್",
        "final_diagnosis": "ಅಂತಿಮ ರೋಗನಿರ್ಣಯ",
        "privacy_warning": "ವಿಶ್ವಾಸಾರ್ಹ ಆರೋಗ್ಯ ಪೂರೈಕೆದಾರರು ಅಥವಾ ಅಧಿಕೃತ ಕುಟುಂಬ ಸದಸ್ಯರೊಂದಿಗೆ ಮಾತ್ರ ಹಂಚಿಕೊಳ್ಳಿ.",
        "rec_maintain_diet": "ಆರೋಗ್ಯಕರ ಆಹಾರ ಕ್ರಮವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ",
        "rec_exercise_30": "ದಿನಕ್ಕೆ 30 ನಿಮಿಷ ವ್ಯಾಯಾಮ ಮಾಡಿ",
        "rec_annual_checkup": "ವಾರ್ಷಿಕ ತಪಾಸಣೆ",
        "rec_reduce_sugar": "ಸಕ್ಕರೆ ಸೇವನೆ ಕಡಿಮೆ ಮಾಡಿ",
        "rec_exercise_5": "ವಾರಕ್ಕೆ 5 ದಿನ ವ್ಯಾಯಾಮ ಮಾಡಿ",
        "rec_monitor_3": "3 ತಿಂಗಳು ಗ್ಲೂಕೋಸ್ ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ",
        "rec_consult_insulin": "ಇನ್ಸುಲಿನ್‌ಗಾಗಿ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "rec_monitor_glucose": "ರಕ್ತದ ಗ್ಲೂಕೋಸ್ ಮೇಲ್ವಿಚಾರಣೆ",
        "rec_balanced_meals": "ಸಮತೋಲಿತ ಊಟ",
        "rec_medication": "ಕಟ್ಟುನಿಟ್ಟಾದ ಔಷಧ ಮತ್ತು ಆಹಾರ",
        "rec_weight": "ತೂಕ ನಿರ್ವಹಣೆ",
        "rec_consult": "ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ",
        "health_trends_title": "ನಿಮ್ಮ ಆರೋಗ್ಯ ಪ್ರವೃತ್ತಿಗಳು",
        "privacy_notice_history": "ಗೌಪ್ಯತೆ ಸೂಚನೆ: ಭದ್ರತೆ ಮತ್ತು ಗೌಪ್ಯತೆಗಾಗಿ ನೀವು ನಿಮ್ಮ ಸ್ವಂತ ವೈದ್ಯಕೀಯ ದಾಖಲೆಗಳನ್ನು ಮಾತ್ರ ವೀಕ್ಷಿಸಬಹುದು.",
        "years": "ವರ್ಷಗಳು"
    }
}

@app.context_processor
def inject_translations():
    lang = session.get('lang', 'en')
    return dict(t=translations.get(lang, translations['en']), lang=lang)

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

# Configuration from environment variables
DOCTOR_SECRET_KEY = os.getenv('DOCTOR_SECRET_KEY', 'HEALTH2025')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
FROM_EMAIL = f"Diabetes Health App <{EMAIL_USERNAME}>"
EMAIL_CONFIGURED = os.getenv('EMAIL_CONFIGURED', 'False').lower() == 'true'

# Load ML models & scaler
try:
    # Load all three models
    model_lr = joblib.load("diabetes_model_lr.pkl")
    model_rf = joblib.load("diabetes_model_rf.pkl")
    model_xgb = joblib.load("diabetes_model_xgb.pkl")
    scaler = joblib.load("scaler.pkl")
    # Keep legacy model for backward compatibility
    model = model_lr
    print("✅ Multi-Model AI System Loaded:")
    print("   • Logistic Regression")
    print("   • Random Forest")
    print("   • XGBoost")
except FileNotFoundError:
    print("Warning: ML model files not found. Please run train_model.py first.")
    model = None
    model_lr = None
    model_rf = None
    model_xgb = None
    scaler = None

# Database connection helper
def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = sqlite3.connect("diabetes_app.db", timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Database initialization
def init_db():
    conn = get_db_connection()
    if not conn:
        print("Failed to initialize database")
        return False
    cursor = conn.cursor()
    
    # Users table with email and reset token
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_expires DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            age INTEGER,
            pregnancies INTEGER,
            glucose REAL,
            bp REAL,
            skin REAL,
            insulin REAL,
            bmi REAL,
            dpf REAL,
            result TEXT,
            stage TEXT,
            suggestion TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    # Admin logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user TEXT,
            action TEXT,
            target_user TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    return True

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    """Validate password strength"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")

    return errors

def send_email(to_email, subject, body, attachment_data=None, attachment_name=None, html_body=None):
    """Send email with optional attachment and HTML support"""
    if not EMAIL_CONFIGURED:
        print(f"📧 EMAIL (Not Configured): To={to_email}, Subject={subject}")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add plain text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)

        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

        # Add attachment if provided
        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def send_verification_email(email, username, verification_token):
    """Send email verification"""
    verification_url = f"http://127.0.0.1:8080/verify-email/{verification_token}"

    subject = "Verify Your Diabetes Health App Account"

    body = f"""
Hello {username},

Welcome to the Diabetes Health App!

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
Diabetes Health App Team
    """

    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🏥 Diabetes Health App</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Welcome to AI-Powered Health Monitoring</p>
                </div>

                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h2 style="color: #667eea; margin-bottom: 20px;">Hello {username}!</h2>

                    <p>Thank you for joining the Diabetes Health App. We're excited to help you monitor and manage your health with our AI-powered prediction system.</p>

                    <p><strong>Please verify your email address to activate your account:</strong></p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}"
                           style="background: linear-gradient(45deg, #667eea, #764ba2);
                                  color: white;
                                  padding: 15px 30px;
                                  text-decoration: none;
                                  border-radius: 25px;
                                  font-weight: 600;
                                  display: inline-block;
                                  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                            ✓ Verify Email Address
                        </a>
                    </div>

                    <p style="color: #666; font-size: 14px;">
                        <strong>Note:</strong> This verification link will expire in 24 hours.
                    </p>

                    <p style="color: #666; font-size: 14px;">
                        If you didn't create this account, please ignore this email.
                    </p>

                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                    <p style="color: #999; font-size: 12px; text-align: center;">
                        Diabetes Health App Team<br>
                        AI-Powered Health Monitoring Platform
                    </p>
                </div>
            </div>
        </body>
    </html>
    """

    return send_email(email, subject, body, html_body=html_body)

def generate_pdf_report(patient_data):
    """Generate comprehensive PDF report with detailed health analysis"""
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Define colors matching the new theme
    purple_gradient = HexColor('#667eea')
    pink_gradient = HexColor('#f093fb')
    dark_bg = HexColor('#1a1a3e')

    # === PAGE 1: HEADER AND PATIENT INFO ===

    # Gradient Header Background
    c.setFillColor(purple_gradient)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)

    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 50, "DiabetesAI")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 75, "Comprehensive Health Analysis Report")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 95, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

    # Patient Information Section
    y = height - 160
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Patient Information")

    # Draw a separator line
    y -= 5
    c.setStrokeColor(pink_gradient)
    c.setLineWidth(2)
    c.line(50, y, width - 50, y)

    y -= 30
    c.setFillColor(black)

    # Patient details in a table format
    patient_info = [
        ["Full Name:", patient_data[0]],
        ["Age:", f"{patient_data[1]} years"],
        ["Report ID:", f"RPT-{datetime.now().strftime('%Y%m%d')}-{patient_data[0][:3].upper()}"]
    ]

    c.setFont("Helvetica-Bold", 12)
    for label, value in patient_info:
        c.drawString(70, y, label)
        c.setFont("Helvetica", 12)
        c.drawString(200, y, str(value))
        c.setFont("Helvetica-Bold", 12)
        y -= 25

    # Health Metrics Section
    y -= 20
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Health Metrics Analysis")

    y -= 5
    c.setStrokeColor(pink_gradient)
    c.line(50, y, width - 50, y)

    y -= 35

    # Create a table for health metrics
    metrics_data = [
        ["Parameter", "Value", "Normal Range", "Status"],
        ["Glucose Level", f"{patient_data[2]} mg/dL", "70-140 mg/dL",
         "Normal" if float(patient_data[2]) < 140 else "Elevated"],
        ["Body Mass Index (BMI)", f"{patient_data[3]}", "18.5-24.9",
         "Normal" if 18.5 <= float(patient_data[3]) <= 24.9 else "Abnormal"],
        ["Blood Pressure", f"{patient_data[4]} mmHg", "80-120 mmHg",
         "Normal" if 80 <= float(patient_data[4]) <= 120 else "Abnormal"],
    ]

    table = Table(metrics_data, colWidths=[150, 100, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), purple_gradient),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#f8f9fa')]),
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y - 100)

    y -= 130

    # Multi-Model AI Analysis Section
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Multi-Model AI Analysis")

    y -= 5
    c.setStrokeColor(pink_gradient)
    c.line(50, y, width - 50, y)

    y -= 30

    # Recalculate predictions from all models
    try:
        features_for_pred = [0, patient_data[2], patient_data[4], 0, 0, patient_data[3], 0, patient_data[1]]  # Basic features
        features_scaled = scaler.transform([features_for_pred])

        pred_lr = model_lr.predict(features_scaled)[0]
        pred_rf = model_rf.predict(features_scaled)[0]
        pred_xgb = model_xgb.predict(features_scaled)[0]

        prob_lr = model_lr.predict_proba(features_scaled)[0][1] * 100
        prob_rf = model_rf.predict_proba(features_scaled)[0][1] * 100
        prob_xgb = model_xgb.predict_proba(features_scaled)[0][1] * 100

        votes = [pred_lr, pred_rf, pred_xgb]
        agreement = sum(votes)
        agreement_text = "All Models Agree (100%)" if agreement in [0, 3] else "Majority Consensus (67%)"

        c.setFont("Helvetica", 11)
        c.drawString(70, y, f"Model Agreement: {agreement_text}")
        y -= 25

        c.setFont("Helvetica-Bold", 11)
        c.drawString(70, y, "Individual Model Predictions:")
        y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(90, y, f"• Logistic Regression: {'Diabetic' if pred_lr == 1 else 'Not Diabetic'} ({prob_lr:.1f}% confidence)")
        y -= 16
        c.drawString(90, y, f"• Random Forest: {'Diabetic' if pred_rf == 1 else 'Not Diabetic'} ({prob_rf:.1f}% confidence)")
        y -= 16
        c.drawString(90, y, f"• XGBoost: {'Diabetic' if pred_xgb == 1 else 'Not Diabetic'} ({prob_xgb:.1f}% confidence)")
        y -= 25
    except:
        pass  # Fallback if models not available

    # Final Prediction Result
    c.setFont("Helvetica-Bold", 16)
    c.drawString(70, y, "Final Diagnosis (Ensemble Prediction):")
    y -= 30

    # Result box with colored background
    result_color = HexColor('#f5576c') if patient_data[5] == "Diabetic" else HexColor('#4facfe')
    c.setFillColor(result_color)
    c.roundRect(50, y - 50, width - 100, 60, 10, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, y - 20, f"Diagnosis: {patient_data[5]}")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 40, f"Stage: {patient_data[6]}")

    y -= 80

    # === PAGE 2: DETAILED RECOMMENDATIONS ===
    c.showPage()

    # Header for page 2
    c.setFillColor(purple_gradient)
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 45, "Personalized Health Recommendations")

    y = height - 120
    c.setFillColor(black)

    # Recommendations section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Medical Recommendations:")
    y -= 22

    c.setFont("Helvetica", 10)
    recommendations = patient_data[7].split("\n")

    for i, rec in enumerate(recommendations, 1):
        if rec.strip():
            # Draw bullet point
            c.setFillColor(pink_gradient)
            c.circle(60, y + 3, 3, fill=1)

            c.setFillColor(black)
            c.drawString(75, y, rec.strip())
            y -= 20

    y -= 25

    # Lifestyle Guidelines
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Lifestyle Guidelines:")
    y -= 22

    guidelines = [
        "Diet: Focus on whole grains, lean proteins, vegetables, and fruits. Limit sugar and processed foods.",
        "Exercise: Aim for at least 150 minutes of moderate aerobic activity per week.",
        "Hydration: Drink 8-10 glasses of water daily to support metabolic function.",
        "Sleep: Maintain 7-9 hours of quality sleep each night for optimal health.",
        "Stress Management: Practice mindfulness, yoga, or meditation to reduce stress levels.",
        "Regular Monitoring: Track your glucose levels, weight, and blood pressure regularly."
    ]

    c.setFont("Helvetica", 10)
    for guideline in guidelines:
        c.setFillColor(pink_gradient)
        c.circle(60, y + 3, 3, fill=1)

        c.setFillColor(black)
        # Word wrap for long text
        words = guideline.split()
        line = ""
        for word in words:
            if len(line + word) < 80:
                line += word + " "
            else:
                c.drawString(75, y, line)
                y -= 16
                line = word + " "
        if line:
            c.drawString(75, y, line)
        y -= 20

    y -= 25

    # Understanding Your Risk
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Understanding Your Risk Level:")
    y -= 22

    risk_info = {
        "Normal": "Your health metrics are within normal ranges. Continue maintaining a healthy lifestyle.",
        "Pre-Diabetic": "You're at increased risk. Lifestyle changes can reduce diabetes risk by up to 58%.",
        "Type 1 Diabetes": "Requires insulin therapy. Consult an endocrinologist for comprehensive care.",
        "Type 2 Diabetes": "Manageable with medication, diet, and exercise. Regular monitoring is essential."
    }

    c.setFont("Helvetica", 10)
    stage_info = risk_info.get(patient_data[6], "Consult with your healthcare provider for personalized advice.")

    # Word wrap
    words = stage_info.split()
    line = ""
    for word in words:
        if len(line + word) < 85:
            line += word + " "
        else:
            c.drawString(70, y, line)
            y -= 16
            line = word + " "
    if line:
        c.drawString(70, y, line)

    y -= 35

    # Next Steps
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recommended Next Steps:")
    y -= 22

    next_steps = [
        "1. Schedule an appointment with your primary care physician to discuss these results.",
        "2. Share this report with your healthcare provider for professional interpretation.",
        "3. Begin implementing the lifestyle recommendations outlined above.",
        "4. Track your progress and monitor key health metrics regularly.",
        "5. Consider consulting a registered dietitian for personalized nutrition guidance."
    ]

    c.setFont("Helvetica", 10)
    for step in next_steps:
        c.drawString(70, y, step)
        y -= 20

    # Footer with disclaimer - improved spacing
    c.setFillColor(HexColor('#6c757d'))
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 140, "IMPORTANT DISCLAIMER")

    c.setFont("Helvetica", 8)
    disclaimer_text = [
        "This report is generated by an AI-powered multi-model prediction system for educational and informational purposes only.",
        "It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment.",
        "Always consult with a qualified healthcare provider regarding any medical condition or health concerns.",
        "The predictions are based on statistical analysis and may not reflect your individual health status.",
        f"Multi-Model System: LR (75.3%), RF (74.7%), XGBoost (74.0%), Ensemble (75.3%) | PIMA Dataset | Report ID: RPT-{datetime.now().strftime('%Y%m%d')}"
    ]

    y_footer = 120
    for line in disclaimer_text:
        c.drawCentredString(width/2, y_footer, line)
        y_footer -= 14

    # Powered by footer - moved down to avoid overlap
    c.setFillColor(purple_gradient)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, 40, "Powered by DiabetesAI | Advanced Machine Learning Health Analytics")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Routes
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            username_or_email = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username_or_email or not password:
                flash("Please enter both username/email and password!", "error")
                return render_template("login.html")

            hashed_password = hash_password(password)

            conn = get_db_connection()
            if not conn:
                flash("Database connection error. Please try again later.", "error")
                return render_template("login.html")

            cursor = conn.cursor()

            # First check if user exists with this username or email
            cursor.execute("""
                SELECT id, role, username, email FROM users
                WHERE username=? OR email=?
            """, (username_or_email, username_or_email))
            user_check = cursor.fetchone()

            if not user_check:
                flash("User not found!", "error")
                conn.close()
                return render_template("login.html")

            # Now check with password and verification status
            cursor.execute("""
                SELECT id, role, username, is_verified, email FROM users
                WHERE (username=? OR email=?) AND password=?
            """, (username_or_email, username_or_email, hashed_password))
            user = cursor.fetchone()
            conn.close()

            if user:
                user_id, role, username, is_verified, email = user

                # Check if email is verified (skip for existing users who don't have this field set)
                if is_verified is not None and is_verified == 0:
                    flash(f"Please verify your email address first. Check your inbox at {email}.", "warning")
                    return render_template("login.html")

                session["user_id"] = user_id
                session["role"] = role
                session["username"] = username
                flash("Login successful!", "success")

                # Redirect based on role
                if role == "doctor":
                    return redirect(url_for("doctor_dashboard"))
                else:
                    return redirect(url_for("dashboard"))
            else:
                flash("Invalid password!", "error")

        except Exception as e:
            print(f"Login error: {e}")
            flash("An error occurred during login. Please try again.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            role = request.form.get("role", "").strip()

            # Validation
            if not username or not email or not password or not role:
                flash("All fields are required!", "error")
                return render_template("register.html")

            if role not in ["patient", "doctor"]:
                flash("Invalid role selected!", "error")
                return render_template("register.html")

            # Password strength validation
            password_errors = validate_password(password)
            if password_errors:
                for error in password_errors:
                    flash(error, "error")
                return render_template("register.html")

            # Check doctor secret key
            if role == "doctor":
                secret_key = request.form.get("secret_key", "").strip()
                if secret_key != DOCTOR_SECRET_KEY:
                    flash("Invalid doctor secret key!", "error")
                    return render_template("register.html")

            hashed_password = hash_password(password)
            verification_token = secrets.token_urlsafe(32)

            conn = get_db_connection()
            if not conn:
                flash("Database connection error. Please try again later.", "error")
                return render_template("register.html")

            cursor = conn.cursor()

            # Auto-verify if email is not configured
            is_verified = 0 if EMAIL_CONFIGURED else 1

            cursor.execute("""
                INSERT INTO users (username, email, password, role, verification_token, is_verified)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, hashed_password, role, verification_token, is_verified))
            conn.commit()
            conn.close()

            # Send verification email
            if EMAIL_CONFIGURED:
                if send_verification_email(email, username, verification_token):
                    flash(f"Registration successful! A verification email has been sent to {email}. Please check your email to activate your account.", "success")
                else:
                    flash(f"Registration successful! However, verification email could not be sent. Please contact support.", "warning")
            else:
                flash("Registration successful! You can now login.", "success")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError as e:
            flash("Username or email already exists!", "error")
        except Exception as e:
            print(f"Registration error: {e}")
            flash("Registration failed. Please try again.", "error")
    
    return render_template("register.html")

@app.route("/verify-email/<token>")
def verify_email(token):
    """Verify email address with token"""
    try:
        conn = sqlite3.connect("diabetes_app.db")
        cursor = conn.cursor()

        # Check if token exists and is valid
        cursor.execute("""
            SELECT id, username, email, is_verified
            FROM users
            WHERE verification_token = ?
        """, (token,))

        user = cursor.fetchone()

        if not user:
            flash("Invalid or expired verification link!", "error")
            return redirect(url_for("login"))

        user_id, username, email, is_verified = user

        if is_verified:
            flash("Email already verified! You can login.", "info")
            return redirect(url_for("login"))

        # Verify the email
        cursor.execute("""
            UPDATE users
            SET is_verified = 1, verification_token = NULL
            WHERE id = ?
        """, (user_id,))

        conn.commit()
        conn.close()

        flash(f"Email verified successfully! Welcome {username}. You can now login.", "success")
        return redirect(url_for("login"))

    except Exception as e:
        print(f"Email verification error: {e}")
        flash("Verification failed. Please try again or contact support.", "error")
        return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        
        conn = sqlite3.connect("diabetes_app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            reset_token = str(uuid.uuid4())
            expires = datetime.now() + timedelta(hours=1)
            
            cursor.execute("""
                UPDATE users SET reset_token=?, reset_expires=? WHERE email=?
            """, (reset_token, expires, email))
            conn.commit()
            
            # Send reset email
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            subject = "Password Reset - Diabetes Predictor"
            body = f"""
            Hello,
            
            You requested a password reset for your Diabetes Predictor account.
            
            Click the link below to reset your password:
            {reset_link}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            Diabetes Predictor Team
            """
            
            if send_email(email, subject, body):
                flash("Password reset link sent to your email!", "success")
            else:
                flash("Failed to send reset email. Please try again.", "error")
        else:
            flash("Email not found!", "error")
        
        conn.close()
    
    return render_template("forgot_password.html")

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = sqlite3.connect("diabetes_app.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM users 
        WHERE reset_token=? AND reset_expires > ?
    """, (token, datetime.now()))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        flash("Invalid or expired reset token!", "error")
        return redirect(url_for("forgot_password"))
    
    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        if new_password != confirm_password:
            flash("Passwords don't match!", "error")
        else:
            hashed_password = hash_password(new_password)
            cursor.execute("""
                UPDATE users 
                SET password=?, reset_token=NULL, reset_expires=NULL 
                WHERE reset_token=?
            """, (hashed_password, token))
            conn.commit()
            conn.close()
            flash("Password reset successful! Please login.", "success")
            return redirect(url_for("login"))
    
    conn.close()
    return render_template("reset_password.html", token=token)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            session["admin_user"] = username
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials!", "error")
    
    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    conn = sqlite3.connect("diabetes_app.db")
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='doctor'")
    total_doctors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_predictions = cursor.fetchone()[0]
    
    # Get recent users
    cursor.execute("""
        SELECT id, username, email, role, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_users = cursor.fetchall()
    
    # Get admin logs
    cursor.execute("""
        SELECT admin_user, action, target_user, timestamp 
        FROM admin_logs 
        ORDER BY timestamp DESC 
        LIMIT 20
    """)
    admin_logs = cursor.fetchall()
    
    conn.close()
    
    return render_template("admin_dashboard.html",
                         total_users=total_users,
                         total_doctors=total_doctors,
                         total_predictions=total_predictions,
                         recent_users=recent_users,
                         admin_logs=admin_logs)

@app.route("/admin/delete-user/<int:user_id>")
def admin_delete_user(user_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    
    conn = sqlite3.connect("diabetes_app.db")
    cursor = conn.cursor()
    
    # Get username before deleting
    cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        # Delete user's patients first
        cursor.execute("DELETE FROM patients WHERE user_id=?", (user_id,))
        # Delete user
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        
        # Log admin action
        cursor.execute("""
            INSERT INTO admin_logs (admin_user, action, target_user) 
            VALUES (?, ?, ?)
        """, (session.get("admin_user"), "DELETE_USER", user[0]))
        
        conn.commit()
        flash(f"User {user[0]} deleted successfully!", "success")
    else:
        flash("User not found!", "error")
    
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

def validate_medical_input(name, age, pregnancies, glucose, bp, skin, insulin, bmi, dpf):
    """Validate medical input data with proper ranges"""
    errors = []

    # Name validation
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")

    # Age validation
    if not (1 <= age <= 120):
        errors.append("Age must be between 1 and 120 years")

    # Pregnancies validation
    if not (0 <= pregnancies <= 20):
        errors.append("Pregnancies must be between 0 and 20")

    # Glucose validation
    if not (0 <= glucose <= 400):
        errors.append("Glucose must be between 0 and 400 mg/dL")

    # Blood Pressure validation
    if not (40 <= bp <= 200):
        errors.append("Blood Pressure must be between 40 and 200 mmHg")

    # Skin Thickness validation
    if not (0 <= skin <= 100):
        errors.append("Skin Thickness must be between 0 and 100 mm")

    # Insulin validation
    if not (0 <= insulin <= 900):
        errors.append("Insulin must be between 0 and 900 µU/mL")

    # BMI validation
    if not (10 <= bmi <= 70):
        errors.append("BMI must be between 10 and 70")

    # DPF validation
    if not (0 <= dpf <= 3):
        errors.append("Diabetes Pedigree Function must be between 0 and 3")

    return errors

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not model or not scaler:
        flash("Prediction model not available. Please contact administrator.", "error")
        return redirect(url_for("dashboard"))

    try:
        name = request.form["name"].strip()
        age = int(request.form["age"])
        pregnancies = int(request.form["pregnancies"])
        glucose = float(request.form["glucose"])
        bp = float(request.form["bp"])
        skin = float(request.form["skin"])
        insulin = float(request.form["insulin"])
        bmi = float(request.form["bmi"])
        dpf = float(request.form["dpf"])

        # Validate inputs
        validation_errors = validate_medical_input(name, age, pregnancies, glucose, bp, skin, insulin, bmi, dpf)
        if validation_errors:
            for error in validation_errors:
                flash(error, "error")
            return redirect(url_for("dashboard"))

        features = [pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]

    except (ValueError, KeyError) as e:
        flash("Invalid input data. Please check all fields and try again.", "error")
        return redirect(url_for("dashboard"))
    
    features_scaled = scaler.transform([features])

    # Get predictions from all three models
    pred_lr = model_lr.predict(features_scaled)[0]
    pred_rf = model_rf.predict(features_scaled)[0]
    pred_xgb = model_xgb.predict(features_scaled)[0]

    # Get probability scores for confidence
    prob_lr = model_lr.predict_proba(features_scaled)[0][1] * 100  # Probability of diabetic
    prob_rf = model_rf.predict_proba(features_scaled)[0][1] * 100
    prob_xgb = model_xgb.predict_proba(features_scaled)[0][1] * 100

    # Ensemble voting - majority wins
    votes = [pred_lr, pred_rf, pred_xgb]
    prediction = 1 if sum(votes) >= 2 else 0

    # Calculate model agreement
    model_agreement = sum(votes)  # 0, 1, 2, or 3
    agreement_key = {
        3: "agree_all",
        2: "agree_majority",
        1: "agree_majority",
        0: "agree_all"
    }[model_agreement]

    # Individual model predictions
    model_predictions = {
        'lr': {'prediction': 'Diabetic' if pred_lr == 1 else 'Not Diabetic', 'confidence': round(prob_lr, 1)},
        'rf': {'prediction': 'Diabetic' if pred_rf == 1 else 'Not Diabetic', 'confidence': round(prob_rf, 1)},
        'xgb': {'prediction': 'Diabetic' if pred_xgb == 1 else 'Not Diabetic', 'confidence': round(prob_xgb, 1)}
    }

    glucose, insulin, bmi = features[1], features[4], features[5]
    if glucose < 110 and bmi < 25:
        stage = "Normal"
        suggestion_keys = ["rec_maintain_diet", "rec_exercise_30", "rec_annual_checkup"]
        suggestion = "✅ Maintain healthy diet\n✅ Exercise 30 min daily\n✅ Annual checkup"
    elif 110 <= glucose <= 140 or bmi >= 25:
        stage = "Pre-Diabetic"
        suggestion_keys = ["rec_reduce_sugar", "rec_exercise_5", "rec_monitor_3"]
        suggestion = "⚠️ Reduce sugar\n⚠️ Exercise 5 days/week\n⚠️ Monitor glucose 3 months"
    elif glucose >= 140 and insulin < 30:
        stage = "Type 1 Diabetes"
        suggestion_keys = ["rec_consult_insulin", "rec_monitor_glucose", "rec_balanced_meals"]
        suggestion = "🚨 Consult doctor for insulin\n🚨 Blood glucose monitoring\n🚨 Balanced meals"
    else:
        stage = "Type 2 Diabetes"
        suggestion_keys = ["rec_medication", "rec_weight", "rec_consult"]
        suggestion = "🚨 Strict medication & diet\n🚨 Weight management\n🚨 Consult doctor"

    # Save patient
    try:
        conn = get_db_connection()
        if not conn:
            flash("Database error. Prediction successful but not saved.", "warning")
            return render_template("result.html",
                                 name=name,
                                 result="Diabetic" if prediction == 1 else "Not Diabetic",
                                 stage=stage,
                                 suggestion=suggestion,
                                 patient_id=None)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (user_id,name,age,pregnancies,glucose,bp,skin,insulin,bmi,dpf,result,stage,suggestion)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (session["user_id"], name, age, *features[:-1],
              "Diabetic" if prediction == 1 else "Not Diabetic", stage, suggestion))
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving prediction: {e}")
        flash("Prediction completed but could not be saved to history.", "warning")
        patient_id = None

    return render_template("result.html",
                         name=name,
                         result="Diabetic" if prediction == 1 else "Not Diabetic",
                         stage=stage,
                         suggestion=suggestion,
                         suggestion_keys=suggestion_keys,
                         patient_id=patient_id,
                         model_predictions=model_predictions,
                         agreement_key=agreement_key)

@app.route("/share-report/<int:patient_id>", methods=["POST"])
def share_report(patient_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    email = request.form["email"]
    
    conn = sqlite3.connect("diabetes_app.db")
    cursor = conn.cursor()
    
    # Check if user owns this report or is a doctor
    if session["role"] == "doctor":
        cursor.execute("""
            SELECT name, age, glucose, bmi, bp, result, stage, suggestion 
            FROM patients WHERE id=?
        """, (patient_id,))
    else:
        cursor.execute("""
            SELECT name, age, glucose, bmi, bp, result, stage, suggestion 
            FROM patients WHERE id=? AND user_id=?
        """, (patient_id, session["user_id"]))
    
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        flash("Report not found or access denied!", "error")
        return redirect(url_for("history"))
    
    # Generate PDF
    pdf_data = generate_pdf_report(patient)
    filename = f"{patient[0]}_diabetes_report.pdf"
    
    # Send email with PDF attachment
    subject = f"DiabetesAI Multi-Model Analysis Report - {patient[0]}"

    # Recalculate multi-model predictions for email
    try:
        features_for_pred = [0, patient[2], patient[4], 0, 0, patient[3], 0, patient[1]]
        features_scaled = scaler.transform([features_for_pred])

        pred_lr = model_lr.predict(features_scaled)[0]
        pred_rf = model_rf.predict(features_scaled)[0]
        pred_xgb = model_xgb.predict(features_scaled)[0]

        prob_lr = model_lr.predict_proba(features_scaled)[0][1] * 100
        prob_rf = model_rf.predict_proba(features_scaled)[0][1] * 100
        prob_xgb = model_xgb.predict_proba(features_scaled)[0][1] * 100

        votes = [pred_lr, pred_rf, pred_xgb]
        agreement = sum(votes)
        agreement_text = "All Models Agree (100%)" if agreement in [0, 3] else "Majority Consensus (67%)"

        model_info = f"""
    Multi-Model AI Analysis:
    - Model Agreement: {agreement_text}
    - Logistic Regression: {'Diabetic' if pred_lr == 1 else 'Not Diabetic'} ({prob_lr:.1f}% confidence)
    - Random Forest: {'Diabetic' if pred_rf == 1 else 'Not Diabetic'} ({prob_rf:.1f}% confidence)
    - XGBoost: {'Diabetic' if pred_xgb == 1 else 'Not Diabetic'} ({prob_xgb:.1f}% confidence)
    """
    except:
        model_info = ""

    body = f"""
    Hello,

    Please find attached the diabetes prediction report for {patient[0]}.

    Report Summary:
    - Final Diagnosis (Ensemble): {patient[5]}
    - Stage: {patient[6]}
    - Age: {patient[1]} years
    {model_info}
    IMPORTANT: This is an AI-generated prediction for informational purposes only.
    Please consult with a healthcare professional for proper medical advice.

    Best regards,
    DiabetesAI Team
    """
    
    if send_email(email, subject, body, pdf_data, filename):
        flash(f"Report sent successfully to {email}!", "success")
    else:
        if not EMAIL_CONFIGURED:
            flash("Email functionality is not configured. Please download the PDF report instead.", "error")
        else:
            flash("Failed to send email. Please try again.", "error")
    
    return redirect(url_for("history"))

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return render_template("history.html", patients=[], stats=None)

        cursor = conn.cursor()

        # Get patient records
        cursor.execute("""
            SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion, p.created_at
            FROM patients p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id=?
            ORDER BY p.created_at DESC
        """, (session["user_id"],))
        data = cursor.fetchall()

        # Calculate statistics for trends
        cursor.execute("""
            SELECT
                COUNT(*) as total_tests,
                AVG(glucose) as avg_glucose,
                AVG(bmi) as avg_bmi,
                AVG(bp) as avg_bp,
                MIN(glucose) as min_glucose,
                MAX(glucose) as max_glucose,
                MIN(bmi) as min_bmi,
                MAX(bmi) as max_bmi
            FROM patients
            WHERE user_id=?
        """, (session["user_id"],))
        stats_row = cursor.fetchone()

        # Get stage distribution
        cursor.execute("""
            SELECT stage, COUNT(*) as count
            FROM patients
            WHERE user_id=?
            GROUP BY stage
        """, (session["user_id"],))
        stage_dist = cursor.fetchall()

        # Get recent trend (last 5 records for chart)
        cursor.execute("""
            SELECT glucose, bmi, created_at
            FROM patients
            WHERE user_id=?
            ORDER BY created_at DESC
            LIMIT 5
        """, (session["user_id"],))
        trend_data = cursor.fetchall()

        conn.close()

        stats = {
            'total_tests': stats_row[0] if stats_row else 0,
            'avg_glucose': round(stats_row[1], 1) if stats_row and stats_row[1] else 0,
            'avg_bmi': round(stats_row[2], 1) if stats_row and stats_row[2] else 0,
            'avg_bp': round(stats_row[3], 1) if stats_row and stats_row[3] else 0,
            'min_glucose': round(stats_row[4], 1) if stats_row and stats_row[4] else 0,
            'max_glucose': round(stats_row[5], 1) if stats_row and stats_row[5] else 0,
            'min_bmi': round(stats_row[6], 1) if stats_row and stats_row[6] else 0,
            'max_bmi': round(stats_row[7], 1) if stats_row and stats_row[7] else 0,
            'stage_distribution': {row[0]: row[1] for row in stage_dist},
            'trend_glucose': [row[0] for row in reversed(trend_data)],
            'trend_bmi': [row[1] for row in reversed(trend_data)],
            'trend_dates': [row[2][:10] if row[2] else '' for row in reversed(trend_data)]
        }

        return render_template("history.html", patients=data, stats=stats)

    except Exception as e:
        print(f"History error: {e}")
        flash("Error loading history.", "error")
        return render_template("history.html", patients=[], stats=None)

@app.route("/download_report/<int:patient_id>")
def download_report(patient_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect("diabetes_app.db")
    cursor = conn.cursor()
    
    # Check if user owns this report or is a doctor
    if session["role"] == "doctor":
        cursor.execute("""
            SELECT name, age, glucose, bmi, bp, result, stage, suggestion 
            FROM patients WHERE id=?
        """, (patient_id,))
    else:
        cursor.execute("""
            SELECT name, age, glucose, bmi, bp, result, stage, suggestion 
            FROM patients WHERE id=? AND user_id=?
        """, (patient_id, session["user_id"]))
    
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        flash("Report not found or access denied!", "error")
        return redirect(url_for("history"))
    
    pdf_data = generate_pdf_report(patient)
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={patient[0]}_report.pdf'
    return response

@app.route("/doctor_dashboard")
def doctor_dashboard():
    if "user_id" not in session or session["role"] != "doctor":
        return redirect(url_for("login"))

    try:
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = 15  # Records per page

        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return render_template("doctor_dashboard.html")

        cursor = conn.cursor()

        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        cursor.execute("SELECT result, COUNT(*) FROM patients GROUP BY result")
        result_data = cursor.fetchall()
        diabetic_count = 0
        non_diabetic_count = 0
        for row in result_data:
            if row[0] == "Diabetic":
                diabetic_count = row[1]
            else:
                non_diabetic_count = row[1]

        cursor.execute("SELECT stage, COUNT(*) FROM patients GROUP BY stage")
        stage_data = cursor.fetchall()
        stages = {stage: 0 for stage in ["Normal", "Pre-Diabetic", "Type 1 Diabetes", "Type 2 Diabetes"]}
        for row in stage_data:
            stages[row[0]] = row[1]

        cursor.execute("SELECT AVG(glucose), AVG(bmi) FROM patients")
        avg_result = cursor.fetchone()
        avg_glucose = avg_result[0] if avg_result[0] else 0
        avg_bmi = avg_result[1] if avg_result[1] else 0

        # Get total count for pagination
        if search:
            cursor.execute("""
                SELECT COUNT(*) FROM patients p
                JOIN users u ON p.user_id = u.id
                WHERE p.name LIKE ? OR u.username LIKE ? OR p.result LIKE ? OR p.stage LIKE ?
            """, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            cursor.execute("SELECT COUNT(*) FROM patients")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records + per_page - 1) // per_page  # Ceiling division

        # Get patient records with search and pagination
        offset = (page - 1) * per_page
        if search:
            cursor.execute("""
                SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion
                FROM patients p
                JOIN users u ON p.user_id = u.id
                WHERE p.name LIKE ? OR u.username LIKE ? OR p.result LIKE ? OR p.stage LIKE ?
                ORDER BY p.id DESC
                LIMIT ? OFFSET ?
            """, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
        else:
            cursor.execute("""
                SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion
                FROM patients p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.id DESC
                LIMIT ? OFFSET ?
            """, (per_page, offset))

        patients = cursor.fetchall()
        conn.close()

        return render_template("doctor_dashboard.html",
                             total_patients=total_patients,
                             diabetic_count=diabetic_count,
                             non_diabetic_count=non_diabetic_count,
                             avg_glucose=round(avg_glucose, 2),
                             avg_bmi=round(avg_bmi, 2),
                             stages=stages,
                             patients=patients,
                             search=search,
                             page=page,
                             total_pages=total_pages,
                             total_records=total_records)

    except Exception as e:
        print(f"Doctor dashboard error: {e}")
        flash("Error loading dashboard.", "error")
        return render_template("doctor_dashboard.html")

@app.route("/doctor/export-csv")
def doctor_export_csv():
    """Export all patient data to CSV"""
    if "user_id" not in session or session["role"] != "doctor":
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return redirect(url_for("doctor_dashboard"))

        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, u.username, p.name, p.age, p.pregnancies, p.glucose, p.bp, p.skin,
                   p.insulin, p.bmi, p.dpf, p.result, p.stage, p.created_at
            FROM patients p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.id ASC
        """)
        patients = cursor.fetchall()
        conn.close()

        # Create CSV
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Username', 'Patient Name', 'Age', 'Pregnancies', 'Glucose',
                        'Blood Pressure', 'Skin Thickness', 'Insulin', 'BMI', 'DPF',
                        'Result', 'Stage', 'Date'])

        # Write data with formatted date
        for patient in patients:
            patient_list = list(patient)
            # Format the date (last column) to just date without time for Excel compatibility
            if patient_list[-1]:
                try:
                    # Extract just the date part (YYYY-MM-DD) to make it shorter
                    date_str = str(patient_list[-1])
                    if ' ' in date_str:
                        # Take only the date part, not the time
                        date_str = date_str.split(' ')[0]
                    patient_list[-1] = date_str
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    patient_list[-1] = str(patient_list[-1])[:10]  # First 10 chars (date only)
            writer.writerow(patient_list)

        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=patient_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

        return response

    except Exception as e:
        print(f"CSV export error: {e}")
        flash("Error exporting data.", "error")
        return redirect(url_for("doctor_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html'), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)
