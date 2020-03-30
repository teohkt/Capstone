
# import the necessary packages
from __future__ import print_function

from GUIWindow import GUIWindow
from tracking import colorTracking
from imutils.video import VideoStream
import argparse
import time
import cv2
import imutils

print("[INFO] Starting Program")

#vs = VideoStream('rtsp://admin:admin@169.254.210.163:554/videoinput_1:0/h264_1/media.stm').start()
vs = VideoStream(0).start()

pitchAngle = float(0)
tiltAngle = float(0)

GUI = GUIWindow(vs,pitchAngle,tiltAngle)
#TRACKING = colorTracking(vs)

GUI.root.mainloop()
#TRACKING.Tracking()
