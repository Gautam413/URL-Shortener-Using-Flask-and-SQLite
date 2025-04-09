from flask import Flask, request, redirect, render_template
import uuid
import datetime
from database import get_db_connection
from email_service import send_email, send_verification_email

app = Flask(__name__)
app.config.from_object("config.Config")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        original_url = request.form["url"]
        creator_email = request.form["creator_email"]
        short_id = str(uuid.uuid4())[:6]

        created_at = datetime.datetime.now(datetime.UTC).isoformat()
        expires_at = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=60)).isoformat()

        allowed_emails = request.form.get("allowed_emails", "").strip().split(",")
        allowed_emails = [email.strip().lower() for email in allowed_emails]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO urls (short_id, original_url, creator_email, created_at, expires_at) VALUES (?, ?, ?, ?, ?)", 
            (short_id, original_url, creator_email, created_at, expires_at)
        )

        for email in allowed_emails:
            cursor.execute("INSERT INTO allowed_emails (short_id, email) VALUES (?, ?)", (short_id, email))
        
        conn.commit()
        conn.close()

        return render_template("success.html", short_url=short_id)

    return render_template("index.html")


@app.route("/<short_id>", methods=["GET", "POST"])
def access_url(short_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    url_data = cursor.execute(
        "SELECT short_id, original_url, expires_at FROM urls WHERE short_id = ?", 
        (short_id,)
    ).fetchone()

    if not url_data:
        return "URL not found", 404

    expires_at = datetime.datetime.fromisoformat(url_data["expires_at"]).replace(tzinfo=datetime.UTC)

    if expires_at < datetime.datetime.now(datetime.UTC):
        cursor.execute("DELETE FROM urls WHERE short_id = ?", (short_id,))
        conn.commit()
        conn.close()
        return "This link has expired!", 403

    allowed_emails = [
        row["email"].strip().lower() 
        for row in cursor.execute("SELECT email FROM allowed_emails WHERE short_id = ?", (short_id,))
    ]

    conn.close()

    if allowed_emails:
        if request.method == "POST":
            user_email = request.form.get("email", "").strip().lower()

            if user_email in allowed_emails:
                #Set verification expiration (1 day)
                verification_expires_at = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)).isoformat()

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO email_verifications (short_id, email, expires_at) VALUES (?, ?, ?)",
                    (short_id, user_email, verification_expires_at)
                )
                conn.commit()
                conn.close()

                # Send verification email
                # verification_link = f"http://localhost:5000/verify/{short_id}/{user_email}"
                # send_email(user_email, "Verify Access", f"Click here to access: {verification_link}")
                send_verification_email(user_email, short_id)

                return "Verification email sent! Check your inbox."

            return "Unauthorized access!", 403

        return render_template("verify_email.html", short_id=short_id)

    return redirect(url_data["original_url"])


@app.route("/verify/<short_id>/<email>")
def verify_email(short_id, email):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 Fetch verification link expiration time
    verification_data = cursor.execute(
        "SELECT expires_at FROM email_verifications WHERE short_id = ? AND email = ?",
        (short_id, email)
    ).fetchone()

    if not verification_data:
        return "Verification not found!", 404

    # 🔹 Convert ISO string to datetime object
    verification_expires_at = datetime.datetime.fromisoformat(verification_data["expires_at"])
    # 🔥 Check if the verification link is still valid
    if verification_expires_at < datetime.datetime.now(datetime.UTC):
        cursor.execute("DELETE FROM email_verifications WHERE short_id = ? AND email = ?", (short_id, email))
        conn.commit()
        conn.close()
        return "Verification link expired!", 403

    url_data = cursor.execute(
        "SELECT original_url, creator_email FROM urls WHERE short_id = ?", 
        (short_id,)
    ).fetchone()

    if not url_data:
        return "URL not found", 404

    cursor.execute(
        "INSERT INTO access_logs (short_id, accessed_by) VALUES (?, ?)", 
        (short_id, email)
    )
    conn.commit()
    conn.close()

    #Notify creator
    send_email(url_data["creator_email"], "Access Alert", f"{email} accessed your link {short_id}.")
    
    return redirect(url_data["original_url"])


if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
