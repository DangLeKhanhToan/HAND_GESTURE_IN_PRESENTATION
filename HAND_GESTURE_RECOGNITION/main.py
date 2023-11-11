import os
import numpy as np
import cv2
from cvzone.HandTrackingModule import HandDetector

# Variables for Webcam
width, height = 1920, 1080


# Variables for presentation
FolderPath = "Presentation"
ImgNumber = 0
height_presentation, width_presentation = int(320), int(480)
Control_line = 300
annotations = [[]]
annotationNumber = -1
annotationStart = False

# Variables for delay transition
wait = False
timeDelay = 30
timeCount = 0
# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Path of Presentation
pathImages = sorted(os.listdir(FolderPath), key=len)

# Hand Detector

detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Camera and Presentation
    success, img = cap.read()
    img = cv2.flip(img, 1)
    Path_Full_Images = os.path.join(FolderPath, pathImages[ImgNumber])
    CurrentPresentation = cv2.imread(Path_Full_Images)

    hands, img = detector.findHands(img, flipType=False)

    # Set up a control line to draw on the presentation
    cv2.line(img, (0, Control_line), (width, Control_line), (0, 255, 0), 10)

    # Adding webcam on Presentation
    Webcam = cv2.resize(img, (width_presentation, height_presentation))
    h, w, _ = CurrentPresentation.shape
    CurrentPresentation[0:height_presentation, w - width_presentation: w] = Webcam

    if hands and wait is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        # Pointer
        # Create a small area to control the Pointer
        X_pointer = int(np.interp(lmList[8][0], [width_presentation//2-60 , width_presentation - 40], [0, w]))
        Y_pointer = int(np.interp(lmList[8][1], [20, height_presentation - 60], [0, h]))
        indexFinger = X_pointer, Y_pointer
        print(lmList[8][0], lmList[8][1])
        print(f'X la {X_pointer}, Y la {Y_pointer}')

        # indexFinger = X_pointer, Y_pointer
        if fingers == [1, 1, 0, 0, 0]:
            cv2.circle(CurrentPresentation, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        if cy <= Control_line:
            # Backward Images
            if fingers == [0, 0, 0, 0, 0]:
                if ImgNumber > 0:
                    wait = True
                    ImgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
            # Next Images
            if fingers == [1, 0, 0, 0, 0]:
                if ImgNumber < len(pathImages) - 1:
                    wait = True
                    ImgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
            # Drawing
            if fingers == [1, 1, 1, 0, 0]:
                if annotationStart is False:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                cv2.circle(CurrentPresentation, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                annotations[annotationNumber].append(indexFinger)
            else:
                annotationStart = False

            # Erase
            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    wait = True
    if wait:
        timeCount += 1
        if timeCount >= timeDelay:
            timeCount = 0
            wait = False


    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(CurrentPresentation, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)

    cv2.imshow("Presentation", CurrentPresentation)
    key = cv2.waitKey(1)
    if key == ord('x'):
        break
