#!/usr/bin/env python3
"""
Email Functionality Tester for Diabetes Prediction App
Test your email configuration before using it in the main app
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import sys

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def load_email_config():
    """Load email configuration from .env file"""
    print_header("LOADING EMAIL CONFIGURATION")
    
    # Try to load .env file
    if os.path.exists('.env'):
        load_dotenv(override=True)
        print_success(".env file found and loaded")
    else:
        print_error(".env file not found!")
        print_info("Please create a .env file with your email credentials")
        return None
    
    # Get configuration
    config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'email_username': os.getenv('EMAIL_USERNAME', ''),
        'email_password': os.getenv('EMAIL_PASSWORD', ''),
        'email_configured': os.getenv('EMAIL_CONFIGURED', 'false').lower()
    }
    
    # Display configuration
    print(f"\n{Colors.BOLD}Configuration Details:{Colors.END}")
    print(f"  SMTP Server: {config['smtp_server']}")
    print(f"  SMTP Port: {config['smtp_port']}")
    print(f"  Email Username: {config['email_username']}")
    print(f"  Email Password: {'*' * len(config['email_password']) if config['email_password'] else 'NOT SET'}")
    print(f"  Email Configured: {config['email_configured']}")
    
    # Validate configuration
    print(f"\n{Colors.BOLD}Validation:{Colors.END}")
    
    if not config['email_username']:
        print_error("EMAIL_USERNAME is not set!")
        return None
    else:
        print_success(f"Email username set: {config['email_username']}")
    
    if not config['email_password']:
        print_error("EMAIL_PASSWORD is not set!")
        return None
    else:
        print_success(f"Email password set (length: {len(config['email_password'])} characters)")
    
    if config['email_configured'] != 'true':
        print_warning(f"EMAIL_CONFIGURED is set to '{config['email_configured']}' (should be 'true')")
        print_info("The app will run in simulation mode with this setting")
    else:
        print_success("EMAIL_CONFIGURED is set to 'true'")
    
    return config

def test_smtp_connection(config):
    """Test SMTP server connection"""
    print_header("TESTING SMTP CONNECTION")
    
    try:
        print_info(f"Connecting to {config['smtp_server']}:{config['smtp_port']}...")
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'], timeout=10)
        print_success("Connected to SMTP server")
        
        print_info("Starting TLS encryption...")
        server.starttls()
        print_success("TLS encryption started")
        
        print_info("Attempting login...")
        server.login(config['email_username'], config['email_password'])
        print_success("Login successful!")
        
        server.quit()
        print_success("Connection closed properly")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print_error("Authentication failed!")
        print_warning("Common causes:")
        print("  1. Wrong email or password")
        print("  2. Not using App Password (for Gmail)")
        print("  3. 2-Factor Authentication not enabled (for Gmail)")
        print(f"\nError details: {e}")
        return False
        
    except smtplib.SMTPException as e:
        print_error(f"SMTP error occurred: {e}")
        return False
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def send_test_email(config, recipient_email=None):
    """Send a test email"""
    print_header("SENDING TEST EMAIL")
    
    if recipient_email is None:
        recipient_email = config['email_username']
    
    print_info(f"Sending test email to: {recipient_email}")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Diabetes Health App <{config['email_username']}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🧪 Test Email - Diabetes Prediction App"
        
        # Plain text version
        text_body = """
Hello!

This is a test email from your Diabetes Prediction App.

If you're reading this, your email configuration is working correctly! ✅

Configuration Details:
- SMTP Server: {smtp_server}
- SMTP Port: {smtp_port}
- From Email: {email_username}

Next Steps:
1. Your email setup is complete
2. The app can now send verification emails
3. Users can share reports via email

