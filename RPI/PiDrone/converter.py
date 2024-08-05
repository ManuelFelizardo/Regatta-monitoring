from math import radians, degrees
from sympy import *
import math


def calculate_initial_compass_bearing(pointA, pointB):

    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])

    diffLong = radians(pointB[1] - pointA[1])

    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1)
            * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    initial_bearing = initial_bearing
    #print("laasafaf", initial_bearing)
    return initial_bearing


def getPlanes(originalOrientation,height):

    posDrone=Point3D(0,0,height)
    #pointX = Point3D(cos(originalOrientation + pi) * cos(giroscope[1]),sin(originalOrientation + pi) * cos(giroscope[1]), height + sin(giroscope[1]))
    #pointY=Point3D(cos(originalOrientation+pi/2)*cos(giroscope[0]),sin(originalOrientation+pi/2)*cos(giroscope[0]),height+sin(giroscope[0]))
    point1=Point3D(cos(originalOrientation),sin(originalOrientation),0)
    point2=Point3D(cos(originalOrientation-pi),sin(originalOrientation-pi),0)
    point3=Point3D(cos(originalOrientation+pi/2),sin(originalOrientation+pi/2),0)
    point4=Point3D(cos(originalOrientation-pi/2),sin(originalOrientation-pi/2),0)
    planeX=Plane(posDrone,point3,point4)
    #print(planeX)
    planeY=Plane(posDrone,point1,point2)
    #print(planeY)
    #print(1234)
    return(planeX,planeY)

def getPlanes2(originalOrientation,height):

    pos=Point3D(0,0,1)
    point1=Point3D(1,0,0)
    point2=Point3D(-1,0,0)
    point3=Point3D(0,1,0)
    point4=Point3D(0,-1,0)
    planeX=Plane(pos,point3,point4)
    #print(planeX)
    planeY=Plane(pos,point1,point2)
    #print(planeY)
    return(planeX,planeY)

"""
def getAngles(originalOrientation,height,objectBearing,objectDistance):
    planes=getPlanes(originalOrientation,height)
    posDrone=Point3D(0,0,height)
    posObject=Point3D(objectDistance*cos(objectBearing),objectDistance*sin(objectBearing),0)
    line=Line3D(posDrone,posObject)
    angleX=planes[0].angle_between(line).evalf()
    angleY=planes[1].angle_between(line).evalf()
    return(angleX,angleY)
    
"""

def getAngles(originalOrientation,height,objectBearing,objectDistance,gyroscope):
    planes=getPlanes2(originalOrientation,height)
    #gyroscope[0]= -gyroscope[0]
    #gyroscope[1] = -gyroscope[1]
    posDrone=Point3D(0,0,0)
    print(objectDistance)
    print(objectBearing)
    if(math.isnan(objectBearing)):
        posObject=Point3D(0,0,-height)
    else:
        posObject=Point3D(objectDistance*sin(objectBearing),objectDistance*cos(objectBearing),-height)
    #print(posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())

    planeZ=Plane(Point3D(0, 1, -height), Point3D(1, 0, -height), Point3D(0, 0, -height))

    rmatrixX = Matrix([[1, 0, 0, 0], [0, cos(gyroscope[0]), sin(gyroscope[0]), 0],
                       [0, -sin(gyroscope[0]), cos(gyroscope[0]), 0], [0, 0, 0, 1]])
    rmatrixY = Matrix([[cos(gyroscope[1]),0, -sin(gyroscope[1]), 0],[0, 1, 0, 0],
                       [ sin(gyroscope[1]),0, cos(gyroscope[1]), 0], [0, 0, 0, 1]])
    posObjectX = posObject.transform(rmatrixY)
    object_line = Line3D(posObjectX, Point3D(0, 0, 0))
    posObjectX = object_line.intersection(planeZ)[0]
    posObjectY = posObjectX.transform(rmatrixX)
    object_line = Line3D(posObjectY, Point3D(0, 0, 0))
    posObjectY = object_line.intersection(planeZ)[0]
    posObject = Point3D(posObjectY.x * (-height / posObjectY.z), posObjectY.y * (-height / posObjectY.z), -height)

    #print(posObject.x.evalf(),posObject.y.evalf(),posObject.z.evalf())

    rmatrix = Matrix(
        [[cos(originalOrientation), sin(originalOrientation), 0, 0], [-sin(originalOrientation), cos(originalOrientation), 0, 0],
         [0, 0, 1, 0], [0, 0, 0, 1]])
    posObject=posObject.transform(rmatrix)
    #print(posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())
    line=Line3D(posDrone,posObject)
    #print("lele",line)
    angleX=planes[0].angle_between(line).evalf()
    angleY=planes[1].angle_between(line).evalf()
    angleX=atan2(-posObject.x,height)
    angleY=atan2(posObject.y,height)
    return(angleX,angleY)

def getObjectCameraAngle(gps1,gps2,cameraOrientation,droneHeight,gyroscope):
    #dist=geopy.distance.vincenty(gps1, gps2).m

    dlon = radians(gps2[1]) - radians(gps1[1])
    dlat = radians(gps2[0])- radians(gps1[0])

    a = sin(dlat / 2) ** 2 + cos(radians(gps1[0])) * cos(radians(gps2[0])) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    R = 6372795
    dist= R * c
    #print("distance", dist)

    objectBearing=calculate_initial_compass_bearing(gps1,gps2)
    result=getAngles(cameraOrientation,droneHeight,objectBearing,dist,gyroscope)
    return result




def getObjectCameraPos(objectAngles,cameraAngle):
    #print("lala",objectAngles)
    #print(degrees(objectAngles[0]),degrees(objectAngles[1]))
    return (-degrees(objectAngles[0])/(cameraAngle[0]/2)*250+250,degrees(objectAngles[1])/(cameraAngle[1]/2)*250+250)

def getCanvasPosition(gps1, gps2, cameraOrientation, droneHeight, gyroscope, cameraAngles=(62.2, 48.8)):
    objectAngles = getObjectCameraAngle(gps1, gps2, cameraOrientation, droneHeight, gyroscope)
    objectCameraPos = getObjectCameraPos(objectAngles, cameraAngles)
    return objectCameraPos

"""
gps1=(40.6329514, -8.6601084)
gps2=(40.633018987427825, -8.660247457207692)
gps2=(40.632951399875445, -8.659938454039345)
cameraOrientation=0
droneHeight=20
gyroscope=(-radians(-45), -radians(-0))

cameraAngles=(62.2, 48.8)
objectAngles=getObjectCameraAngle(gps1,gps2,cameraOrientation,droneHeight,gyroscope)
objectCameraPos=getObjectCameraPos(objectAngles,cameraAngles)
#print(objectAngles)
print(123)
print(objectCameraPos)
"""
