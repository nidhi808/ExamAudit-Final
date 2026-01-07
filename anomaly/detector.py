import csv
import statistics

SUBJECTS = ["maths", "physics", "chemistry"]
Z_THRESHOLD = 2.0

def read_students(csv_path):
    with open(csv_path, "r") as f:
        return list(csv.DictReader(f))

def audit_subject(students, subject):
    results = []

    # collect valid marks
    marks = []
    for s in students:
        try:
            marks.append(int(s[subject]))
        except:
            pass

    if len(marks) < 3:
        return results

    mean = statistics.mean(marks)
    std = statistics.stdev(marks)

    for s in students:
        try:
            score = int(s[subject])

            # 🔴 HARD RULE — ALWAYS FLAG
            if score < 35:
                results.append({
                    "student_id": s["student_id"],
                    "email": s["email"],
                    "subject": subject.capitalize(),
                    "marks": score,
                    "severity": "High",
                    "explanation": (
                        "Score below minimum acceptable threshold (35). "
                        "Automatically flagged for fairness review."
                    )
                })
                continue

            # 🟠 Z-SCORE CHECK
            z = (score - mean) / std

            if abs(z) >= Z_THRESHOLD:
                results.append({
                    "student_id": s["student_id"],
                    "email": s["email"],
                    "subject": subject.capitalize(),
                    "marks": score,
                    "severity": "High" if abs(z) >= 3 else "Medium",
                    "explanation": (
                        f"Z-score anomaly detected (z = {round(z,2)}). "
                        "Score significantly deviates from class average."
                    )
                })

        except:
            continue

    return results

def detect_anomalies_from_csv(csv_path, selected_subject):
    students = read_students(csv_path)
    final = []

    if selected_subject == "Audit All Subjects":
        for sub in SUBJECTS:
            final.extend(audit_subject(students, sub))
    else:
        final.extend(audit_subject(students, selected_subject.lower()))

    return final
