import cv2
import face_recognition
import pickle
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api


cloudinary.config(
    cloud_name= "dnw11pui1",
    api_key ="366774748762333",
    api_secret ="IcSmluygFM8EBAm9bFCqoGWwrYg"
)
#importing the student images
folderPath= 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds =[]

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    file_path = os.path.join(folderPath, path)
    public_id = f"student_images/{os.path.splitext(path)[0]}"  # Unique ID for each student image

    # Check if image is already uploaded in Cloudinary
    try:
        cloudinary.api.resource(public_id)  # If image exists, this will succeed
        print(f"Skipping {path}, already uploaded.")
    except cloudinary.exceptions.NotFound:  # If not found, upload it
        response = cloudinary.uploader.upload(
            file_path,
            public_id=public_id,  # Use file name as public_id
            overwrite=True  # Ensures Cloudinary replaces the old file
        )
        print(f"Uploaded {path} to Cloudinary: {response['secure_url']}")

# print(path)
   # print(os.path.splitext(path)[0])
print(studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)


    return encodeList
print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds =[encodeListKnown, studentIds]
#print(encodeListKnown)
print("Encoding complete")

file =open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")