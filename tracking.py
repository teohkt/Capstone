from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

#green cap
colorLower = (63,139,56)
colorUpper = (90,255,146)

pts = deque(maxlen=32)



class colorTracking:

    def Tracking(frameOrig, overlay):
        
        detect = None

        frameOrig = imutils.resize(frameOrig, height=600)
        
        frame = imutils.resize(frameOrig, height = 600)
        blurred = cv2.GaussianBlur(frame, (11,11),0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        #Creates a mask for just the color
        mask = cv2.inRange(hsv, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations = 2)
        mask = cv2.dilate(mask, None, iterations = 2)

        #Find the contours of the mask and center point
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        #If one contour was found
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x,y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))

            #Proceed if the radius is at least 10 pixels
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
                cv2.circle(frame, center, 5, (0,0,255), -1)
                detect = "Detected"
            else:
                detect = "Not Detected"

        #update points in queue
        pts.appendleft(center)

        #loop over set of points in queue for tail
        for i in range(1, len(pts)):
            if pts[i-1] is None or pts[i] is None:
                continue

            thickness = int(np.sqrt(64/float(i+1))*2.5)
            #cv2.line(frame, pts[i-1], pts[i], (0,0,255), thickness)

        if overlay == True:
            return(frame, center, detect)

        else:
            return(frameOrig, center, detect)
