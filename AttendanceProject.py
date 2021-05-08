import os
import cv2
import pytz
import numpy as np
from time import sleep
import face_recognition
from datetime import datetime

path = 'ImageAttendance'
images = []
classNames = []
myList = os.listdir(path)


for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
#print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('Attendance.csv','r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            pytz.timezone('Asia/Jakarta')
            now = datetime.now()
            tgl = now.strftime('%x')
            dtString = now.strftime('%X')
            hadir = now.replace(hour=7,minute=40,second=0)
            pulang = now.replace(hour=14,minute=0,second=0)

            if (now <= hadir):
                f.writelines(f'\n{tgl},{name},0,{dtString}')
            elif (now >= pulang):
                with open('Attendance.csv','r') as f1:
                    atd = f1.read()
                atd = atd.replace(f'{tgl},{name},0',f'{tgl},{name},{dtString}')
                with open('Attendance.csv','w') as f1:
                    f1.write(atd)

encodeListKnown = findEncodings(images)
#print(len(encodeListKnown))
#print("Encoding Complete")
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
#        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
#            print(name)
            y1,x2,y2,x1 = faceLoc
#            y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
            sleep(10)

    cv2.imshow('Attendance System',img)
    cv2.waitKey(1)