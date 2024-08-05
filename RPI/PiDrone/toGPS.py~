from math import radians, degrees
from geopy import units
from sympy import *
from sympy.physics.vector import *
from geopy import Point


def get_gps(tyleX,tyleY,coordX,coordY,gps,cameraAngle,droneOrientation,height,gyroscope):
    angleX=(coordX/(tyleX/2)-1)*(cameraAngle[0]/2)
    angleY = (coordY / (tyleY / 2) - 1) * (cameraAngle[1]/2)
    hypotenuseX=height/cos(radians(angleX))
    hypotenuseY=height/cos(radians(angleY))

    planeZ=Plane(Point3D(0, 1, -height), Point3D(1, 0, -height), Point3D(0, 0, -height))
    posObject=Point3D((hypotenuseX*sin(radians(angleX))).evalf(),(hypotenuseY*sin(radians(angleY))).evalf(),-height)
    print("distance",sqrt(pow(posObject.x, 2)+pow(posObject.y, 2)).evalf())
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
    posObject=Point3D(posObjectY.x*(-height/posObjectY.z),posObjectY.y*(-height/posObjectY.z),-height)
    droneOrientation = radians(droneOrientation)
    rmatrix = Matrix(
        [[cos(droneOrientation), sin(droneOrientation), 0, 0], [-sin(droneOrientation), cos(droneOrientation), 0, 0],
         [0, 0, 1, 0], [0, 0, 0, 1]])
    posObject=posObject.transform(rmatrix)
    print(posObject.x.evalf(), posObject.y.evalf(), posObject.z.evalf())
    object_line=Line3D(posObject,Point3D(0,0,0))
    posObject=object_line.intersection(planeZ)
    posObject=posObject[0]
    if posObject.x==0:
        if posObject.y>0:
            value=(pi/2)
        else:
            value=-(pi/2)
    else:
        if posObject.x<0:
            value=atan(posObject.y/posObject.x)+pi
        else:
            value=atan(posObject.y/posObject.x)
    value=-(value-pi/2)
    gps_location=destination(gps,value,sqrt(pow(posObject.x,2)+pow(posObject.y,2))/1000)
    return (gps_location.latitude,gps_location.longitude)



def destination( point, bearing, distance):
        print("bearing:",bearing.evalf())
        point = Point(point)
        print(point.latitude)
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
#print(get_gps(500, 500, 0, 0, (40.6329514, -8.6601084), (62.2, 48.8), -0, 20, (radians(-45), radians(-0))))