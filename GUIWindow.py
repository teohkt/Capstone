
#pyinstaller --onefile -w CapstoneProgram.py

# import the necessary packages
from __future__ import print_function
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont, ImageEnhance
from collections import deque
from tkinter import Menu, simpledialog, filedialog, ttk

# Other python scripts
from tracking import colorTracking
from motorcontrols import motorControls



import tkinter as tk
import threading
import datetime
import imutils
import cv2
import os
import socket
import numpy as np
import sys
import time




TCP_IP = '169.254.210.163'
TCP_PORT = 6791
BUFFER_SIZE = 1024

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((TCP_IP, TCP_PORT))


class GUIWindow:
	def __init__(self, vs, pitchRead, tiltRead, connection):

		# Demonstration Variables
		self.brightnessVal = 0

		#store video stream and position locally
		self.vs = vs
		self.pitchRead = float(pitchRead)
		self.tiltRead = float(tiltRead) #how much to rotate the image by

		self.s = connection

		self.outputPath = os.path.dirname(os.path.realpath(__file__)) #Default save location to where program is stored
		self.saveLoc = os.getcwd()
		self.currDir = os.getcwd()

		#Initializations for video modifications
		self.vidFrame = None
		self.videoFrame = None
		self.circimage = None
		self.rawimage = None
		self.image = None
		self.savedimg = None

		#initializations for keyboard controls
		self.go = False
		self.repeater = False
		self.imgpress = False

		#Initializations for GUI Status 
		self.trackStatus = False
		self.detectStatus = False
		self.markerStatus = False
		
		self.centerCoord = None

		# initialize the root window and image panel	
		self.panel = None
		self.root = tk.Tk()
		#self.canvas = tk.Canvas(self.root,height=650, width=1150)
		#self.canvas.grid()

		self.root.geometry("1150x650+386+0")

		self.root.wm_title("PTZ Inspection Camera")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		#Menu Bar
		menuBar = Menu(self.root)

		fileMenu = Menu(menuBar, tearoff=0)
		fileMenu.add_command(label="Save Location", command=self.changeSaveLoc)
		fileMenu.add_separator()
		fileMenu.add_command(label="Exit", command=self.onClose)
		menuBar.add_cascade(label="File", menu=fileMenu)

		helpMenu = Menu(menuBar, tearoff=0)
		helpMenu.add_command(label="Setup Details", command=self.setupDet)
		menuBar.add_cascade(label="Help", menu=helpMenu)
		self.root.config(menu=menuBar)

        # Labels next to the buttons
		self.captureLabel = tk.Label(self.root, text="Capture Image")
		self.statusLabel = tk.Label(self.root, text="Tracking Status: ")
		self.detectLabel = tk.Label(self.root, text="Not Detected", fg="red")
		self.trackLabel = tk.Label(self.root, text="Automatically Follow Marker")
		self.laserLabel = tk.Label(self.root, text="Laser Pointer Toggle")

		self.captureLabel.place(x=200, y=396)
		self.statusLabel.place(x=200, y=433)
		self.detectLabel.place(x=305, y=433)
		self.trackLabel.place(x=200, y=481)
		self.laserLabel.place(x=200, y=531)

        # height function does not work on macs... Height is based on font size, ie 2 = *2 font size
		self.captureButton = tk.Button(self.root, text="Capture", font="Times 16", command=self.takeSnapshot, width=10)
		self.markButton = tk.Button(self.root, text="Mrk OFF", font="Times 16", command=self.showMarker, width=10)
		self.trackButton = tk.Button(self.root, text="OFF", font="Times 16", command=self.trackActivate, width=10)
		self.laserButton = tk.Button(self.root, text="OFF", font="Times 16", command=self.laserActivate, width=10)

        # x and y are offset in pixels
		self.captureButton.place(x=50, y=375)
		self.markButton.place(x=50, y=425)
		self.trackButton.place(x=50, y=475)
		self.laserButton.place(x=50, y=525)

		# Sliders for LED Brightness and Zoom
		self.slideLED = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, command = self.adjBright, length=127, resolution=10)
		self.slideLED.place(x=50, y=570)
		self.ledLabel = tk.Label(self.root, text="LED Brightness").place(x=200, y=590)
		self.slideLED.set(50)

		self.slideZoom = tk.Scale(self.root, from_=0, to=100, command = self.adjZoom, length=300, resolution=10)
		self.slideZoom.place(x=395, y=215)
		self.zoomLabel = tk.Label(self.root, text="Zoom").place(x=395, y=190)

        # Arrow Cluster & Bindings
		picupArrow = os.path.join(self.currDir, "images/upArrow.gif")
		self.arrowUp=ImageTk.PhotoImage(file=picupArrow)
		upButton=tk.Button(self.root, image=self.arrowUp)
		upButton.bind('<ButtonPress-1>', self.bpressi)
		upButton.bind('<ButtonRelease-1>', self.makeChoicei)
		upButton.place(x=110, y=220-50)

		picdownArrow = os.path.join(self.currDir, "images/downArrow.gif")
		self.arrowDown = tk.PhotoImage(file=picdownArrow)
		downButton=tk.Button(self.root, image=self.arrowDown)
		downButton.bind('<ButtonPress-1>', self.bpressk)
		downButton.bind('<ButtonRelease-1>', self.makeChoicek)
		downButton.place(x=110, y=346-50)

		picleftArrow = os.path.join(self.currDir, "images/leftArrow.gif")
		self.arrowLeft = tk.PhotoImage(file=picleftArrow)
		leftButton=tk.Button(self.root, image=self.arrowLeft)
		leftButton.bind('<ButtonPress-1>', self.bpressj)
		leftButton.bind('<ButtonRelease-1>', self.makeChoicej)
		leftButton.place(x=50, y=280-50)

		picrightArrow = os.path.join(self.currDir, "images/rightArrow.gif")
		self.arrowRight = tk.PhotoImage(file=picrightArrow)
		rightButton=tk.Button(self.root, image=self.arrowRight)
		rightButton.bind('<ButtonPress-1>', self.bpressl)
		rightButton.bind('<ButtonRelease-1>', self.makeChoicel)
		rightButton.place(x=175, y=280-50)

		# Keyboard Button Bindings
		self.root.bind('<j>', self.pressj)
		self.root.bind('<KeyRelease-j>', self.makeChoicej)

		self.root.bind('<l>', self.pressl)
		self.root.bind('<KeyRelease-l>', self.makeChoicel)

		self.root.bind('<i>', self.pressi)
		self.root.bind('<KeyRelease-i>', self.makeChoicei)

		self.root.bind('<k>', self.pressk)
		self.root.bind('<KeyRelease-k>', self.makeChoicek)

		#Start thread for video stream, daemon terminates the thread when application ends
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=(), daemon=True)
		self.thread.start()

	def adjBright(self, ledPower):
		self.brightnessVal = ledPower
		print("[DATA] NEW LED: ", ledPower)

	def adjZoom(self, zoomValue):
		print("[DATA] NEW ZOM LEVEL: ", zoomValue)


	# Video Stream Loop and Status Updates 
	def videoLoop(self):
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():

				self.vidFrame = self.vs.read()

				# Flips image to be mirror mode only for webcam application
				if self.s == None:
					self.vidFrame = cv2.flip(self.vidFrame, 1)
				
				# Rotate image if required from tilt angle input
				rows,cols = self.vidFrame.shape[:2]
				M = cv2.getRotationMatrix2D((cols/2,rows/2),self.tiltRead,1)
				self.videoFrame = cv2.warpAffine(self.vidFrame,M,(cols,rows))

				# Pass rotated image through tracking script and store outputs
				if self.markerStatus == True:
					trackingFeed = colorTracking.Tracking(self.videoFrame, True)
					videoFeed = trackingFeed[0]
					self.centerCoord = trackingFeed[1]
					detectStatus = trackingFeed[2]

					if detectStatus == "Detected":
						self.detectLabel.config(text="Detected", fg="green")
					else:
						self.detectLabel.config(text="Not Detected", fg="red")
				else:
					trackingFeed = colorTracking.Tracking(self.videoFrame, False)
					videoFeed = trackingFeed[0]
					self.centerCoord = trackingFeed[1]
					detectStatus = trackingFeed[2]

					if detectStatus =="Detected":
						self.detectLabel.config(text="Detected", fg="green")
					else:
						self.detectLabel.config(text="Not Detected", fg="red")

				# Convert processed image RGB
				self.image = cv2.cvtColor(videoFeed, cv2.COLOR_BGR2RGB)	
				self.rawimage = Image.fromarray(self.image)

				#Converting the image to a circle
				self.mask = Image.new('L', (850,600), 0)
				draw = ImageDraw.Draw(self.mask) 
				draw.ellipse([(0, 0), (600,600)], fill=255)  
				#draw.ellipse([(125, 0), (600,725)] + self.mask.size, fill=255) 

				self.circimage = ImageOps.fit(self.rawimage, (850,600), centering = (0.5,0.5))
				self.circimage.putalpha(self.mask)
				self.circimage = ImageTk.PhotoImage(self.circimage)

				# Fake Brightness Modification
				#self.circimage = ImageEnhance.Brightness(self.circimage._PhotoImage__photo).enhance(2.0)
				#self.circimage = Image.fromarray(self.circimage)

				# Image Panel that shows the video stream
				if self.panel is None:
					self.panel = tk.Label(image=self.circimage)
					self.panel.image = self.circimage					
					self.panel.place(x=475, y=25)
				else:
					self.panel.configure(image=self.circimage)
					self.panel.image = self.circimage

		#Handles runtime errors from threading
		except RuntimeError:
			print("[INFO] CAUGHT A RUNTIMEERROR")

	# Update status lines on GUI
	def showMarker(self):
		if self.markButton['text'] == "Mrk OFF":
			self.markButton.configure(text="Mrk ON")
			self.markerStatus = True
		else:
			self.markButton.configure(text="Mrk OFF")
			self.markerStatus = False
			
	# Output motor commands if auto tracking is toggled
	def trackActivate(self):
		if self.trackButton['text'] == "OFF":
			self.trackButton.configure(text="ON")
			self.trackStatus = True
			self.outputMotorCoord()
		else:
			self.trackButton.configure(text="OFF")
			self.trackStatus = False
			self.outTimer.cancel()
	
	#Start a thread for timer. 2 seconds to allow for motors to reach position
	def outputMotorCoord(self):
		self.outTimer = threading.Timer(2.0,self.outputMotorCoord)
		self.outTimer.start()
		if self.centerCoord == None:
			print("NO OBJECT DETECTED")
		else:
			print("[DATA] OBJECT COORDINATE: {}".format(str(self.centerCoord)))
			
			self.motorCoord()

			
	# Calculating motor distance
	def motorCoord(self):
		tiltMin = 0
		tiltMax = 1000
		objX = self.centerCoord[0]
		objY = self.centerCoord[1]

		if 250 < objX < 350:
			if 250 < objY <350:
				print("[OPERATION] OBJECT CENTERED")
			else:
				motorY = objY - 300
				motorINP = (0,motorY)
				print("[OPERATION] MOVE MOTORS TO {}".format(str(motorINP)))
		else:
			if 250 < objY <350:
				motorX = 300 - objX
				motorINP = (motorX, 0)
				print("[OPERATION] MOVE MOTORS TO {}".format(str(motorINP)))
			else:
				motorX = 300 - objX
				motorY = objY - 300
				motorINP = (motorX,motorY)
				print("[OPERATION] MOVE MOTORS TO {}".format(str(motorINP)))


	def laserActivate(self):
		if self.laserButton['text'] == "OFF":
			self.laserButton.configure(text="ON")
			print("[OPERATION] LED POWERED ON")
		else:
			self.laserButton.configure(text="OFF")
			print("[OPERATION] LED POWERED OFF")

	def takeSnapshot(self):		# grab the current timestamp and use it to construct the output path
		#ts = datetime.datetime.now()
		#filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		self.changeFileName()
		filename = "{}.jpg".format(self.fileName)
		pathname = self.saveLoc
		p = os.path.sep.join((pathname, filename))
		
		self.savedimg = self.vidFrame

		# Draw the text info on image
		cv2_im_rgb = cv2.cvtColor(self.savedimg, cv2.COLOR_BGR2RGB)
		pil_im = Image.fromarray(cv2_im_rgb)

		draw = ImageDraw.Draw(pil_im)

		font = ImageFont.truetype("./font/arial.ttf", size=10)

		textOnImg = "{} ROTATION ANGLE: {}".format(filename, str(self.tiltRead))
		draw.text((0, 0), textOnImg, (255,255,255), font=font)

		# Save the image
		cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
		cv2.imwrite(p, cv2_im_processed.copy())

		print("[INFO] IMAGE {} SAVED TO {}".format(filename,pathname))


	 # for button Press
	def bpressi(self, event=None):
		#self.s.send(str.encode('i'))
		print("[OUT] BUTTON: TILT MOTOR UP")
	def bpressj(self, event=None):
		#self.s.send(str.encode('j'))
		print("[OUT] BUTTON: PAN MOTOR LEFT")
	def bpressk(self, event=None):
		#self.s.send(str.encode('k'))
		print("[OUT] BUTTON: TILT MOTOR DOWN")
	def bpressl(self, event=None):
		#self.s.send(str.encode('l'))
		print("[OUT] BUTTON: PAN MOTOR RIGHT")

 # for keypress j
	def pressj(self, event=None):
		if self.go == False:
			self.go = True
			print("[OUT] KEYPRESS: PAN MOTOR LEFT")

		else: 
			self.keepShowingj()

	def keepShowingj(self):
		if self.repeater == False:
			#self.s.send(str.encode('j'))
			self.repeat = True
			
	def makeChoicej(self, event=None):
		self.go = False
		self.repeater = False
		#self.s.send(str.encode('J'))


