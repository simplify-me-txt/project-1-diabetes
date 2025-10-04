#!/bin/bash

# Diabetes Health App - Email Setup Script
# Alternative deployment method for email functionality

echo "📧 DIABETES HEALTH APP - EMAIL DEPLOYMENT"
echo "=========================================="
echo ""

# Function to show email queue status
show_queue() {
    python3 email_service.py status
}

# Function to send test email
send_test() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: $0 test <your-email@gmail.com> <your-app-password>"
        return 1
    fi

    echo "🧪 Sending test email..."
    python3 email_service.py test "$1" "$2"
}

# Function to process email queue
process_queue() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: $0 send <your-email@gmail.com> <your-app-password>"
        echo ""
        echo "To get Gmail app password:"
        echo "1. Go to myaccount.google.com"
        echo "2. Security → 2-Step Verification (enable it)"
        echo "3. Security → App passwords"
        echo "4. Generate password for 'Mail'"
        echo "5. Use the 16-character password here"
        return 1
    fi

    echo "📤 Processing email queue..."
    python3 email_service.py send "$1" "$2"
}

# Function to show help
show_help() {
    echo "Available commands:"
    echo ""
    echo "  ./setup_email.sh status                              # Show email queue"
    echo "  ./setup_email.sh test <email> <password>            # Send test email"
    echo "  ./setup_email.sh send <email> <password>            # Process all queued emails"
    echo "  ./setup_email.sh auto <email> <password>            # Set up automatic processing"
    echo ""
    echo "Examples:"
    echo "  ./setup_email.sh status"
    echo "  ./setup_email.sh test myapp@gmail.com abcd1234efgh5678"
    echo "  ./setup_email.sh send myapp@gmail.com abcd1234efgh5678"
    echo ""
    echo "📝 How it works:"
    echo "  1. Registration instantly queues emails (no delays)"
    echo "  2. Use this script to send real emails when ready"
    echo "  3. Perfect for development and production deployment"
}

# Process command line arguments
case "$1" in
    "status")
        show_queue
        ;;
    "test")
        send_test "$2" "$3"
        ;;
    "send")
        process_queue "$2" "$3"
        ;;
    "auto")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 auto <email> <password>"
            exit 1
        fi
        echo "🔄 Setting up automatic email processing..."
        echo "Creating cron job to process emails every 5 minutes..."

        # Create cron job
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        CRON_CMD="*/5 * * * * cd $SCRIPT_DIR && python3 email_service.py send $2 $3 >> email.log 2>&1"

        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo "✅ Automatic email processing enabled (every 5 minutes)"
        echo "📋 Check email.log for processing logs"
        ;;
    *)
        show_help
        ;;
esac