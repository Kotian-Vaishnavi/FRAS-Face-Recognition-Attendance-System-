import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': " "
})

# Get current month (YYYY-MM format)
current_month = datetime.now().strftime("%Y-%m")

# Reference to Students in Firebase
ref = db.reference('Students')

# Updated Data with Monthly Attendance Tracking
data = {
    "321654": {
        "name": "Sheldon Lee Cooper",
        "major": "Quantum Physics",
        "starting_year": 2024,
        "total_attendance": 6,
        "monthly_attendance": {current_month: 6},  # Track attendance per month
        "standing": "G",
        "year": 1,
        "last_attendance_time": "2025-02-08 00:54:34"
    },
    
    "963852": {
        "name": "Elon Musk",
        "major": "Quantum Mechanics",
        "starting_year": 2021,
        "total_attendance": 10,
        "monthly_attendance": {current_month: 10},
        "standing": "B",
        "year": 4,
        "last_attendance_time": "2025-02-08 00:54:34"
    }
}

# Upload data to Firebase
for key, value in data.items():
    ref.child(key).set(value)

print("Student data uploaded with monthly attendance tracking!")

