import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
import time
import pandas as pd
 
path = 'register_users'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
import pickle

# print(classNames)
data = pickle.loads(open('encodings.pickle', "rb").read())
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
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
            f.writelines(f"\n{name}, {dtString}, {estTime}")
            print(f"Hi {name}, your entry is recorded at {dtString}. Est. out time: {estTime}")
        
        else:
            print(f"Hi {name}, You are already in. Enjoy your meal ;)")

        canteenCount()
        # time.sleep(5)

def readImage():    
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        print("curImg " ,curImg)
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    
    print("images ", images, classNames)
    return images, classNames



# imgs , clsnames = readImage()
# encodeListKnown = findEncodings(imgs)

cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        # matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        matches = face_recognition.compare_faces(data["encodings"],encodeFace)
        faceDis = face_recognition.face_distance(data["encodings"], encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1


            name = max(counts, key=counts.get)
            # name = classNames[matchIndex].title()
            y1,x2,y2,x1 = faceLoc
            # y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            # cv2.rectangle(img,(x1,y2-35), (x2,y2), (0,255,0), cv2.FILLED)
            # cv2.putText(img, name, (x1+6,y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

            insideCanteen(name)
    cv2.imshow('Frame Face Detection', cv2.flip(img, 1))
    # if cv2.waitKey(5) & 0xFF == 27:
    #     break