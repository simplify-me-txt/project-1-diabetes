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

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuration
DOCTOR_SECRET_KEY = "HEALTH2025"  # Secret key for doctor registration
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Change this in production

# Email configuration (configure these with your email settings)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USERNAME = "your-email@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "your-app-password"     # Replace with your app password

# Load ML model & scaler
try:
    model = joblib.load("diabetes_model.pkl")
    scaler = joblib.load("scaler.pkl")
except FileNotFoundError:
    print("Warning: ML model files not found. Please run train_model.py first.")
    model = None
    scaler = None

# Database initialization
def init_db():
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    
    # Users table with email and reset token
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
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

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def send_email(to_email, subject, body, attachment_data=None, attachment_name=None):
    """Send email with optional PDF attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_name}'
            )
            msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

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
    c.setFont("Helvetica-Italic", 10)
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
        username_or_email = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)
        
        conn = sqlite3.connect("diabetes.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, role, username FROM users 
            WHERE (username=? OR email=?) AND password=?
        """, (username_or_email, username_or_email, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["user_id"] = user[0]
            session["role"] = user[1]
            session["username"] = user[2]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "error")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        
        # Check doctor secret key
        if role == "doctor":
            secret_key = request.form.get("secret_key", "")
            if secret_key != DOCTOR_SECRET_KEY:
                flash("Invalid doctor secret key!", "error")
                return render_template("register.html")
        
        hashed_password = hash_password(password)
        
        try:
            conn = sqlite3.connect("diabetes.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password, role) 
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_password, role))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "error")
    
    return render_template("register.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        
        conn = sqlite3.connect("diabetes.db")
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
    conn = sqlite3.connect("diabetes.db")
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
    
    conn = sqlite3.connect("diabetes.db")
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
    
    conn = sqlite3.connect("diabetes.db")
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

@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if not model or not scaler:
        flash("Prediction model not available. Please contact administrator.", "error")
        return redirect(url_for("dashboard"))
    
    name = request.form["name"]
    age = int(request.form["age"])
    features = [
        int(request.form["pregnancies"]),
        float(request.form["glucose"]),
        float(request.form["bp"]),
        float(request.form["skin"]),
        float(request.form["insulin"]),
        float(request.form["bmi"]),
        float(request.form["dpf"]),
        age
    ]
    
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
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (user_id,name,age,pregnancies,glucose,bp,skin,insulin,bmi,dpf,result,stage,suggestion)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (session["user_id"], name, age, *features[:-1], 
          "Diabetic" if prediction == 1 else "Not Diabetic", stage, suggestion))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()

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
    
    conn = sqlite3.connect("diabetes.db")
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
        flash("Failed to send email. Please try again.", "error")
    
    return redirect(url_for("history"))

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion
        FROM patients p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id=?
        ORDER BY p.id DESC
    """, (session["user_id"],))

    data = cursor.fetchall()
    conn.close()

    return render_template("history.html", patients=data)

@app.route("/download_report/<int:patient_id>")
def download_report(patient_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect("diabetes.db")
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
    
    search = request.args.get('search', '').strip()
    
    conn = sqlite3.connect("diabetes.db")
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
    
    # Get patient records with search
    if search:
        cursor.execute("""
            SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion
            FROM patients p
            JOIN users u ON p.user_id = u.id
            WHERE p.name LIKE ? OR u.username LIKE ? OR p.result LIKE ? OR p.stage LIKE ?
            ORDER BY p.id DESC
        """, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("""
            SELECT p.id, u.username, p.name, p.age, p.glucose, p.bmi, p.bp, p.result, p.stage, p.suggestion
            FROM patients p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.id DESC
        """)
    
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
                         search=search)

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
    app.run(debug=True)
