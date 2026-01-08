#!/bin/bash

# Diabetes Health App - Production Deployment Script
# This script helps configure the app for production with real email sending

echo "🚀 DIABETES HEALTH APP - PRODUCTION SETUP"
echo "=========================================="
echo ""

# Check if environment variables are set
if [ -z "$EMAIL_USERNAME" ] || [ -z "$EMAIL_PASSWORD" ]; then
    echo "⚠️  Email configuration required for production!"
    echo ""
    echo "To enable real email sending, set these environment variables:"
    echo ""
    echo "For Gmail:"
    echo "export EMAIL_USERNAME=\"your-app-email@gmail.com\""
    echo "export EMAIL_PASSWORD=\"your-gmail-app-password\""
    echo "export EMAIL_FROM_NAME=\"Diabetes Health App\""
    echo ""
    echo "For Outlook:"
    echo "export EMAIL_USERNAME=\"your-app-email@outlook.com\""
    echo "export EMAIL_PASSWORD=\"your-outlook-password\""
    echo "export EMAIL_FROM_NAME=\"Diabetes Health App\""
    echo ""
    echo "Gmail App Password Setup:"
    echo "1. Go to myaccount.google.com"
    echo "2. Security → 2-Step Verification (enable it)"
    echo "3. Security → App passwords"
    echo "4. Generate password for 'Mail'"
    echo "5. Use that 16-character password"
    echo ""
    echo "Then run this script again or start the app:"
    echo "python3 app.py"
    echo ""
else
    echo "✅ Email configuration found!"
    echo "📧 Email Username: $EMAIL_USERNAME"
    echo "👤 From Name: ${EMAIL_FROM_NAME:-Diabetes Health App}"
    echo ""
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip3 install flask
fi

# Check for other dependencies
echo "📦 Checking dependencies..."
python3 -c "
import sys
missing = []
try: import flask
except: missing.append('flask')
try: import sqlite3
except: missing.append('sqlite3')
try: import pandas
except: missing.append('pandas')
try: import sklearn
except: missing.append('scikit-learn')
try: import reportlab
except: missing.append('reportlab')

if missing:
    print('Missing packages:', ', '.join(missing))
    print('Install with: pip3 install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All dependencies satisfied')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Please install missing dependencies and run again"
    exit 1
fi

echo ""
echo "🎯 Starting Diabetes Health App..."
echo "🌐 Access at: http://localhost:5000"
echo "📊 Admin login: admin / admin123"
echo "👨‍⚕️ Doctor login: doctor1 / doctor123 (with secret key: HEALTH2025)"
echo ""

# Start the Flask app
python3 app.py