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

# Load ML model & scaler
try:
    model = joblib.load("diabetes_model.pkl")
    scaler = joblib.load("scaler.pkl")
except FileNotFoundError:
    print("Warning: ML model files not found. Please run train_model.py first.")
    model = None
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
    """Generate PDF report and return as bytes"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, 750, "🏥 Diabetes Prediction Report")
    
    # Patient Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 700, "Patient Information:")
    
    c.setFont("Helvetica", 12)
    y_position = 680
    fields = [
        ("Patient Name", patient_data[0]),
        ("Age", f"{patient_data[1]} years"),
        ("Glucose Level", patient_data[2]),
        ("BMI", patient_data[3]),
        ("Blood Pressure", patient_data[4]),
        ("Result", patient_data[5]),
        ("Stage", patient_data[6])
    ]
    
    for field, value in fields:
        c.drawString(50, y_position, f"{field}: {value}")
        y_position -= 20
    
    # Suggestions
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position - 20, "Medical Recommendations:")
    
    c.setFont("Helvetica", 11)
    text_obj = c.beginText(70, y_position - 45)
    for line in patient_data[7].split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    
    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, 35, "This report is for informational purposes only. Please consult a healthcare professional.")
    
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
    prediction = model.predict(features_scaled)[0]

    glucose, insulin, bmi = features[1], features[4], features[5]
    if glucose < 110 and bmi < 25:
        stage = "Normal"
        suggestion = "✅ Maintain healthy diet\n✅ Exercise 30 min daily\n✅ Annual checkup"
    elif 110 <= glucose <= 140 or bmi >= 25:
        stage = "Pre-Diabetic"
        suggestion = "⚠️ Reduce sugar\n⚠️ Exercise 5 days/week\n⚠️ Monitor glucose 3 months"
    elif glucose >= 140 and insulin < 30:
        stage = "Type 1 Diabetes"
        suggestion = "🚨 Consult doctor for insulin\n🚨 Blood glucose monitoring\n🚨 Balanced meals"
    else:
        stage = "Type 2 Diabetes"
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
                         patient_id=patient_id)

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
    subject = f"Diabetes Prediction Report - {patient[0]}"
    body = f"""
    Hello,
    
    Please find attached the diabetes prediction report for {patient[0]}.
    
    Report Summary:
    - Result: {patient[5]}
    - Stage: {patient[6]}
    - Age: {patient[1]} years
    
    Please consult with a healthcare professional for proper medical advice.
    
    Best regards,
    Diabetes Predictor Team
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
            ORDER BY p.created_at DESC
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

        # Write data
        for patient in patients:
            writer.writerow(patient)

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
    app.run(debug=True, host='127.0.0.1', port=8080)