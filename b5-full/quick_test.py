import smtplib

email = "diabetespredictiontool@gmail.com"
password = "ciniikghomiautsi"  # Your exact password

try:
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    server.set_debuglevel(1)  # Shows detailed output
    server.starttls()
    print("TLS started successfully")
    server.login(email, password)
    print("✅ LOGIN SUCCESSFUL!")
    server.quit()
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"Details: {e}")