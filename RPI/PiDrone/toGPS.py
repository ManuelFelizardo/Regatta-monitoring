from math import radians, degrees, pi, sqrt, cos, sin, atan, asin, atan2
from geopy import units
from sympy import Point3D, Line3D, Plane, Matrix
from sympy.physics.vector import *
from geopy import Point
import numpy as np

def get_gps(tyleX,tyleY,coordX,coordY,gps,cameraAngle,droneOrientation,height,gyroscope):
    angleX=(coordX/(tyleX/2)-1)*(cameraAngle[0]/2)
    angleY = (coordY / (tyleY / 2) - 1) * (cameraAngle[1]/2)

    hypotenuseX=height/cos(radians(angleX))
    hypotenuseY=height/cos(radians(angleY))

    posObject=Point3D((hypotenuseX*sin(radians(angleX))),(hypotenuseY*sin(radians(angleY))),-height)

    print("pos3",posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())
    lineX = np.array([0,-cos(gyroscope[0]),-sin(gyroscope[0])])  
    lineY = np.array([-cos(gyroscope[1]),0,-sin(gyroscope[1])])
    CameraFocusLine=np.cross(lineX,lineY)
    value=atan2(CameraFocusLine[1],CameraFocusLine[0])
    print(value)
    h=sqrt(pow(CameraFocusLine[0],2)+pow(CameraFocusLine[1],2))
    value2=atan2(h,-CameraFocusLine[2]) 

    droneOrientation = radians(droneOrientation)
    rmatrixZ2 = Matrix(
        [[cos(value+droneOrientation), sin(value+droneOrientation), 0, 0], [-sin(value+droneOrientation), cos(value+droneOrientation), 0, 0],
         [0, 0, 1, 0], [0, 0, 0, 1]])
    rmatrixY = Matrix([[cos(-value2),0, -sin(-value2), 0],[0, 1, 0, 0],
                       [ sin(-value2),0, cos(-value2), 0], [0, 0, 0, 1]])
    value3=atan2(posObject.y,posObject.x)

    hypot=sqrt(pow(posObject.x,2)+pow(posObject.y,2))
    posObject = Point3D(hypot*cos(-value+value3),hypot*sin(-value+value3),-height)
    print("pos1",posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())
    posObject = posObject.transform(rmatrixY)
    print("pos2",posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())
    posObject = posObject.transform(rmatrixZ2)
    print("pos3",posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())   
    posObject=Point3D(posObject.x*(-height/posObject.z),posObject.y*(-height/posObject.z),-height)
    print("pos3",posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())
		
    value=atan2(posObject.y,posObject.x)
    value=-(value+pi/2)
    print(value+pi/2)
    print(atan2(posObject.y,posObject.x))
    gps_location=destination(gps,value,sqrt(pow(posObject.x,2)+pow(posObject.y,2))/1000)
    return (gps_location.latitude,gps_location.longitude)



def destination( point, bearing, distance):
        point = Point(point)
        lat1 = units.radians(degrees=point.latitude)
        lng1 = units.radians(degrees=point.longitude)


        d_div_r = float(distance) / 6372.795

        lat2 = asin(
            sin(lat1) * cos(d_div_r) +
            cos(lat1) * sin(d_div_r) * cos(bearing)
        )

        lng2 = lng1 + atan2(
            sin(bearing) * sin(d_div_r) * cos(lat1),
            cos(d_div_r) - sin(lat1) * sin(lat2)
        )

        return Point(units.degrees(radians=lat2), units.degrees(radians=lng2))





#print(get_gps(100,100,50,50,(40.639782, -8.677226),(90,90),-0,10,(radians(45),radians(0))))
print(get_gps(500, 500, 250, 250, (40.618972, -8.761278), (62.2, 48.8), -45, 20, (radians(-24.4), radians(-0))))
