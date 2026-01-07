from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
from services.emailer import send_result_email

import os

from anomaly.detector import detect_anomalies_from_csv
from db.database import (
    create_tables,
    save_results,
    fetch_all_results,
    delete_record,
    clear_all_history
)
from services.emailer import send_result_email
from ai.chatbot import ask_exam_bot

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "examaudit-secret")

create_tables()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    session["name"] = request.form["name"]
    session["email"] = request.form["email"]
    session["role"] = request.form["role"]
    session["subject"] = request.form["subject"]
    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect("/")
    return render_template("dashboard.html", email=session["email"])

# ---------------- AUDIT ----------------
@app.route("/audit", methods=["POST"])
def audit():
    if "email" not in session:
        return redirect("/")

    subject = session.get("subject", "Audit All Subjects")

    results = detect_anomalies_from_csv(
        "data/marks.csv",
        subject
    )

    save_results(results)

    
    try:
        send_result_email(session["email"], results)
    except Exception as e:
        print("Email error:", e)

    return render_template("results.html", results=results)


# ---------------- MANUAL REVIEW ----------------
@app.route("/manual", methods=["GET", "POST"])
def manual():
    if request.method == "POST":
        student_id = request.form["student_id"]
        subject = request.form["subject"]
        marks = int(request.form["marks"])

        results = [{
            "student_id": student_id,
            "email": session["email"],
            "subject": subject,
            "marks": marks,
            "severity": "Manual",
            "explanation": "Manually submitted for review"
        }]

        save_results(results)
        return render_template("results.html", results=results)

    return render_template("manual.html")


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    records = fetch_all_results()
    return render_template("history.html", records=records)

@app.route("/delete/<int:record_id>")
def delete(record_id):
    delete_record(record_id)
    return redirect("/history")

@app.route("/clear-history")
def clear_history():
    clear_all_history()
    return redirect("/history")

# ---------------- CHATBOT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    question = request.json["message"]
    answer = ask_exam_bot(question)
    return {"reply": answer}

if __name__ == "__main__":
    app.run(debug=True)
