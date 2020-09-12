# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:14:18 2020

@author: 44758
"""
from typing import List

"""
IMPORTS
"""
import pymysql
from imutils.video import FileVideoStream
import face_recognition
import sys
import time
import numpy as np
import imutils
import cv2
from datetime import datetime
import os
import threading
from datetime import date




class queueAnalysis():

    """"
    CLASS VARIABLES
    """


    #video_file_entrance = None
    #video_file_exit = None

    # SET UP DATABASE

    connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                 database="queue_buster", port=3306)

    cursor = connection.cursor()

    #SET UP KNOWN ENCODED FACES VECTOR

    test_face = face_recognition.load_image_file('imgs/Initialise_face.jpg')

    test_encoding = face_recognition.face_encodings(test_face)[0]

    known_faces = [

        test_encoding,

    ]

    known_numbers=[
        0
    ]

    store=0

    # CONFIDENCE VALUE FOR FACIAL DETECTION

    confidence_val = 0.99


    """"
    THREADED ENTRANCE AND EXIT VIDEOS FUNCTION 
    """

    @staticmethod
    def threadedProcessing(video_file_entrance, video_file_exit, video_file_queue):
        print("Starting video analysis")


        p3 = threading.Thread(target=queueAnalysis.findQueueLength(store=queueAnalysis.store, queueVideo=video_file_queue))
        p3.start()


        for video in video_file_entrance:
            p1 = threading.Thread(target=queueAnalysis.process_entrance_video(video))
            p1.start()

        for video in video_file_exit:
            p2 = threading.Thread(target=queueAnalysis.process_exit_video(video))
            p2.start()



        p1.join()
        p2.join()
        p3.join()


        queueAnalysis.cursor.close()
        print("Video analysis complete")

        #END OF THREADED FUNCTION


    """
    ENTRANCE VIDEO
    """

    @staticmethod
    def process_entrance_video(video_file_entrance):

        caffe_file = "detection_model/res10_300x300_ssd_iter_140000.caffemodel"

        model_file = "detection_model/deploy.prototxt.txt"

        gender_model_file = "gender_model/deploy_gender.prototxt"

        gender_caffe_file = "gender_model/gender_net.caffemodel"


        # SET-UP GENDER RETURN

        gender_list = [0, 1]


        # SET-UP NETS FROM MODEL FILES

        net = cv2.dnn.readNetFromCaffe(model_file, caffe_file)

        gender_net = cv2.dnn.readNet(gender_model_file, gender_caffe_file)

        # Start the Video
        fvs = FileVideoStream(video_file_entrance).start()

        retrive = "Select CustomerID FROM q_Customers ORDER BY CustomerID DESC LIMIT 1;"

        # executing the quires
        queueAnalysis.cursor.execute(retrive)
        rows = queueAnalysis.cursor.fetchall()
        customer = rows[0][0]+1


        count = 0

        while fvs.more():
            frame = fvs.read()
            count += 1
            if count % 5 == 0:
                if frame is None:
                    break
                else:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    # frame= frame[200:400,150:250]
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                                 (300, 300), (104.0, 177.0, 123.0))
                    net.setInput(blob)
                    detections = net.forward()

                    for i in np.arange(0, detections.shape[2]):
                        confidence = detections[0, 0, i, 2]
                        if confidence > queueAnalysis.confidence_val:
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")
                            if startX > 20:
                                face = frame[startY - 20:endY + 20, startX - 20:endX + 20]
                                try:
                                    unknown_face_encoding = face_recognition.face_encodings(face)[0]
                                    results = face_recognition.compare_faces(queueAnalysis.known_faces, unknown_face_encoding)

                                    if not True in results:
                                        img_folder = "imgs/" + str(customer)
                                        img_path = "imgs/" + str(customer) + "/face1.jpg"
                                        if not os.path.exists(img_folder):
                                            os.makedirs(img_folder)
                                        queueAnalysis.known_numbers.append(customer)
                                        queueAnalysis.known_faces.append(unknown_face_encoding)
                                        faceBlob = cv2.dnn.blobFromImage(face, 1.0, (227, 227),
                                                                         (78.4263377603, 87.7689143744, 114.895847746),
                                                                         swapRB=False)


                                        gender_net.setInput(faceBlob)
                                        predg = gender_net.forward()
                                        j = predg[0].argmax()
                                        gender = gender_list[j]

                                        insertC="INSERT INTO `q_Customers` (`CustomerID`, `StoreID`, `Date`, `EntranceTime`, `GenderID`) VALUES (%s, %s, %s, %s, %s)"
                                        record= (customer, '1', date.today(), datetime.now(), gender)

                                        queueAnalysis.cursor.execute(insertC, record)
                                        queueAnalysis.connection.commit()

                                        cv2.imwrite(img_path, face)
                                        customer += 1


                                    if True in results:
                                        match = results.index(True)
                                        customermatch = queueAnalysis.known_numbers[match]
                                        img_folder = "imgs/" + str(customermatch)

                                        if os.path.exists(img_folder):
                                            fileSize=len(os.listdir(img_folder))+1

                                            if fileSize < 4:
                                                img_path = "imgs/" + str(customermatch) + "/face"+str(fileSize)+".jpg"
                                                cv2.imwrite(img_path, face)

                                except IndexError:
                                    #print("Could not encode this face entrance")
                                    continue



        #END OF ENTRANCE VIDEO FUNCTION

    """
    EXIT VIDEO
    """

    @staticmethod
    def process_exit_video(video_file_exit):

        caffe_file = "detection_model/res10_300x300_ssd_iter_140000.caffemodel"

        model_file = "detection_model/deploy.prototxt.txt"

        # CONFIDENCE VALUE FOR FACIAL DETECTION

        confidence_val = 0.99

        # SET-UP NETS FROM MODEL FILES

        net2 = cv2.dnn.readNetFromCaffe(model_file, caffe_file)

        time.sleep(10)

        # Start the Video
        fvs2 = FileVideoStream(video_file_exit).start()

        count = 0

        while fvs2.more():
            frame = fvs2.read()
            count += 1
            if count % 2 == 0:
                if frame is None:
                    break
                else:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    # frame= frame[200:400,150:250]
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                                 (300, 300), (104.0, 177.0, 123.0))
                    net2.setInput(blob)
                    detections = net2.forward()

                    for i in np.arange(0, detections.shape[2]):
                        confidence = detections[0, 0, i, 2]
                        if confidence > confidence_val:
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")
                            if startX > 20:
                                face = frame[startY - 20:endY + 20, startX - 20:endX + 20]
                                try:
                                    unknown_face_encoding = face_recognition.face_encodings(face)[0]
                                    results = face_recognition.compare_faces(queueAnalysis.known_faces, unknown_face_encoding, 0.5)
                                    if True in results:
                                        match = results.index(True)
                                        customer=queueAnalysis.known_numbers[match]

                                        exitTime = datetime.now()
                                        retrive = "Select EntranceTime FROM q_Customers WHERE CustomerID= %s"

                                        # executing the quires
                                        queueAnalysis.cursor.execute(retrive,customer)
                                        rows = queueAnalysis.cursor.fetchall()
                                        entranceTime = rows[0][0]
                                        waitTime = exitTime - entranceTime


                                        updateC = "UPDATE `q_Customers` SET `ExitTime` = %s, `WaitTime` = %s WHERE `q_Customers`.`CustomerID` = %s;"
                                        recordUpdate = (exitTime, waitTime, customer)

                                        queueAnalysis.cursor.execute(updateC, recordUpdate)
                                        queueAnalysis.connection.commit()
                                    #if not True in results:
                                        #print("EXIT: I encoded this face but I'm not sure who it is? ")
                                except IndexError:
                                    #print("Could not encode this face exit")
                                    continue

    # END OF EXIT VIDEO FUNCTION



    @staticmethod
    def findQueueLength(store, queueVideo):

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                      database="queue_buster", port=3306)

        cursor=connection.cursor()

        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                   "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                   "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                   "sofa", "train", "tvmonitor"]


        caffe_file="mobilenet_ssd/MobileNetSSD_deploy.caffemodel"

        model_file="mobilenet_ssd/MobileNetSSD_deploy.prototxt"

        net = cv2.dnn.readNetFromCaffe(model_file, caffe_file)

        fvs = FileVideoStream(queueVideo).start()

        count = 0

        peopleInLastFrame=0

        while fvs.more():
            peopleInFrame=0
            arrival=0
            frame = fvs.read()
            if frame is None:
                break
            count += 1
            if count % 100 == 0:
                if frame is None:
                    break
                else:
                    #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    # frame= frame[200:400,150:250]
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(frame, 0.007843, (w, h), 127.5)
                    net.setInput(blob)
                    detections = net.forward()

                    for i in np.arange(0, detections.shape[2]):

                        confidence = detections[0, 0, i, 2]

                        if confidence > 0.6:
                            idx = int(detections[0, 0, i, 1])

                            # if the class label is not a person, ignore it
                            if CLASSES[idx] == "person":
                                peopleInFrame += 1
                                #print("Person detected")



            if peopleInFrame > peopleInLastFrame:
                arrival=1
                #print("New arrival")
            else:
                arrival=0
            peopleInLastFrame = peopleInFrame

            insert="INSERT INTO `q_length` (`StoreID`, `Date`, `Time`, `QueueLength`, `Arrival`) VALUES (%s, %s, %s, %s, %s);"

            data=(1, date.today(), datetime.now(), peopleInFrame, arrival)

            queueAnalysis.cursor.execute(insert, data)
            queueAnalysis.connection.commit()

        fvs.stop()
