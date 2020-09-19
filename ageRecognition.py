import pymysql
import face_recognition
import sys
import numpy as np
import imutils
import cv2
import os


def mainAgeFunction(customerNumber):

    connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                 database="queue_buster", port=3306)

    cursor = connection.cursor()

    img_folder = "imgs/" + str(customerNumber)

    dirSize = len(os.listdir(img_folder))

    ages = []
    confidence = []

    for i in range(dirSize - 1):
        img_path = "imgs/" + str(customerNumber) + "/face" + str(i + 1) + ".jpg"


        if ageRecognition(img_path)!=None:
            ages.append(ageRecognition(img_path)[0])
            confidence.append((ageRecognition(img_path))[1])

    if len(confidence) > 0:
        i = confidence.index(max(confidence))
        age_i = int(ages[i])

        updateC = "UPDATE `q_Customers` SET `AgeID` = %s WHERE `q_Customers`.`CustomerID` = %s;"
        recordUpdate = (age_i, customerNumber)

        cursor.execute(updateC, recordUpdate)
        connection.commit()

        try:
            os.removedirs(img_folder)
        except:
            print("Unable to delete")


    cursor.close()


def ageRecognition(imagePath):
    image = cv2.imread(imagePath)

    caffe_file = "detection_model/res10_300x300_ssd_iter_140000.caffemodel"

    model_file = "detection_model/deploy.prototxt.txt"

    age_caffe_file = "age_model/age_net.caffemodel"

    age_model_file = "age_model/deploy_age.prototxt"

    faceNet = cv2.dnn.readNetFromCaffe(model_file, caffe_file)
    ageNet = cv2.dnn.readNet(age_model_file, age_caffe_file)

    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))

    faceNet.setInput(blob)
    detections = faceNet.forward()

    # loop over the detections
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.9:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            face = image[startY:endY, startX:endX]
            faceBlob = cv2.dnn.blobFromImage(face, 1.0, (227, 227),
                                             (78.4263377603, 87.7689143744, 114.895847746),
                                             swapRB=False)

            ageNet.setInput(faceBlob)
            preds = ageNet.forward()
            i = preds[0].argmax()
            ageConfidence = preds[0][i]

            if ageConfidence > 0.5:
                return [i, ageConfidence]

            else:
                return None

