import cv2
import firebase_admin
import numpy as np
import cloudinary
import cloudinary.api
import requests
import sys
from firebase_admin import db
from firebase_admin import credentials
import time
from datetime import datetime

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dnw11pui1",
    api_key="366774748762333",
    api_secret="IcSmluygFM8EBAm9bFCqoGWwrYg"
)

# Firebase Initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionproject-676be-default-rtdb.firebaseio.com/"
})

# Define Placements
placements = {
    "photo": (494, 131, 216, 216),
    "name": (339, 466),
    "branch": (361, 528),
    "percentage": (428, 583),
    "remarks": (383, 638)
}
text_color = (255, 255, 255)  # #41435d in BGR
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.75
thickness = 2

# Get current month
current_month = datetime.now().strftime("%Y-%m")


# Fetch student details from Firebase
def get_student_data(id):
    ref = db.reference(f'Students/{id}')
    return ref.get()


# Fetch Image from Cloudinary
def get_student_image(id):
    try:
        url = cloudinary.utils.cloudinary_url(f'student_images/{id}.png')[0]
        response = requests.get(url)
        if response.status_code != 200:
            print(f" Failed to fetch image, status code: {response.status_code}")
            return None

        array = np.asarray(bytearray(response.content), dtype=np.uint8)
        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
        return imgStudent
    except Exception as e:
        print(f" Error fetching image: {e}")
        return None


# Calculate Monthly Attendance Percentage
def calculate_attendance(student_data):
    monthly_attendance = student_data.get("monthly_attendance", {})
    attended = monthly_attendance.get(current_month, 0)
    total_working_days = student_data.get("total_days", 22)  # Default: 22 days

    if total_working_days == 0:  # Prevent division by zero
        return 0

    return round((attended / total_working_days) * 100, 2)


# Generate Remarks Based on Attendance
def generate_remarks(percentage):
    if percentage >= 90:
        return "Excellent"
    elif percentage >= 75:
        return "Competent"
    else:
        return "Detention"


# Update Monthly Attendance in Firebase
def update_attendance(student_id):
    ref = db.reference(f'Students/{student_id}')
    student_data = ref.get()

    if not student_data:
        print(f" Student data not found for ID: {student_id}!")
        return

    #  Get or initialize monthly attendance records
    monthly_attendance = student_data.get("monthly_attendance", {})

    #  Reset attendance if it's a new month
    if current_month not in monthly_attendance:
        monthly_attendance[current_month] = 0

    #  Increment attendance for the current month
    monthly_attendance[current_month] += 1

    #  Calculate total attendance dynamically
    total_attendance = sum(monthly_attendance.values())  #  Fix: No manual incrementing

    #  Update Firebase
    ref.update({
        "monthly_attendance": monthly_attendance,
        "total_attendance": total_attendance  # Dynamically calculated
    })

    print(f" Attendance updated for {student_data['name']} (ID: {student_id})")


# Generate Attendance Report
def generate_attendance_report(student_id):
    update_attendance(student_id)  #  Mark attendance before generating report

    student_data = get_student_data(student_id)
    if not student_data:
        print(f" Student data not found for ID: {student_id}!")
        return

    #  Load Background Image
    bg_img = cv2.imread("Resources/ReportBg.png")

    #  Fetch Student Photo
    student_photo = get_student_image(student_id)
    if student_photo is not None:
        x, y, w, h = placements["photo"]
        resized_photo = cv2.resize(student_photo, (w, h))
        bg_img[y:y + h, x:x + w] = resized_photo

    #  Compute Attendance Percentage & Remarks
    percentage = calculate_attendance(student_data)
    remarks = generate_remarks(percentage)

    #  Overlay Text
    cv2.putText(bg_img, f"{student_data['name']}", placements["name"], font, font_scale, text_color, thickness)
    cv2.putText(bg_img, f"{student_data['major']}", placements["branch"], font, font_scale, text_color, thickness)
    cv2.putText(bg_img, f"{percentage}%", placements["percentage"], font, font_scale, text_color, thickness)
    cv2.putText(bg_img, f"{remarks}", placements["remarks"], font, font_scale, text_color, thickness)

    # Save & Show Report
    report_filename = f"Attendance_Report_{student_id}.png"
    cv2.imwrite(report_filename, bg_img)
    print(f" Report saved as: {report_filename}")

    #  Display Report for 3 Seconds & Exit
    cv2.imshow("Student Attendance Report", bg_img)
    cv2.waitKey(3000)  # Keep window open for 3 seconds
    cv2.destroyAllWindows()
    sys.exit()  #Ensure script exits properly


#  Accept Student ID as Command-Line Argument
if __name__ == "__main__":
    print(f" sys.argv received: {sys.argv}")  # Debugging line

    if len(sys.argv) > 1:
        student_id = sys.argv[1]  # Get student ID from main.py
        print(f" ID received in AttendanceReport.py: {student_id}")  # Debugging print
        generate_attendance_report(student_id)  #  Generate report after marking attendance
    else:
        print(" No Student ID provided! Exiting...")
