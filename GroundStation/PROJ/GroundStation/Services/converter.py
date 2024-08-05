import time
from math import radians, degrees
from sympy import *
import math
import numpy as np


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

    return initial_bearing


def getPlanes():
    pos = Point3D(0, 0, 1)
    point1 = Point3D(1, 0, 0)
    point2 = Point3D(-1, 0, 0)
    point3 = Point3D(0, 1, 0)
    point4 = Point3D(0, -1, 0)
    planeX = Plane(pos, point3, point4)
    planeY = Plane(pos, point1, point2)

    return (planeX, planeY)


def getDistance(gps1, gps2):
    dlon = radians(gps2[1]) - radians(gps1[1])
    dlat = radians(gps2[0]) - radians(gps1[0])

    a = sin(dlat / 2) ** 2 + cos(radians(gps1[0])) * cos(radians(gps2[0])) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    R = 6372795
    dist = R * c
    return dist


def getAnglesList(gps1, gpslist, originalOrientation, height, gyroscope):
    planes = getPlanes()

    posDrone = Point3D(0, 0, 0)

    lineX = np.array([0, -cos(gyroscope[0]), -sin(gyroscope[0])])
    lineY = np.array([-cos(gyroscope[1]), 0, -sin(gyroscope[1])])
    CameraFocusLine = np.cross(lineX, lineY)
    value = -atan2(CameraFocusLine[1], CameraFocusLine[0])
    print("value", value)
    h = sqrt(pow(CameraFocusLine[0], 2) + pow(CameraFocusLine[1], 2))
    value2 = atan2(h, -CameraFocusLine[2])

    droneOrientation = radians(originalOrientation)
    rmatrixZ2 = Matrix(
        [[cos(value + droneOrientation), sin(value + droneOrientation), 0, 0],
         [-sin(value + droneOrientation), cos(value + droneOrientation), 0, 0],
         [0, 0, 1, 0], [0, 0, 0, 1]])
    rmatrixY = Matrix([[cos(-value2), 0, -sin(-value2), 0], [0, 1, 0, 0],
                       [sin(-value2), 0, cos(-value2), 0], [0, 0, 0, 1]])

    """
    rmatrixX = Matrix([[1, 0, 0, 0], [0, cos(gyroscope[0]), sin(gyroscope[0]), 0],
                       [0, -sin(gyroscope[0]), cos(gyroscope[0]), 0], [0, 0, 0, 1]])
    rmatrixY = Matrix([[cos(gyroscope[1]), 0, -sin(gyroscope[1]), 0], [0, 1, 0, 0],
                       [sin(gyroscope[1]), 0, cos(gyroscope[1]), 0], [0, 0, 0, 1]])
    rmatrix = Matrix(
        [[cos(originalOrientation), sin(originalOrientation), 0, 0],
         [-sin(originalOrientation), cos(originalOrientation), 0, 0],
         [0, 0, 1, 0], [0, 0, 0, 1]])
    """

    angles = {}
    for gps in gpslist:
        objectDistance = getDistance(gps1, gps[0])
        objectBearing = calculate_initial_compass_bearing(gps1, gps[0])
        if (math.isnan(objectBearing)):
            posObject = Point3D(0, 0, -height)
        else:
            # posObject=Point3D(objectDistance*sin(objectBearing),objectDistance*cos(objectBearing),-height)
            posObject = Point3D(objectDistance * cos(-value + objectBearing),
                                objectDistance * sin(-value + objectBearing), -height)
        print("pos1", posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())
        posObject = posObject.transform(rmatrixY)
        print("pos2", posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())
        posObject = posObject.transform(rmatrixZ2)
        print("pos3", posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())
        posObject = Point3D(posObject.x * (-height / posObject.z), posObject.y * (-height / posObject.z), -height)
        print("pos4", posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())

        """
        posObject = posObject.transform(rmatrix)

        #print("---",posObject.x.evalf(),posObject.y.evalf())
        posObject1 = posObject.transform(rmatrixX)
        posObject1 = posObject1.transform(rmatrixY)

        posObject2 = posObject.transform(rmatrixY)
        posObject2 = posObject2.transform(rmatrixX)
        #print("---",posObject1)
        #print("...",posObject2)

        #posObjectY = Point3D(posObjectY.x * (-height / posObjectY.z), posObjectY.y * (-height / posObjectY.z), -height)

        posObject = Point3D(posObject1.x * (-height / posObject1.z), posObject2.y * (-height / posObject2.z), -height)
        """

        # posObject = posObject.transform(rmatrix)
        line = Line3D(posDrone, posObject)
        angleX = planes[0].angle_between(line).evalf()
        angleY = planes[1].angle_between(line).evalf()
        angleX = atan2(-posObject.x, height)
        angleY = atan2(posObject.y, height)
        print(angleX.evalf(), angleY.evalf())
        angles[gps[1]] = (angleX, angleY)

    return angles


def getObjectCameraPos(objectAngles, cameraAngle):
    result = {}
    for angle in objectAngles:
        result[angle] = (-degrees(objectAngles[angle][0]) / (cameraAngle[0] / 2) * 250 + 250,
                         500 - (degrees(objectAngles[angle][1]) / (cameraAngle[1] / 2) * 250 + 250))
    return result


def getCanvasPosition(gps1, gpsList, cameraOrientation, droneHeight, gyroscope, cameraAngles=(62.2, 48.8),
                      canvasSize=None):
    objectAngles = getAnglesList(gps1, gpsList, cameraOrientation, droneHeight, gyroscope)
    objectCameraPos = getObjectCameraPos(objectAngles, cameraAngles)
    if canvasSize != None:
        for pos in objectCameraPos:
            objectCameraPos[pos][0] = objectCameraPos[pos][0] * (canvasSize[0] / 500)
            objectCameraPos[pos][1] = objectCameraPos[pos][1] * (canvasSize[1] / 500)
    return objectCameraPos


"""
gps1=(40.618972, -8.761278)
#gpsList=[[(40.632951399875445, -8.659938454039345),1],[(40.633018987427825, -8.660247457207692),2],[(40.633018987427825, -8.660247457207692),4],[(40.633018987427825, -8.660247457207692),3],[(40.633018987427825, -8.660247457207692),5],[(40.633018987427825, -8.660247457207692),6]]
gpsList=[[(40.61907454743543, -8.761458624940305),1]]
cameraOrientation=radians(0)
droneHeight=20
gyroscope=(radians(25), radians(25))

cameraAngles=(50, 50)
time1=time.time()
print(getCanvasPosition(gps1,gpsList,cameraOrientation,droneHeight,gyroscope,cameraAngles))
print(time.time()-time1)
"""
