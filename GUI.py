import tkinter as tk
import os
import cv2
import threading
from PIL import Image, ImageTk

class Window(tk.Frame):
    # Initializing the window
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.outputPath = os.path.dirname(os.path.realpath(__file__))

        self.panel = None
        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture('rtsp://admin:admin@192.254.30.144')

        self.lmain = tk.Label(root)
        self.lmain.place(x=500, y=200)

        self.frame = None
        self.thread = None
        self.stopEvent = None
        # self.videoLoop()

        #self.stopEvent = threading.Event()
        #self.thread = threading.Thread(targe=self.videoLoop(), args=())
        #self.thread.start()

    def init_window(self):
        self.master.title("Inspection Camera Inferface")
        self.pack(fill=tk.BOTH, expand=1)

        # Labels next to the buttons
        self.webcamLabel = tk.Label(root, text="Webcam Status:")
        self.statusLabel = tk.Label(root, text="Tracking Status: ")
        self.detectLabel = tk.Label(root, text="Not Detected", fg="red")
        self.trackLabel = tk.Label(root, text="Automatically Follow Marker")
        self.laserLabel = tk.Label(root, text="Laser Pointer Toggle")

        self.webcamLabel.place(x=138, y=378)
        self.statusLabel.place(x=138, y=428)
        self.detectLabel.place(x=250, y=428)
        self.trackLabel.place(x=138, y=478)
        self.laserLabel.place(x=138, y=528)

        # height function does not work on macs... Height is based on font size, ie 2 = *2 font size
        self.webcamButton = tk.Button(self, text="Webcam", font="Times 16", command=self.start_Webcam(), width=5)
        self.webcamButton = tk.Button(self, text="Camera", font="Times 16", width=5)
        self.runButton = tk.Button(self, text="Detect", font="Times 16", command=self.showMarker, width=5)
        self.trackButton = tk.Button(self, text="OFF", font="Times 16", command=self.trackActivate, width=5)
        self.laserButton = tk.Button(self, text="OFF", font="Times 16", command=self.laserActivate, width=5)

        # x and y are offset in pixels
        self.webcamButton.place(x=50, y=378)
        self.runButton.place(x=50, y=425)
        self.trackButton.place(x=50, y=475)
        self.laserButton.place(x=50, y=525)

        # Arrow Cluster
        self.arrowUp=tk.PhotoImage(file="upArrow.gif")
        self.upButton=tk.Button(self, image=self.arrowUp, command=self.upControl)
        self.upButton.place(x=110, y=220-50)

        self.arrowDown = tk.PhotoImage(file="downArrow.gif")
        self.downButton = tk.Button(self, image=self.arrowDown, command=self.downControl)
        self.downButton.place(x=110, y=346-50)

        self.arrowLeft = tk.PhotoImage(file="leftArrow.gif")
        self.leftButton = tk.Button(self, image=self.arrowLeft, command=self.leftControl)
        self.leftButton.place(x=50, y=280-50)

        self.arrowRight = tk.PhotoImage(file="rightArrow.gif")
        self.rightButton = tk.Button(self, image=self.arrowRight, command=self.rightControl)
        self.rightButton.place(x=175, y=280-50)

    def upControl(self):
        #up controls
        exit()


    def downControl(self):
        #downControls
        exit()

    def leftControl(self):
        #leftControls
        exit()

    def rightControl(self):
        #rightControls
        exit()

    def showMarker(self):
        # If detected, then
        self.detectLabel.config(text="Detected", fg="green")

    def trackActivate(self):
        if self.trackButton['text'] == "OFF":
            self.trackButton.configure(text="ON")
        else:
            self.trackButton.configure(text="OFF")

    def laserActivate(self):
        if self.laserButton['text'] == "OFF":
            self.laserButton.configure(text="ON")
        else:
            self.laserButton.configure(text="OFF")

    def client_exit(self):
        exit()

    def start_Webcam(self):
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(targe=self.videoLoop(), args=())
        self.thread.start()


    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():

                check, self.frame = self.cap.read()

                self.frame = cv2.resize(self.frame, None, fx=0.4, fy=0.4)
                cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)

                self.lmain.imgtk = imgtk
                self.lmain.configure(image=imgtk)
                #self.lmain.after(10, self.videoLoop)

                if self.panel is None:
                    self.lmain.imgtk = imgtk
                    self.lmain.configure(image=imgtk)
                    #self.lmain.after(10, self.videoLoop)

                else:
                    self.lmain.imgtk = imgtk
                    self.lmain.configure(image=imgtk)

        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")


# Making our root window. Tk is a class from tkinter
root = tk.Tk()
root.geometry("1000x600")
app = Window(root)
#app.videoLoop()

# generates our window

root.mainloop()
