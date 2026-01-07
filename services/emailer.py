import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_result_email(to_email, results):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        print("Email credentials missing")
        return

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "ExamAudit – AI Audit Results"

    if not results:
        body = "No anomalies detected. All scores appear fair."
    else:
        body = "Anomalies Detected:\n\n"
        for r in results:
            body += (
                f"Student ID: {r['student_id']}\n"
                f"Subject: {r['subject']}\n"
                f"Marks: {r['marks']}\n"
                f"Severity: {r['severity']}\n"
                f"Reason: {r['explanation']}\n\n"
            )

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

    print("✅ Email sent successfully")