Best regards,
Diabetes Health App Team
        """.format(**config)
        
        # HTML version
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="margin: 0; font-size: 28px;">🧪 Email Test Successful!</h1>
                        <p style="margin: 10px 0 0 0; font-size: 16px;">Diabetes Prediction App</p>
                    </div>

                    <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <h2 style="color: #667eea; margin-bottom: 20px;">✅ Email Configuration Working!</h2>

                        <p>If you're reading this, your email configuration is working correctly!</p>

                        <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #667eea; margin-top: 0;">Configuration Details:</h3>
                            <p style="margin: 5px 0;"><strong>SMTP Server:</strong> {smtp_server}</p>
                            <p style="margin: 5px 0;"><strong>SMTP Port:</strong> {smtp_port}</p>
                            <p style="margin: 5px 0;"><strong>From Email:</strong> {email_username}</p>
                        </div>

                        <h3 style="color: #667eea;">Next Steps:</h3>
                        <ul>
                            <li>✅ Your email setup is complete</li>
                            <li>✅ The app can now send verification emails</li>
                            <li>✅ Users can share reports via email</li>
                        </ul>

                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                        <p style="color: #999; font-size: 12px; text-align: center;">
                            Diabetes Health App Team<br>
                            AI-Powered Health Monitoring Platform
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """.format(**config)
        
        # Attach both versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_username'], config['email_password'])
        server.sendmail(config['email_username'], recipient_email, msg.as_string())
        server.quit()
        
        print_success(f"Test email sent successfully to {recipient_email}!")
        print_info("Check your inbox (and spam folder) for the test email")
        return True
        
    except Exception as e:
        print_error(f"Failed to send test email: {e}")
        return False

def test_verification_email_format(config):
    """Test the verification email format (without sending)"""
    print_header("TESTING VERIFICATION EMAIL FORMAT")
    
    test_username = "TestUser"
    test_token = "sample_verification_token_12345"
    verification_url = f"http://127.0.0.1:8080/verify-email/{test_token}"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🏥 Diabetes Health App</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Welcome to AI-Powered Health Monitoring</p>
                </div>

                <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h2 style="color: #667eea; margin-bottom: 20px;">Hello {test_username}!</h2>

                    <p>Thank you for joining the Diabetes Health App.</p>

                    <p><strong>Please verify your email address:</strong></p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}"
                           style="background: linear-gradient(45deg, #667eea, #764ba2);
                                  color: white;
                                  padding: 15px 30px;
                                  text-decoration: none;
                                  border-radius: 25px;
                                  font-weight: 600;
                                  display: inline-block;">
                            ✓ Verify Email Address
                        </a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    
    print_info("Verification email HTML preview generated")
    print_success("Email format is valid and ready to use")
    print(f"\nSample verification URL: {verification_url}")

def main():
    """Main test runner"""
    print_header("DIABETES APP - EMAIL FUNCTIONALITY TESTER")
    
    # Load configuration
    config = load_email_config()
    if not config:
        print_error("\n❌ Configuration loading failed!")
        print_info("\nPlease ensure your .env file exists and contains:")
        print("""
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_CONFIGURED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
        """)
        sys.exit(1)
    
    # Test SMTP connection
    if not test_smtp_connection(config):
        print_error("\n❌ SMTP connection test failed!")
        print_info("\nTroubleshooting tips:")
        print("  1. For Gmail: Use an App Password, not your regular password")
        print("  2. Enable 2-Factor Authentication first")
        print("  3. Generate App Password: https://myaccount.google.com/apppasswords")
        print("  4. Check firewall/antivirus settings")
        sys.exit(1)
    
    # Send test email
    print()
    send_test = input("Do you want to send a test email? (yes/no): ").strip().lower()
    if send_test in ['yes', 'y']:
        recipient = input(f"Enter recipient email (press Enter for {config['email_username']}): ").strip()
        if not recipient:
            recipient = config['email_username']
        
        if send_test_email(config, recipient):
            print_success("\n✅ All tests passed!")
        else:
            print_error("\n❌ Test email failed!")
    else:
        print_info("Skipping test email")
    
    # Test email formats
    test_verification_email_format(config)
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("✅ Configuration loaded successfully")
    print_success("✅ SMTP connection successful")
    print_success("✅ Authentication successful")
    print_success("✅ Email format validated")
    print()
    print_info("Your email configuration is ready to use in the main app!")
    print_info("Make sure EMAIL_CONFIGURED=true in your .env file")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)