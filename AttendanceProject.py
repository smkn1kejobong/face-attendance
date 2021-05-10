import os
import cv2
import pytz
import pymysql
import numpy as np
import face_recognition
from time import sleep
from datetime import datetime

path = 'ImageAttendance'
images = []
classNames = []
myList = os.listdir(path)


for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def cekabshadir(tanggal,name):
    db = pymysql.connect(host='localhost', user='root', passwd='', db='attendance', charset='utf8mb4')
    cursor = db.cursor()
    sql = "SELECT hadir FROM data WHERE tanggal=%s AND nama=%s"
    cursor.execute(sql, (tanggal, name))
    results = cursor.fetchone()
    return results

def cekabspulang(tanggal,name):
    db = pymysql.connect(host='localhost', user='root', passwd='', db='attendance', charset='utf8mb4')
    cursor = db.cursor()
    sql = "SELECT pulang FROM data WHERE tanggal=%s AND nama=%s"
    cursor.execute(sql, (tanggal, name))
    results = cursor.fetchone()
    return results

def abshadir(tanggal,name,hadir):
    db = pymysql.connect(host='localhost', user='root', passwd='', db='attendance', charset='utf8mb4')
    cursor = db.cursor()
    sql = "INSERT INTO data(tanggal, nama, hadir) VALUES (%s, %s,%s)"
    cursor.execute(sql, (tanggal, name, hadir))
    db.commit()

def abspulang(tanggal,name,pulang):
    db = pymysql.connect(host='localhost', user='root', passwd='', db='attendance', charset='utf8mb4')
    cursor = db.cursor()
    sql = "UPDATE data SET pulang=%s WHERE tanggal=%s AND nama=%s"
    cursor.execute(sql, (pulang, tanggal, name))
    db.commit()

encodeListKnown = findEncodings(images)

# Video Capture (WEBCAM)
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
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1,x2,y2,x1 = faceLoc
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            pytz.timezone('Asia/Jakarta')
            now = datetime.now()
            tgl = now.strftime('%x')
            dtString = now.strftime('%X')
            hadir = now.replace(hour=17,minute=0,second=0)
            pulang = now.replace(hour=18,minute=30,second=0)
            if (now <= hadir):
                if (cekabshadir(tgl,name) == None):
                    cv2.putText(img,"SELAMAT DATANG",(x1+6,y2-240),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    abshadir(tgl,name,dtString)
                else:
                    cv2.putText(img,"SUDAH ABSEN HADIR",(x1+6,y2-240),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            elif (now >= pulang):
                if (cekabspulang(tgl,name) == None):
                    cv2.putText(img,"SAMPAI JUMPA LAGI",(x1+6,y2-240),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    abspulang(tgl,name,dtString)
                else:
                    cv2.putText(img,"SUDAH ABSEN PULANG",(x1+6,y2-240),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
#            markAttendance(name)


    cv2.imshow('Attendance System',img)
    cv2.waitKey(1)