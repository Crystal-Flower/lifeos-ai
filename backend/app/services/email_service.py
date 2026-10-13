import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_notification_email(subject: str, body: str, to_email: str = "anandhappriya@gmail.com"):
    # Always log to a local file for transparency and local verification
    log_msg = f"=== EMAIL NOTIFICATION SENT ===\nTo: {to_email}\nSubject: {subject}\nBody:\n{body}\n================================\n\n"
    try:
        with open("email_delivery_log.txt", "a") as f:
            f.write(log_msg)
        print(f"Logged notification email to email_delivery_log.txt")
    except Exception as e:
        print(f"Failed to log email: {e}")
        
    if not settings.GMAIL_PASSWORD:
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(settings.GMAIL_USER, settings.GMAIL_PASSWORD)
        server.sendmail(settings.GMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"Sent email notification to {to_email} successfully.")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        return False
