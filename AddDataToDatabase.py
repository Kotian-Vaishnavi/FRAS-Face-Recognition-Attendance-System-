import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionproject-676be-default-rtdb.firebaseio.com/"
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
    "334556": {
        "name": "Rutuja Patil",
        "major": "IT Engineering",
        "starting_year": 2023,
        "total_attendance": 10,
        "monthly_attendance": {current_month: 10},
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-02-08 00:54:34"
    },
    "852741": {
        "name": "Vaishnavi Kotian",
        "major": "IT Engineering",
        "starting_year": 2023,
        "total_attendance": 9,
        "monthly_attendance": {current_month: 9},
        "standing": "G",
        "year": 2,
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
    },
    "989774": {
        "name": "Shravani Alam",
        "major": "IT Engineering",
        "starting_year": 2023,
        "total_attendance": 12,
        "monthly_attendance": {current_month: 12},
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-02-08 00:54:34"
    }
}

# Upload data to Firebase
for key, value in data.items():
    ref.child(key).set(value)

print("Student data uploaded with monthly attendance tracking!")
