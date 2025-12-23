import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import cloudinary
import cloudinary.uploader
import requests
import cloudinary.api
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import subprocess
import sys
import time

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

# Load known face encodings
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

# Setup webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread('Resources/background.png')

# Load mode images
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

studentInfo = {}
modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    found_known_face = False  # Track if any known face was found

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            # Convert small frame face location to full size
            y1, x2, y2, x1 = [v * 4 for v in faceLoc]
            bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)

            if matches[matchIndex]:
                found_known_face = True
                id = studentIds[matchIndex]
                # Set the rectangle color (BGR format)
                rectangle_color = (255, 255, 50)  # Neon Cyan
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0,colorC=rectangle_color)  # Draw rectangle

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
            else:
                # **Unknown face detected**
                cv2.rectangle(imgBackground, (55 + x1, 162 + y1), (55 + x2, 162 + y2), (0, 0, 255), 2)  # Red box
                cv2.putText(imgBackground, "Unknown Face", (55 + x1, 162 + y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if found_known_face:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Fetch student image
                url = cloudinary.utils.cloudinary_url(f'student_images/{id}')[0]
                response = requests.get(url)
                array = np.frombuffer(response.content, np.uint8)
                imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                # Check attendance time
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo.get('total_attendance', 0)), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if id:
                        subprocess.Popen([sys.executable, "AttendanceReport.py", str(id)])
                    else:
                        print(" No student ID available for report generation!")

    else:
        modeType = 0  # Keep active mode
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
