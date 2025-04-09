from flask_mail import Mail, Message
import sqlite3
from datetime import datetime

mail = Mail()

def send_email(recipient, subject, body):
    from app import app 
    mail.init_app(app)
    with app.app_context():
        msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[recipient])
        msg.body = body
        mail.send(msg)

def send_verification_email(email, short_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT expires_at FROM email_verifications WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return  # No verification request found

    expires_at = result[0]

    try:
        expiration_time = datetime.fromisoformat(expires_at)  # Ensures correct UTC format
    except ValueError:
        expiration_time = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")  

    formatted_expiration = expiration_time.strftime("%B %d, %Y at %I:%M %p")

    email_body = f"""
    Hello,

    Click the link below to verify your access:

    http://localhost:5000/verify/{short_id}/{email}

    This link will expire on {formatted_expiration}.

    If you did not request this, please ignore this email.

    Thank You
    """
    # print(email_body, flush=True)
    send_email(email, "Verify Your Access", email_body)

def notify_creator(short_id, email):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT creator_email FROM urls WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        creator_email = result[0]
        email_body = f"{email} has accessed the link associated with short ID: {short_id}"
        send_email(creator_email, "URL Access Notification", email_body)
