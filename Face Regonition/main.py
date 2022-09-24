import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
import time
import pandas as pd
import sqlite3

# conn = sqlite3.connect('canteen.db')
 
path = 'register_users'
images = []
classNames = []
myList = os.listdir(path)

# iterate folders
# image_folders = [x[0] for x in os.walk(path)]
# image_folders = image_folders[1:]

# # iterate files in folders
# myList = []
# for files in image_folders:
#     myList.extend(os.listdir(files))

# # create complete path
# complete_paths = []
# for i in range(len(image_folders)):
#     complete_paths.append(f"{image_folders[i]}/{myList[i]}")

# # append classNames
# for folder in image_folders:
#     folder = folder.split('register_users/')[1]
#     classNames.append(folder)
                   
# for path in complete_paths:
#     curImg = cv2.imread(path)
#     images.append(curImg)
    # classNames.append(os.path.splitext(cl)[0])

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encodeList = []
    cnt = 0
    for img in images:
        cnt+=1
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            try:
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except Exception as e:
                print(e, cnt)
        else:
            pass
    return encodeList

# function for update real time count
def canteenCount():
    count = pd.read_csv('insideCanteen.csv')
    count = len(count)
    total_seats = 42
    available = total_seats - count
    print(f"Canteen Count = {count}")
    print(f"Available Seats = {available}")

# function to fetch list of persons in Canteen
def getCanteenPerson():
    persons = pd.read_csv('insideCanteen.csv')
    print(persons)

# if person enters in canteen
def insideCanteen(name):

    # remove - from name
    name = name.split("-")[0]

    # fetch data from db
    # dataList = conn.execute("select name from Canteen")
    # nameList = []
    # for name in dataList:
    #     nameList.append(name)

    # # if current name is in list or not
    # if name not in nameList:
    #     now = datetime.now()
    #     dtString = now.strftime('%H:%M:%S')
    #     estTime = now + timedelta(minutes=30)
    #     estTime = estTime.strftime('%H:%M:%S')
    #     # f.writelines(f'\n{name}, {dtString}, {estTime}')
    #     print(name)
    #     conn.execute(f"insert into Canteen (name,time,estTime) values('{name}', '{dtString}', '{estTime}')")
    #     conn.commit()
    #     # conn.close()
    #     print(f"Hi {name}, your entry is recorded at {dtString}. Est. out time: {estTime}")
    
    # else:
    #     print(f"Hi {name}, You are already in. Enjoy your meal ;)")

    with open('insideCanteen.csv', 'r+') as f:
        # already arrived in canteen
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        
        # if current name is in list or not
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            estTime = now + timedelta(minutes=30)
            estTime = estTime.strftime('%H:%M:%S')
            f.writelines(f'\n{name}, {dtString}, {estTime}')
            print(f"Hi {name}, your entry is recorded at {dtString}. Est. out time: {estTime}")
        
        else:
            print(f"Hi {name}, You are already in. Enjoy your meal ;)")

        # canteenCount()
        # time.sleep(1)

encodeListKnown = findEncodings(images)

cap = cv2.VideoCapture(0)
while True:
    # print("processing...")
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].title()
            # y1,x2,y2,x1 = faceLoc
            # y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            # cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            # cv2.rectangle(img,(x1,y2-35), (x2,y2), (0,255,0), cv2.FILLED)
            # cv2.putText(img, name, (x1+6,y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
            insideCanteen(name)