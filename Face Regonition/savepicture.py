import cv2
import smtplib,ssl
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
cap = cv2.VideoCapture(0)
model = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def SendMail(ImgFileName):
    with open(ImgFileName, 'rb') as f:
        img_data = f.read()
    msg = MIMEMultipart()
    msg['Subject'] = 'Cropped Image'
    msg['From'] = 'Tinkal Shakya'
    msg['To'] = 'recevier'
    text = MIMEText("I have cropped the face from the live video")
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)
    context=ssl.create_default_context()
    s =  smtplib.SMTP_SSL("smtp.gmail.com",465,context=context)
    s.login("sender_mail","password")
    s.sendmail('sender_mail','recevier_mail', msg.as_string())
    s.quit()
    print("Mail Sended")

cap = cv2.VideoCapture(0)
i = 0
while True:
    i = i + 1
    success, img = cap.read()
    face  = model.detectMultiScale(img)
    if len(face) == 0:
        pass
    else:
        x1 = face[0][0]
        y1 = face[0][1]
        x2 = face[0][2] + x1
        y2 = face[0][3] + y1 
        crop_img = img[y1:y2 , x1:x2]         
        cv2.imshow('Crop Image', crop_img)
        if cv2.waitKey(100) == 13:
            break
        cv2.imwrite('images/ayaz/'+str(i)+".png",crop_img)

cv2.destroyAllWindows()