#for keypress l
	def pressl(self, event=None):
		if self.go == False:
			self.go = True
			print("[OUT] KEYPRESS: PAN MOTOR RIGHT")
		else: 
			self.keepShowingl()

	def keepShowingl(self):
		if self.repeater == False:
			#self.s.send(str.encode('l'))
			self.repeat = True
			

	def makeChoicel(self, event=None):
		self.go = False
		self.repeater = False
		#self.s.send(str.encode('L'))


#for keypress i
	def pressi(self, event=None):
		if self.go == False:
			self.go = True
			print("[OUT] KEYPRESS: TILT MOTOR UP")
		else: 
			self.keepShowingi()

	def keepShowingi(self, event=None):
		if self.repeater == False:
			#self.s.send(str.encode('i'))
			self.repeat = True
			

	def makeChoicei(self, event=None):
		self.go = False
		self.repeater = False
		#self.s.send(str.encode('I'))


#for keypress k
	def pressk(self, event=None):
		if self.go == False:
			self.go = True
			print("[OUT] KEYPRESS: TILT MOTOR DOWN")
		else: 
			self.keepShowingk()

	def keepShowingk(self):
		if self.repeater == False:
			#self.s.send(str.encode('k'))
			self.repeat = True		

	def makeChoicek(self, event=None):
		self.go = False
		self.repeater = False
		#self.s.send(str.encode('K'))


	def changeSaveLoc(self):
		self.saveLoc = filedialog.askdirectory()
		print(self.saveLoc)

	def changeFileName(self):
		self.fileName=simpledialog.askstring("New File Name", "Input file name")
		print(self.fileName)

	def setupDet(self):
		popup = tk.Tk()
		popup.wm_title("Setup Details")

		textAngle = "Rotation Angle: {}".format(str(self.tiltRead))
		saveLoc = "Current Save Directory: {}".format(str(self.saveLoc))

		label = ttk.Label(popup, text="{}\n{}".format(textAngle,saveLoc))
		label.pack(side="top", fill="x", pady=10)
		#B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
		#B1.pack()
		popup.mainloop()
		

	def onClose(self):
		# Returning Motors to home position
		print("[OPERATION] MOVING MOTORS TO HOME POSITION")
		time.sleep(2)

		# Set the stop event, end timer function, cleanup the camera
		print("[INFO] ENDING PROCESSES")
		self.stopEvent.set()
		if self.trackButton['text'] == "ON":
			self.outTimer.cancel()
		self.vs.stop()

		# Quit GUI
		print("[INFO] QUITTING GUI")
		self.root.quit()
		#self.root.destroy()
