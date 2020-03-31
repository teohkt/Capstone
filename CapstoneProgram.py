
# import the necessary packages
from __future__ import print_function

from GUIWindow import GUIWindow
from tracking import colorTracking
from imutils.video import VideoStream
import argparse
import time
import cv2
import imutils
import socket

print("[INFO] STARTING PROGRAM")

'''
print("[INFO] Trying RTSP Connection")
try: 
    TCP_IP = '169.254.210.163'
    TCP_PORT = 6791
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = s.connect((TCP_IP, TCP_PORT))
    connection
    vs = VideoStream('rtsp://admin:admin@169.254.210.163:554/videoinput_1:0/h264_1/media.stm').start()

except:
    print("[INFO] Timeout on RTSP, Trying Webcam Connection")
    vs = VideoStream(0).start()
    connection = None
'''

vs = VideoStream(0).start()
connection = None


print("[INFO] CALCULATING EULER ANGLES")

pitchAngle = float(0)
tiltAngle = float(0)

print("[DATA] PITCH ANGLE {}, TILT ANGLE {}".format(str(pitchAngle), str(tiltAngle)))


print("[OPERATION] TILT MOTOR HOME SEQUENCE")
time.sleep(2)
print("[OPERATION] PAN MOTOR HOME SEQUENCE")
time.sleep(2)

print("[INFO] STARTING GUI")


GUI = GUIWindow(vs,pitchAngle,tiltAngle, connection)
#TRACKING = colorTracking(vs)

GUI.root.mainloop()
