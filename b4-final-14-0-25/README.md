# 🏥 Diabetes Prediction App

AI-powered diabetes risk assessment tool with role-based access for patients, doctors, and administrators.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![ML](https://img.shields.io/badge/ML-scikit--learn-orange.svg)

---

## ✨ Features

### 🔐 **Multi-Role Access**
- **Patients**: Submit health data, get AI predictions, view history with trends
- **Doctors**: Access patient records, analytics dashboard, export data
- **Admins**: User management, system statistics, audit logs

### 🤖 **AI-Powered Predictions**
- Logistic Regression model trained on PIMA Indian Diabetes Dataset
- Input validation with medical data range checking
- Risk stratification (Normal, Pre-Diabetic, Type 1/2 Diabetes)
- Personalized health recommendations

### 📊 **Analytics & Visualization**
- Patient health trends with Chart.js
- Statistical insights (avg glucose, BMI, BP)
- Doctor dashboard with pagination
- CSV data export

### 🔒 **Security Features**
- Environment-based configuration
- Strong password requirements
- Email verification (optional)
- Password reset functionality
- Secure session management

---

## 📸 Screenshots

### Patient Dashboard
View predictions, health trends, and download/share PDF reports.

### Doctor Dashboard
Access all patient records with search, pagination, and CSV export.

### Analytics
Interactive charts showing glucose and BMI trends over time.

---

## 🚀 Quick Start

### **Option 1: Automated Setup (Recommended)**

#### **macOS/Linux:**
```bash
git clone <your-repo-url>
cd Diabetesprediction
chmod +x setup.sh
./setup.sh
```

#### **Windows:**
```cmd
git clone <your-repo-url>
cd Diabetesprediction
setup.bat
```

### **Option 2: Manual Setup**

#### **1. Clone the Repository**
```bash
git clone <your-repo-url>
cd Diabetesprediction
```

#### **2. Create Virtual Environment**
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Configure Environment**
```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

#### **5. Train ML Model**
```bash
python3 train_model.py
```

#### **6. Run the Application**
```bash
python3 app.py
```

#### **7. Access the App**
Open your browser: **http://127.0.0.1:8080**

---

## ⚙️ Configuration

### **Environment Variables (.env)**

```bash
# Flask Secret Key (generate new one!)
FLASK_SECRET_KEY=your-secret-key

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourStrongPass123!

# Doctor Registration Key
DOCTOR_SECRET_KEY=YourSecretKey2025!

# Email (Optional)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_CONFIGURED=False  # Set to True to enable
```

### **Generate Secure Keys**
```bash
# Flask secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Random password
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(16)))"
```

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB free space

### **Python Dependencies**
See `requirements.txt` for complete list:
- Flask 3.0.0
- scikit-learn 1.3.2
- pandas 2.1.4
- reportlab 4.0.7
- python-dotenv 1.0.0

---

## 🎯 Usage Guide

### **For Patients**

1. **Register Account**
   - Visit http://127.0.0.1:8080
   - Click "Register" → Choose "Patient"
   - Use strong password (min 8 chars, mixed case, numbers, symbols)

2. **Submit Prediction**
   - Login → Dashboard → "New Prediction"
   - Enter medical data (glucose, BMI, age, etc.)
   - Get instant AI-powered risk assessment

3. **View History**
   - Dashboard → "History"
   - See all past predictions
   - View health trends chart
   - Download/share PDF reports

### **For Doctors**

1. **Register Account**
   - Click "Register" → Choose "Doctor"
   - Enter doctor secret key from `.env` file
   - Complete registration

2. **Access Patient Records**
   - Login → Doctor Dashboard
   - Search patients by name/username
   - Navigate with pagination (15 records/page)
   - View detailed analytics

3. **Export Data**
   - Click "Export CSV" button
   - Download complete patient database
   - Analyze in Excel/Google Sheets

### **For Admins**

1. **Login**
   - Visit http://127.0.0.1:8080/admin-login
   - Use credentials from `.env`

2. **Manage System**
   - View user statistics
   - Delete user accounts
   - Review audit logs
   - Monitor system health

---

## 🗂️ Project Structure

```
Diabetesprediction/
├── app.py                      # Main Flask application
├── train_model.py              # ML model training script
├── requirements.txt            # Python dependencies
├── setup.sh                    # macOS/Linux setup script
├── setup.bat                   # Windows setup script
├── .env.example                # Environment variables template
├── .env                        # Your actual config (git-ignored)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── IMPROVEMENTS.md             # Recent improvements log
├── CLAUDE.md                   # AI assistant instructions
│
├── diabetes.csv                # PIMA dataset (768 records)
├── diabetes_model.pkl          # Trained ML model
├── scaler.pkl                  # Feature scaler
├── diabetes_app.db             # SQLite database
│
└── templates/                  # HTML templates
    ├── base.html               # Base template
    ├── landing.html            # Homepage
    ├── login.html              # Login page
    ├── register.html           # Registration
    ├── index.html              # Patient dashboard
    ├── result.html             # Prediction results
    ├── history.html            # Patient history (with charts)
    ├── doctor_dashboard.html   # Doctor interface
    ├── admin_login.html        # Admin login
    ├── admin_dashboard.html    # Admin panel
    ├── forgot_password.html    # Password reset request
    ├── reset_password.html     # Password reset form
    └── 404.html                # Error page
