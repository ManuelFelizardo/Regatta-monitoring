import memcache
import cv2
import numpy as np
import toGPS
from MSP_Thread import getDroneData
from MSP import MSP
from math import radians, degrees

def startDetection(capture):
    FRAME_WIDTH = 1280
    FRAME_HEIGHT= 720
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    data = mc.get("calibration")
    icol = (int(data["minHue"]), int(data["maxHue"]), int(data["minSat"]), int(data["maxSat"]), int(data["minBright"]), int(data["maxBright"]))
    print(icol)
    lowHue = int(data["minHue"])
    lowSat =  int(data["minSat"])
    lowVal = int(data["minBright"])
    highHue = int(data["maxHue"])
    highSat =  int(data["maxSat"])
    highVal = int(data["maxBright"])
    frame = capture.readFrame()
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    colorLow = np.array([lowHue,lowSat,lowVal])
    colorHigh = np.array([highHue,highSat,highVal])
    mask = cv2.inRange(frameHSV, colorLow, colorHigh)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    if len(contour_sizes)>0:
        biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
        x,y,w,h = cv2.boundingRect(biggest_contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

        xx = x+int(w/2)
        yy = y+int(h/2)





        print("X= " + str(xx))
        print("Y= " + str(yy))
        if(yy<FRAME_HEIGHT/2-75):
            print("Must go down")
        elif(yy>FRAME_HEIGHT/2 + 75):
            print("Must go up")

        if(xx>FRAME_WIDTH/2+100):
            print("Must go left")
        elif(xx<FRAME_WIDTH/2-100):
            print("Must go right")
 
        msp=MSP()
        droneData=getDroneData(msp)
        height=droneData['alt']
        if(height<2):
        	height=15
        print(droneData)
        #print(FRAME_WIDTH, FRAME_HEIGHT, xx, FRAME_HEIGHT - yy, (droneData['Lat'],droneData['Long']), (62.2,48.8), droneData['degree'], height ,(radians(droneData['angy']),-radians(droneData['angx'])))
        xx=FRAME_WIDTH/2
        yy=FRAME_HEIGHT
        result = toGPS.get_gps(FRAME_WIDTH, FRAME_HEIGHT, xx, FRAME_HEIGHT - yy, (droneData['Lat'],droneData['Long']), (62.2,48.8), droneData['degree'], height ,(radians(droneData['angy']),-radians(droneData['angx'])))
        print("%.16f" % result[0],"%.16f" %  result[1])
    else:
        print("CANT FIND ANYTHING")


# Initial HSV GUI slider values to load on program start.
#icol = (36, 202, 59, 71, 255, 255)    # Green	
#icol = (18, 0, 196, 36, 255, 255)  # Yellow
#icol = (89, 0, 0, 125, 255, 255)  # Blue
#icol = (0, 100, 80, 10, 255, 255)   # Red
#icol = (104, 117, 222, 121, 255, 255)   # test
#icol = (0, 0, 0, 255, 255, 255)   # New start


#icol = (33, 138, 20, 71, 255, 255)    # TestingVideo
#icol = (73, 45, 00,93, 255, 255)    # TestingCam
#icol = (00, 00,00, 255,255,255)  #TestingOrangePhone






'''
cv2.namedWindow('colorTest')
# Lower range colour sliders.
cv2.createTrackbar('lowHue', 'colorTest', icol[0], 255, nothing)
cv2.createTrackbar('lowSat', 'colorTest', icol[1], 255, nothing)
cv2.createTrackbar('lowVal', 'colorTest', icol[2], 255, nothing)
# Higher range colour sliders.
cv2.createTrackbar('highHue', 'colorTest', icol[3], 255, nothing)
cv2.createTrackbar('highSat', 'colorTest', icol[4], 255, nothing)
cv2.createTrackbar('highVal', 'colorTest', icol[5], 255, nothing)

# Initialize webcam. Webcam 0 or webcam 1 or ...
vidCapture = cv2.VideoCapture(0)
vidCapture.set(cv2.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
vidCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
print("ola")

P=1.2
I=1
D=0.001
objective=FRAME_HEIGHT/2
pid = PID.PID(P, I, D)
pid.SetPoint=objective
pid.setSampleTime(0.01)
feedback_list = []
time_list = []
setpoint_list = []


i=0
while True:

    #dict = request.getDroneData(1)
    timeCheck = time.time()

    # Get HSV values from the GUI sliders.
    lowHue = cv2.getTrackbarPos('lowHue', 'colorTest')
    lowSat = cv2.getTrackbarPos('lowSat', 'colorTest')
    lowVal = cv2.getTrackbarPos('lowVal', 'colorTest')
    highHue = cv2.getTrackbarPos('highHue', 'colorTest')
    highSat = cv2.getTrackbarPos('highSat', 'colorTest')
    highVal = cv2.getTrackbarPos('highVal', 'colorTest')
    
    # Get webcam frame
    #for i in range(0,10):


    _, frame = vidCapture.read()

   #frame=cv2.resize(frame,(500, 500));

    print(frame)
    # Show the original image.
    cv2.imshow('frame', frame)

    # Convert the frame to HSV colour model.
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # HSV values to define a colour range we want to create a mask from.
    colorLow = np.array([lowHue,lowSat,lowVal])
    colorHigh = np.array([highHue,highSat,highVal])
    mask = cv2.inRange(frameHSV, colorLow, colorHigh)
    # Show the first mask
    cv2.imshow('mask-plain', mask)

    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    if len(contour_sizes)>0:
        biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
        cv2.drawContours(frame, biggest_contour, -1, (0,255,0), 3)




        x,y,w,h = cv2.boundingRect(biggest_contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        print("X= " + str(x))
        print("Y= " + str(y))

        feedback=y
        #pid.update(feedback)
        #output = pid.output
        #print(output)
        #if pid.SetPoint > 0:
        #    feedback = y
        #if i>9:
        #    pid.SetPoint = objective
        #time.sleep(0.02)
        feedback_list.append(feedback)
        setpoint_list.append(pid.SetPoint)
        time_list.append(i)



        if(y<FRAME_HEIGHT/2-75):
            print("Must go down")
        elif(y>FRAME_HEIGHT/2 + 75):
            print("Must go up")

        if(x>FRAME_WIDTH/2+100):
            print("Must go left")
        elif(x<FRAME_WIDTH/2-100):
            print("Must go right")

        #dict = request.getDroneData(1)
        #(tyleX,tyleY,coordX,coordY,gps,cameraAngle,droneOrientation,height,gyroscope)
        #print(get_gps(100,100,50,50,(40.639782, -8.677226),(90,90),-0,10,(radians(45),radians(0))))
        #heigh=dict['alt']
        #if(heigh==0):
        #	heigh=1
        #print(FRAME_WIDTH, FRAME_HEIGHT, x, y, (dict['Lat'],dict['Long']), (62.2,48.8), -dict['degree'], heigh,(radians(dict['angx']),radians(dict['angy'])))
        #print(toGPS.get_gps(FRAME_WIDTH, FRAME_HEIGHT, x, y, (dict['Lat'],dict['Long']), (62.2,48.8), -dict['degree'], heigh,(radians(dict['angx']),radians(dict['angy']))))
        #cv2.drawContours(frame, contours, -1, (0,255,0), 3)
        
        #cv2.drawContours(frame, contours, 3, (0,255,0), 3)
        
        #cnt = contours[1]
        #cv2.drawContours(frame, [cnt], 0, (0,255,0), 3)

        # Show final output image
        cv2.imshow('colorTest', frame)
    else:
        print("CANT FIND ANYTHING")
   
	
    k = cv2.waitKey(1) & 0xFF
    if k == 1:
        break
  
    print('fps - ', 1/(time.time() - timeCheck))
'''