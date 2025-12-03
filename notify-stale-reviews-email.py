#!/usr/bin/env python3
"""
notify-stale-reviews-email.py - Send email alerts for reviews waiting > 3 days

This script sends email notifications for stale reviews, similar to the Slack
notification but via email.

Configuration:
    Create ~/.mymcp-email.env with:
    
    # Option 1: Gmail (with App Password)
    EMAIL_SMTP_HOST=smtp.gmail.com
    EMAIL_SMTP_PORT=587
    EMAIL_USERNAME=your-email@gmail.com
    EMAIL_PASSWORD=your-app-password
    EMAIL_FROM=your-email@gmail.com
    EMAIL_TO=your-email@gmail.com
    
    # Option 2: Red Hat (if available)
    EMAIL_SMTP_HOST=smtp.corp.redhat.com
    EMAIL_SMTP_PORT=25
    EMAIL_USERNAME=
    EMAIL_PASSWORD=
    EMAIL_FROM=omcgonag@redhat.com
    EMAIL_TO=omcgonag@redhat.com

Usage:
    ./notify-stale-reviews-email.py           # Send email
    ./notify-stale-reviews-email.py --preview # Preview without sending
    ./notify-stale-reviews-email.py --test    # Send test email

Cron example (8 AM on weekdays):
    0 8 * * 1-5 ~/Work/mymcp/notify-stale-reviews-email.py
"""

import os
import sys
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path


def load_env(filepath: str) -> dict:
    """Load environment variables from a file."""
    env = {}
    path = Path(filepath).expanduser()
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def generate_fresh_report():
    """Generate fresh activity report."""
    script_dir = Path(__file__).parent / "activity-tracker-agent"
    subprocess.run(
        ["./generate_in_progress.sh"],
        cwd=script_dir,
        capture_output=True
    )


def get_stale_reviews() -> list:
    """Extract reviews waiting > 3 days from in_progress.md."""
    activity_file = Path.home() / "Work/mymcp/workspace/iproject/activity/in_progress.md"
    
    if not activity_file.exists():
        return []
    
    stale_items = []
    in_waiting_section = False
    
    with open(activity_file) as f:
        for line in f:
            # Track when we're in the "People Waiting" section
            if "## 🔔 People Waiting" in line:
                in_waiting_section = True
                continue
            if in_waiting_section and line.startswith("## "):
                # Left the section
                break
            if in_waiting_section and line.startswith("---"):
                break
            
            # Look for table rows with review data
            if in_waiting_section and line.startswith("| ["):
                # Parse the line to extract days
                parts = line.split("|")
                if len(parts) >= 7:
                    # Try to find the days column (usually second to last)
                    for i, part in enumerate(parts):
                        part = part.strip()
                        if part.isdigit() and int(part) >= 3:
                            # Extract key info
                            key = parts[1].strip()
                            # Remove markdown link syntax
                            if "[" in key and "]" in key:
                                key = key.split("]")[0].replace("[", "")
                            owner = parts[2].strip() if len(parts) > 2 else "Unknown"
                            title = parts[4].strip() if len(parts) > 4 else ""
                            if len(title) > 50:
                                title = title[:47] + "..."
                            days = int(part)
                            stale_items.append({
                                'key': key,
                                'owner': owner,
                                'title': title,
                                'days': days
                            })
                            break
    
    return stale_items


def build_email_body(stale_items: list) -> tuple:
    """Build email subject and body."""
    count = len(stale_items)
    subject = f"🚨 mymcp: {count} review(s) waiting > 3 days"
    
    # Plain text body
    body_lines = [
        "Reviews Waiting for Your Attention",
        "=" * 40,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"You have {count} review(s) that have been waiting for more than 3 days:",
        "",
    ]
    
    for item in stale_items:
        body_lines.append(f"• {item['key']} ({item['days']} days)")
        body_lines.append(f"  Owner: {item['owner']}")
        if item['title']:
            body_lines.append(f"  Title: {item['title']}")
        body_lines.append("")
    
    body_lines.extend([
        "-" * 40,
        "Run `~/Work/mymcp/standup-prep.sh` for full details",
        "",
        "-- ",
        "Sent by mymcp activity tracker",
        "https://github.com/mcgonago/mymcp"
    ])
    
    return subject, "\n".join(body_lines)


def send_email(config: dict, subject: str, body: str) -> bool:
    """Send email using SMTP."""
    msg = MIMEMultipart()
    msg['From'] = config.get('EMAIL_FROM', '')
    msg['To'] = config.get('EMAIL_TO', '')
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    smtp_host = config.get('EMAIL_SMTP_HOST', '')
    smtp_port = int(config.get('EMAIL_SMTP_PORT', 587))
    username = config.get('EMAIL_USERNAME', '')
    password = config.get('EMAIL_PASSWORD', '')
    
    try:
        if smtp_port == 465:
            # SSL
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            # TLS
            server = smtplib.SMTP(smtp_host, smtp_port)
            if smtp_port == 587:
                server.starttls()
        
        if username and password:
            server.login(username, password)
        
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}", file=sys.stderr)
        return False


def main():
    # Parse arguments
    preview = "--preview" in sys.argv
    test_mode = "--test" in sys.argv
    
    # Load config
    config = load_env("~/.mymcp-email.env")
    
    if not config and not preview:
        print("❌ No email configuration found!")
        print("")
        print("Create ~/.mymcp-email.env with:")
        print("")
        print("  # Gmail example:")
        print("  EMAIL_SMTP_HOST=smtp.gmail.com")
        print("  EMAIL_SMTP_PORT=587")
        print("  EMAIL_USERNAME=your-email@gmail.com")
        print("  EMAIL_PASSWORD=your-app-password")
        print("  EMAIL_FROM=your-email@gmail.com")
        print("  EMAIL_TO=your-email@gmail.com")
        print("")
        print("See: https://support.google.com/accounts/answer/185833 for App Passwords")
        sys.exit(1)
    
    # Test mode - send a simple test email
    if test_mode:
        print("📧 Sending test email...")
        subject = "🧪 mymcp Email Test"
        body = f"This is a test email from mymcp activity tracker.\n\nSent: {datetime.now()}"
        if send_email(config, subject, body):
            print("✅ Test email sent successfully!")
        else:
            print("❌ Failed to send test email")
        sys.exit(0)
    
    # Generate fresh report
    print("📊 Generating fresh activity report...")
    generate_fresh_report()
    
    # Get stale reviews
    stale_items = get_stale_reviews()
    
    if not stale_items:
        print("✅ No stale reviews (all items < 3 days old)")
        sys.exit(0)
    
    print(f"⚠️  Found {len(stale_items)} review(s) waiting > 3 days")
    
    # Build email
    subject, body = build_email_body(stale_items)
    
    if preview:
        print("")
        print("=== PREVIEW ===")
        print(f"To: {config.get('EMAIL_TO', 'not set')}")
        print(f"Subject: {subject}")
        print("-" * 40)
        print(body)
        print("=== END PREVIEW ===")
    else:
        print("📧 Sending email...")
        if send_email(config, subject, body):
            print("✅ Email sent successfully!")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

