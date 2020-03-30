from pid import PID
from tracking import colorTracking

from multiprocessing import Manager, Process

from imutils.video import VideoStream
import cv2



class motorControls:

    def __init__(self):
        self.upLimit = 200
        self.dwnLimit = 200
        centX = 300
        centY = 225

    def motionOut(self, center):
        objX = center[0]
        objY = center[1]
        movX = objX - centX
        movY = objY - centY

    def obj_center(objX, objY, centerX, centerY):
        vs = VideoStream(0).start()

        while True:
            frame = vs.read()
            (H,W) = frame.shape[:2]
            centerX.value = w // 2
            centerY.value = H // 2

            trackingFeed = colorTracking.Tracking(frame, True)
            
            (objX.Value, objY.Value) = trackingFeed[1]

            print(objX.Value)
            print(objY.Value)

            cv2.imshow("Tracking", frame)
            

    def pid_process(output, p, i, d, objCoord, centerCoord):
        p = PID(p.value, i.value, d.value)
        p.initialize()

        while True:
            error = centerCoord.value - objCoord.value
            output.value = p.update(error)

    def in_range(val, start, end):
        return (val >= start and val <= end)

    def set_motors(pan, tilt):
        while True:
            panAngle = -1 * pan.value
            tiltAngle = -1 * tilt.value

            if in_range(tiltAngle, self.upLimit, self.dwnLimit):
                tiltAngle

    if __name__=="__main__":

        with Manager() as manager:
            centerX = manager.Value("i", 0)
            centerY = manager.Value("i", 0)

            objX = manager.Value("i", 0)
            objY = manager.Value("i", 0)

            pan = manager.Value("i", 0)
            tilt = manager.Value("i", 0)

            # set PID values for panning
            panP = manager.Value("f", 0.09)
            panI = manager.Value("f", 0.08)
            panD = manager.Value("f", 0.002)
            # set PID values for tilting
            tiltP = manager.Value("f", 0.11)
            tiltI = manager.Value("f", 0.10)
            tiltD = manager.Value("f", 0.002)

            # we have 4 independent processes
            # 1. objectCenter  - finds/localizes the object
            # 2. panning       - PID control loop determines panning angle
            # 3. tilting       - PID control loop determines tilting angle
            # 4. setServos     - drives the servos to proper angles based
            #                    on PID feedback to keep object in center
            processObjectCenter = Process(target=obj_center,
                args=(objX, objY, centerX, centerY))

            processPanning = Process(target=pid_process,
                args=(pan, panP, panI, panD, objX, centerX))

            processTilting = Process(target=pid_process,
                args=(tilt, tiltP, tiltI, tiltD, objY, centerY))

            processSetServos = Process(target=set_motors, args=(pan, tilt))

            # start all 4 processes
            processObjectCenter.start()
            processPanning.start()
            processTilting.start()
            processSetServos.start()

            # join all 4 processes
            processObjectCenter.join()
            processPanning.join()
            processTilting.join()
            processSetServos.join()

            # disable the servos
            pth.servo_enable(1, False)
            pth.servo_enable(2, False)

motorControls()