import cv2
import os
import threading

import face_recognition as frc
import requests as rq
import numpy as np

from time import sleep
from datetime import datetime
from threading import Thread

home = os.getenv('HOME') + '/'
ssc = home + 'Documents/smart_security_cam/'
latest = ssc + 'latest/'

camera = ssc + 'camera/'
faces = latest + 'faces/'
video = ssc + 'video_feed/'


dt = datetime.now()
today = str(dt.date()) + '/'

face_locations = []
face_encodings = []

def check_dirs():
    if not os.path.exists(ssc):
        os.system('mkdir ' + ssc)

    if not os.path.exists(camera):
        os.system('mkdir ' + camera)

    if not os.path.exists(video):
        os.system('mkdir ' + video)

    if not os.path.exists(camera + today):
        os.system('mkdir ' + camera + today)

    if not os.path.exists(video + today):
        os.system('mkdir ' + video + today)


def take_pictures(n, source):

    if not os.path.exists(ssc):
        os.system('mkdir ' + ssc)
    if not os.path.exists(camera):
        os.system('mkdir ' + camera)
    if not os.path.exists(camera + today):
        os.system('mkdir ' + camera + today)

    if type(source) == int:
        cam = cv2.VideoCapture(source)

    # cam = cv2.VideoCapture(0)
    count = 0
    images = dict()
    time = str(datetime.now().time()).split('.')[0] + '/'
    time = time.replace(':','-')
    while count < n:
        ret, frame = cam.read()
        if ret:
            count += 1
            face_locations = frc.face_locations(frame)
            if face_locations:
                frame_name = 'img_' + str(count) + '.jpg'
                images[frame_name] = frame
                sleep(1)
    cam.release()

    if images:
        os.system('mkdir ' + camera + today + time)

        for name, img in images.items():
            cv2.imwrite(camera + today + time + name, img)

        if os.path.exists(latest):
            os.system('rm -rf ' + latest[:-1])
        os.symlink(camera + today + time[:-1], latest[:-1])

        if not os.path.exists(faces):
            os.system('mkdir ' + faces)


def face_recognition():
    img_no = 0
    for snap in os.listdir(latest):
        if snap == 'faces':
            continue

        img_no += 1
        img = cv2.imread(latest + snap)
        face_locations = frc.face_locations(img)
        face_encodings = frc.face_encodings(img, face_locations)
        face_no = 0
        for face in face_locations:
            face_no += 1
            face_name = faces + "/face_" + str(img_no) + "_" + str(face_no) + ".jpg"
            top, right, bottom, left = face
            crop_img = img[top:bottom, left:right]
            cv2.imwrite(face_name, crop_img)


def find_unique_faces():
    file_names = os.listdir(faces)
    for file in file_names:
        face = cv2.imread(faces + '/' + file)
        encoding = frc.face_encodings(face)[0]
        face_encodings.append(encoding)

    unique_faces = []
    index_list = []
    index = 0
    for face in face_encodings:
        matches = frc.compare_faces(unique_faces, face)
        if not True in matches:
            index_list.append(index)
            unique_faces.append(face)
        index += 1

    index = 0
    no = 0
    for file in file_names:
        if index not in index_list:
            os.system("rm " + faces + "/" + file)
        else:
            os.system("mv " + faces + "/" + file + " " + faces + "/" + "face_" + str(no) + ".jpg")
            no += 1
        index += 1

buffer = []
done = 0
res = ''

def ip_feed(url, usr, pswd):

    global buffer
    global done
    global res

    if not os.path.exists(ssc):
        os.system('mkdir ' + ssc)
    if not os.path.exists(video):
        os.system('mkdir ' + video)

    today = str(dt.date()) + '/'
    if not os.path.exists(video + today):
        os.system('mkdir ' + video + today)
    time = datetime.now()
    time1 = datetime.now()
    while True:
        today = str(dt.date()) + '/'
        if not os.path.exists(video + today):
            os.system('mkdir ' + video + today)
        rqst = rq.get(url, auth=(usr,pswd))
        read = rqst.content
        imgNp = np.array(bytearray(read),dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)
        if not res:
            res = img.shape[:-1]
            res = res[::-1]
        end = datetime.now()
        dif = end - time
        if dif.seconds > 120:
            buffer.append(0)
            time = datetime.now()
        end1 = datetime.now()
        dif1 = end1 - time1
        if dif1.microseconds > 300000:
            time1 = datetime.now()
            buffer.append(img)
        if done:
            break

def fps():
    global buffer
    while not buffer:
        pass
    print(len(buffer))
    sleep(1)
    print(len(buffer))

def vid_feed():

    global buffer
    global done
    global res

    done = 0

    if not os.path.exists(ssc):
        os.system('mkdir ' + ssc)
    if not os.path.exists(video):
        os.system('mkdir ' + video)

    today = str(dt.date()) + '/'
    if not os.path.exists(video + today):
        os.system('mkdir ' + video + today)

    cam = cv2.VideoCapture(0)
    count = 0
    time = datetime.now()
    time1 = datetime.now()
    while True:
        today = str(dt.date()) + '/'
        if not os.path.exists(video + today):
            os.system('mkdir ' + video + today)
        # count += 1
        img = cam.read()[1]
        if not res:
            res = img.shape[:-1]
            res = res[::-1]
        end = datetime.now()
        dif = end - time
        if dif.seconds > 120:
            buffer.append(0)
            time = datetime.now()
        end1 = datetime.now()
        dif1 = end1 - time1
        if dif1.microseconds >300000:
            time1 = datetime.now()
            buffer.append(img)
        if done:
            break
    cam.release()

def vid_frc():

    global buffer
    global done
    global res

    out = ''
    while not res:
        res = tuple()
    while not done:
        time = str(datetime.now().time())
        time = time.split('.')[0]
        out = cv2.VideoWriter(video + today + 'recording_'+ time +'.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 5, (res[0],res[1]))

        flocs = []
        res = tuple()
        count = 0
        while True:
            if not buffer:
                if done:
                    print('finished')
                    break
                continue

            img = buffer[0]
            buffer = buffer[1:]
            if type(img) == int and img == 0:
                break

            x = 2
            y = 1/x

            if count == 5:
                small_img = cv2.resize(img, (0, 0), fx=y, fy=y)
                # small_img = img
                flocs = frc.face_locations(small_img)
                count = 0
            if flocs:
                for top, right, bottom, left in flocs:
                    top = int(top*x)
                    right = int(right*x)
                    bottom = int(bottom*x)
                    left = int(left*x)
                    cv2.rectangle(img, (left-10, top-10), (right+10, bottom+10), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, str(datetime.now().time()).split('.')[0], (0,25), font, 1.0, (0, 0, 255), 1)
            count += 1
            cv2.imshow('vid_frc', img)
            out.write(img)
            #
            k = cv2.waitKey(1);
            if k == ord('q'):
                done = 1
            elif k == ord('s'):
                done = 0
                break
        cv2.destroyAllWindows()
        out.release()

def latdir():
    dir = os.listdir(latest)
    print(dir)


if __name__ == '__main__':

    url = 'http://DCS933L17C4.local/image/jpeg.cgi'
    usr = 'admin'
    pswd = 'sharath'
   # t1 = Thread(target=vid_feed)
    t1 = Thread(target=ip_feed, args=(url,usr,pswd))# <--- takes video feed from ip camera and saves frame in buffer
    t2 = Thread(target=vid_frc)# <--- reads buffer and performs face recognition.
    t1.start()
    t2.start()
    t1.join()
    t2.join()
