# ⚡ Quick Start Guide

Get the Diabetes Prediction App running in **under 5 minutes**!

---

## 🚀 For the Impatient

### **macOS/Linux (One Command)**
```bash
git clone <https://github.com/simplify-me-txt/project-1-diabetes/tree/main/b3-4.10.25> && cd Diabetesprediction && chmod +x setup.sh && ./setup.sh && source venv/bin/activate && python3 app.py
```

### **Windows (One Command)**
```cmd
git clone <repo-url> && cd Diabetesprediction && setup.bat && python app.py
```

Then open: **http://127.0.0.1:8080** 🎉

---

## 📦 Step-by-Step (3 Steps)

### **Step 1: Setup**
```bash
# Clone and run setup
git clone <repo-url>
cd Diabetesprediction
./setup.sh          # macOS/Linux
# OR
setup.bat           # Windows
```

### **Step 2: Configure (Optional)**
```bash
# Edit .env if you want email features
nano .env
# Change EMAIL_CONFIGURED=True
```

### **Step 3: Run**
```bash
# macOS/Linux
source venv/bin/activate
python3 app.py

# Windows
venv\Scripts\activate
python app.py
```

Visit: **http://127.0.0.1:8080**

---

## 🎮 Try It Out

### **Register as Patient**
1. Click "Register"
2. Username: `testuser`
3. Email: `test@example.com`
4. Password: `Test123!` (must be strong!)
5. Role: Patient

### **Make a Prediction**
1. Login
2. Dashboard → "New Prediction"
3. Fill in sample data:
   - Name: John Doe
   - Age: 45
   - Glucose: 120
   - BMI: 28
   - Blood Pressure: 80
   - (fill other fields)
4. Submit → Get AI prediction!

### **View Trends**
1. Make 2-3 more predictions
2. Go to "History"
3. See health trends chart 📊

---

## 👨‍⚕️ Try Doctor Account

### **Register as Doctor**
1. Register → Choose "Doctor"
2. Secret Key: `HEALTH2025` (from .env)
3. Login → Access patient records

### **Export Data**
1. Doctor Dashboard
2. Click "Export CSV"
3. Download all data

---

## 🔐 Try Admin Panel

1. Visit: http://127.0.0.1:8080/admin-login
2. Username: `admin`
3. Password: `admin123` (from .env)
4. Manage users & view stats

---

## ⚠️ Common Issues

### **"Model files not found"**
```bash
python3 train_model.py
```

### **Port 8080 in use**
Edit `app.py` line 1133:
```python
app.run(debug=True, host='127.0.0.1', port=5000)
```

### **Permission denied (macOS/Linux)**
```bash
chmod +x setup.sh
```

---

## 📝 Default Credentials

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| Admin | admin | admin123 | Change in .env |
| Doctor Key | - | HEALTH2025 | Change in .env |

⚠️ **Change these before production!**

---

## 🎯 Next Steps

- [ ] Change default passwords in `.env`
- [ ] Try all features (predict, history, export)
- [ ] Read full README.md for advanced config
- [ ] Configure email (optional)
- [ ] Deploy to production

---

## 🆘 Need Help?

- Full docs: See `README.md`
- Recent changes: See `IMPROVEMENTS.md`
- Issues: Check troubleshooting section in README

---

**That's it! You're ready to go! 🚀**
