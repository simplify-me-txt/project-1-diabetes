from flask import Flask, render_template, request, redirect, session, url_for, make_response
import sqlite3
import joblib
import numpy as np
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load ML model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

# Database initialization
def init_db():
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
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
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# Home - Landing page
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

# Login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("diabetes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username,password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"]=user[0]
            session["role"]=user[1]
            return redirect(url_for("dashboard"))
        else:
            return "⌘ Invalid credentials!"
    return render_template("login.html")

# Register
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]   # safe now, form always has it
        try:
            conn = sqlite3.connect("diabetes.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",(username,password,role))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            return "⌘ Username already exists!"
    return render_template("register.html",
                           page_title="Register",
                           button_text="Register",
                           show_role=True)   # 👈 force role field to appear

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# Prediction
@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))
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
    """, (session["user_id"],name,age,*features[:-1], "Diabetic" if prediction==1 else "Not Diabetic", stage, suggestion))
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return render_template("result.html", name=name, result="Diabetic" if prediction==1 else "Not Diabetic",
                           stage=stage, suggestion=suggestion, patient_id=patient_id)

# History - FIXED: Only show user's own data unless they're a doctor
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()

    # Users can only see their own data
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

# Download PDF - FIXED: Users can only download their own reports
@app.route("/download_report/<int:patient_id>")
def download_report(patient_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    
    # Check if user owns this report or is a doctor
    if session["role"] == "doctor":
        cursor.execute("SELECT name, age, glucose, bmi, bp, result, stage, suggestion FROM patients WHERE id=?",(patient_id,))
    else:
        cursor.execute("SELECT name, age, glucose, bmi, bp, result, stage, suggestion FROM patients WHERE id=? AND user_id=?",(patient_id, session["user_id"]))
    
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        return "⌘ Report not found or access denied!"
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180,750,"🏥 Diabetes Prediction Report")
    c.setFont("Helvetica",12)
    c.drawString(50,700,f"Patient Name: {patient[0]}")
    c.drawString(50,680,f"Age: {patient[1]}")
    c.drawString(50,660,f"Glucose Level: {patient[2]}")
    c.drawString(50,640,f"BMI: {patient[3]}")
    c.drawString(50,620,f"Blood Pressure: {patient[4]}")
    c.drawString(50,600,f"Result: {patient[5]}")
    c.drawString(50,580,f"Stage: {patient[6]}")
    c.drawString(50,540,"Suggestions:")
    text_obj = c.beginText(70,520)
    for line in patient[7].split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()
    c.save()
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition']=f'attachment; filename={patient[0]}_report.pdf'
    return response

# Doctor Dashboard - FIXED: Added search functionality and proper patient list
@app.route("/doctor_dashboard")
def doctor_dashboard():
    if "user_id" not in session or session["role"]!="doctor":
        return redirect(url_for("login"))
    
    search = request.args.get('search', '').strip()
    
    conn = sqlite3.connect("diabetes.db")
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]
    
    cursor.execute("SELECT result, COUNT(*) FROM patients GROUP BY result")
    result_data = cursor.fetchall()
    diabetic_count=0
    non_diabetic_count=0
    for row in result_data:
        if row[0]=="Diabetic": diabetic_count=row[1]
        else: non_diabetic_count=row[1]
    
    cursor.execute("SELECT stage, COUNT(*) FROM patients GROUP BY stage")
    stage_data = cursor.fetchall()
    stages = {stage:0 for stage in ["Normal","Pre-Diabetic","Type 1 Diabetes","Type 2 Diabetes"]}
    for row in stage_data:
        stages[row[0]]=row[1]
    
    cursor.execute("SELECT AVG(glucose), AVG(bmi) FROM patients")
    avg_glucose, avg_bmi = cursor.fetchone()
    
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
                           avg_glucose=round(avg_glucose,2) if avg_glucose else 0,
                           avg_bmi=round(avg_bmi,2) if avg_bmi else 0,
                           stages=stages,
                           patients=patients,
                           search=search)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html'), 500

if __name__=="__main__":
    init_db()
    app.run(debug=True)
