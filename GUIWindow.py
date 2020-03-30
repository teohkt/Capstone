
#pyinstaller --onefile -w CapstoneProgram.py

# import the necessary packages
from __future__ import print_function
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont
from collections import deque
from tkinter import Menu, simpledialog, filedialog, ttk


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


TCP_IP = '169.254.210.163'
TCP_PORT = 6791
BUFFER_SIZE = 1024

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((TCP_IP, TCP_PORT))


class GUIWindow:
	def __init__(self, vs, pitchRead, tiltRead):

		#store video stream and position locally
		self.vs = vs
		self.pitchRead = float(pitchRead)
		self.tiltRead = float(tiltRead) #how much to rotate the image by
		
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

		#Initializations for GUI
		self.trackStatus = False
		self.detectStatus = False
		self.markerStatus = False
		
		self.centerCoord = None

		# initialize the root window and image panel	
		self.panel = None
		self.root = tk.Tk()
		self.canvas = tk.Canvas(self.root,height=650, width=1200)
		self.canvas.grid()

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

		#Start thread for video stream
		#self.thread = None
		#self.stopEvent = None
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

        # Labels next to the buttons
		self.captureLabel = tk.Label(self.root, text="Capture Image")
		self.statusLabel = tk.Label(self.root, text="Tracking Status: ")
		self.detectLabel = tk.Label(self.root, text="Not Detected", fg="red")
		self.trackLabel = tk.Label(self.root, text="Automatically Follow Marker")
		self.laserLabel = tk.Label(self.root, text="Laser Pointer Toggle")

		self.captureLabel.place(x=200, y=396)
		self.statusLabel.place(x=200, y=433)
		self.detectLabel.place(x=312, y=433)
		self.trackLabel.place(x=200, y=481)
		self.laserLabel.place(x=200, y=531)

        # height function does not work on macs... Height is based on font size, ie 2 = *2 font size
		self.captureButton = tk.Button(self.root, text="Capture", font="Times 16", command=self.takeSnapshot, width=10)
		self.markButton = tk.Button(self.root, text="Mrk OFF", font="Times 16", command=self.showMarker, width=10)
		self.trackButton = tk.Button(self.root, text="OFF", font="Times 16", command=self.trackActivate, width=10)
		self.laserButton = tk.Button(self.root, text="OFF", font="Times 16", command=self.laserActivate, width=10)

        # x and y are offset in pixels
		self.captureButton.place(x=50, y=378)
		self.markButton.place(x=50, y=425)
		self.trackButton.place(x=50, y=475)
		self.laserButton.place(x=50, y=525)

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

	# Video Stream Loop and Status Updates 
	def videoLoop(self):
		try:
			# keep looping over frames until we are instructed to stop
			while not self.stopEvent.is_set():

				self.vidFrame = self.vs.read()

				# Rotate image if required from tilt angle input
				rows,cols = self.vidFrame.shape[:2]
				M = cv2.getRotationMatrix2D((cols/2,rows/2),self.tiltRead,1)
				self.videoFrame = cv2.warpAffine(self.vidFrame,M,(cols,rows))

				# Pass image through tracking script and store outputs
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
				self.mask = Image.new('L', (600,600), 0)
				draw = ImageDraw.Draw(self.mask) 
				draw.ellipse((0, 0) + self.mask.size, fill=255)  
		
				self.circimage = ImageOps.fit(self.rawimage, (600,600), centering = (0.5,0.5))
				self.circimage.putalpha(self.mask)
				self.circimage = ImageTk.PhotoImage(self.circimage)

				# Image Panel that shows the video stream
				if self.panel is None:
					self.panel = tk.Label(image=self.circimage)
					self.panel.image = self.circimage					
					self.panel.place(x=450, y=25)
				else:
					self.panel.configure(image=self.circimage)
					self.panel.image = self.circimage

		#Handles runtime errors from threading
		except RuntimeError:
			print("[INFO] caught a RuntimeError")

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

	def outputMotorCoord(self):
		self.outTimer = threading.Timer(2.0,self.outputMotorCoord)
		self.outTimer.start()
		if self.centerCoord == None:
			print("not detected")
		else:
			print(self.centerCoord)

	def laserActivate(self):
		if self.laserButton['text'] == "OFF":
			self.laserButton.configure(text="ON")
		else:
			self.laserButton.configure(text="OFF")

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

		textOnImg = "{} Rotation Angle: {}".format(filename, str(self.tiltRead))
		draw.text((0, 0), textOnImg, (255,255,255), font=font)

		# Save the image
		cv2_im_processed = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
		cv2.imwrite(p, cv2_im_processed.copy())

		print("[INFO] saved {}".format(filename))


	 # for button Press
	def bpressi(self, event=None):
		s.send(str.encode('i'))
	def bpressj(self, event=None):
		s.send(str.encode('j'))
	def bpressk(self, event=None):
		s.send(str.encode('k'))
	def bpressl(self, event=None):
		s.send(str.encode('l'))

 # for keypress j
	def pressj(self, event=None):
		if self.go == False:
			self.go = True
			self.showJudgmentsA()
		else: 
			self.keepShowingj()

	def showJudgmentsA(self):
		print("key-press started")

	def keepShowingj(self):
		print('a key being pressed')
		if self.repeater == False:
			s.send(str.encode('j'))
			self.repeat = True

	def makeChoicej(self, event=None):
		print("choice made")
		self.go = False
		self.repeater = False
		s.send(str.encode('J'))

#for keypress l
	def pressl(self, event=None):
		if self.go == False:
			self.go = True
			self.showJudgmentsA()
		else: 
			self.keepShowingl()

	def keepShowingl(self):
		print('a key being pressed')
		if self.repeater == False:
			s.send(str.encode('l'))
			self.repeat = True

	def makeChoicel(self, event=None):
		print("choice made")
		self.go = False
		self.repeater = False
		s.send(str.encode('L'))

#for keypress i
	def pressi(self, event=None):
		if self.go == False:
			self.go = True
			self.showJudgmentsA()
		else: 
			self.keepShowingi()

	def keepShowingi(self, event=None):
		print('a key being pressed')
		if self.repeater == False:
			s.send(str.encode('i'))
			self.repeat = True

	def makeChoicei(self, event=None):
		print("choice made")
		self.go = False
		self.repeater = False
		s.send(str.encode('I'))

#for keypress k
	def pressk(self, event=None):
		if self.go == False:
			self.go = True
			self.showJudgmentsA()
		else: 
			self.keepShowingk()

	def keepShowingk(self):
		print('a key being pressed')
		if self.repeater == False:
			s.send(str.encode('k'))
			self.repeat = True
			
	def makeChoicek(self, event=None):
		print("choice made")
		self.go = False
		self.repeater = False
		s.send(str.encode('K'))

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
		# set the stop event, cleanup the camera, and allow the rest of the quit process to continue
		print("[INFO] closing stopEvent")
		self.stopEvent.set()
		print("[INFO] closing video feed")
		self.vs.stop()

		print("[INFO] closing Timer")
		if self.trackButton['text'] == "ON":
			self.outTimer.cancel()

		print("[INFO] quit root")
		self.root.quit()

		print("[INFO] destroy root")
		#self.root.quit()
		self.root.destroy()
