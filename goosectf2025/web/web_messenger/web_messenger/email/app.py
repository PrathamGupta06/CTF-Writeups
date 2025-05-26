import asyncio
from aiosmtpd.controller import Controller
import time

userEmail = "1337@warwickcybersoc.com"

class EmailHandler:
    def __init__(self):
        self.emails = []  # Store emails in memory

    async def handle_DATA(self, server, session, envelope):
        email = {
            "id": len(self.emails) + 1,
            "from": envelope.mail_from,
            "to": envelope.rcpt_tos,
            "subject": envelope.content.decode("utf8", errors="replace").split("\n")[0],
            "body": envelope.content.decode("utf8", errors="replace"),
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if userEmail in envelope.rcpt_tos:
            self.emails.append(email)
            print(f"Received email: {email}")
        return '250 Message accepted for delivery'

# Start SMTP server
def run_smtp_server():
    handler = EmailHandler()
    controller = Controller(handler, hostname="127.0.0.1", port=8025)
    controller.start()
    return handler


from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)


@app.route("/inbox")
def inbox():
    # Sort emails by time received
    sorted_emails = sorted(handler.emails, key=lambda email: email["time"], reverse=True)    
    return render_template("inbox.html", emails=sorted_emails, email_address=userEmail)

@app.route("/email/<int:email_id>")
def view_email(email_id):
    email = next((email for email in handler.emails if email["id"] == email_id), None)
    if not email:
        return redirect(url_for("inbox"))
    return render_template("view_email.html", email=email)



if __name__ == "__main__":
    handler = run_smtp_server()
    app.run(port=5001)
else:
    handler = run_smtp_server()