```

---

## 🔧 Advanced Configuration

### **Change Pagination Limit**
Edit `app.py` line 994:
```python
per_page = 20  # Default: 15
```

### **Customize Validation Ranges**
Edit `app.py` lines 628-668:
```python
def validate_medical_input(...):
    # Modify ranges as needed
    if not (0 <= glucose <= 400):
        errors.append("Glucose must be between 0 and 400 mg/dL")
```

### **Switch Database to PostgreSQL**
```python
# Install: pip install psycopg2-binary
# Update app.py connection string:
conn = psycopg2.connect(
    "postgresql://user:pass@localhost/diabetes_db"
)
```

---

## 🧪 Testing

### **Run Manual Tests**
```bash
# Test patient registration
curl -X POST http://127.0.0.1:8080/register \
  -d "username=test&email=test@test.com&password=Test123!&role=patient"

# Test login
curl -X POST http://127.0.0.1:8080/login \
  -d "username=test&password=Test123!"
```

### **Check Database**
```bash
sqlite3 diabetes_app.db "SELECT COUNT(*) FROM users;"
sqlite3 diabetes_app.db "SELECT COUNT(*) FROM patients;"
```

---

## 🐛 Troubleshooting

### **"Model files not found"**
```bash
# Run training script
python3 train_model.py
```

### **"Database connection error"**
```bash
# Reinitialize database
python3 -c "from app import init_db; init_db()"
```

### **"Email sending failed"**
- Check `.env` file has correct Gmail credentials
- Ensure 2FA is enabled and app password is generated
- Set `EMAIL_CONFIGURED=True` in `.env`

### **"Import error: No module named..."**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### **Port 8080 already in use**
Edit `app.py` line 1133:
```python
app.run(debug=True, host='127.0.0.1', port=5000)  # Change port
```

---

## 📊 Model Information

- **Dataset**: PIMA Indian Diabetes Dataset
- **Algorithm**: Logistic Regression (scikit-learn)
- **Features**: 8 medical indicators
- **Accuracy**: ~77% on test set
- **Training Time**: ~30 seconds

### **Input Features**
| Feature | Range | Unit |
|---------|-------|------|
| Pregnancies | 0-20 | count |
| Glucose | 0-400 | mg/dL |
| Blood Pressure | 40-200 | mmHg |
| Skin Thickness | 0-100 | mm |
| Insulin | 0-900 | µU/mL |
| BMI | 10-70 | kg/m² |
| Diabetes Pedigree Function | 0-3 | ratio |
| Age | 1-120 | years |

---

## 🔐 Security Best Practices

- ✅ Change all default credentials in `.env`
- ✅ Never commit `.env` to version control
- ✅ Use HTTPS in production (get SSL certificate)
- ✅ Enable email verification for user accounts
- ✅ Implement rate limiting (TODO)
- ✅ Regular security audits
- ✅ Keep dependencies updated

---

## 🚀 Deployment

### **Production Checklist**

1. **Update Configuration**
   - [ ] Change Flask secret key
   - [ ] Change admin password
   - [ ] Change doctor secret key
   - [ ] Configure email (optional)
   - [ ] Set `DEBUG=False` in production

2. **Use Production Server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

3. **Set Up Reverse Proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Enable HTTPS**
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See `IMPROVEMENTS.md` for recent changes
- **Email**: Contact project maintainer

---

## 🙏 Acknowledgments

- **Dataset**: PIMA Indian Diabetes Dataset (Kaggle)
- **Framework**: Flask
- **ML Library**: scikit-learn
- **Charts**: Chart.js

---

## 📈 Roadmap

- [ ] Add multi-model ensemble (Random Forest + XGBoost)
- [ ] Implement real-time notifications
- [ ] Mobile-responsive design improvements
- [ ] API for external integrations
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Automated model retraining

---

**Built with ❤️ using Flask and Machine Learning**

*Last Updated: 2025-10-04*
