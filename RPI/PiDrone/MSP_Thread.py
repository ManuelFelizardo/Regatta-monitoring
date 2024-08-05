import json
import threading
import memcache
import time
import socket
from MSP import MSP

payloadStart=[255,1]
payloadEnd=[0,0,0]
payload_base={
        "wp_no" : 255,
        "action" : 1,
        "p2" :0,
        "p3" : 0,
        "nav_flag" : 0
    }

def send_msp(msp, function, payload=[]):
    dict = {"payload": payload, "function": function}
    data=msp.MSP_message(dict)
    return data


def getDroneData(msp):
    dict = send_msp(msp, 108)
    dict2 = send_msp(msp, 106)
    dict3 = send_msp(msp, 109)
    droneData={}
    droneData["degree"] = dict["heading"]
    droneData["angx"]=dict["angx"]/10.0
    droneData["angy"] = dict["angy"]/10.0
    droneData["Lat"] = dict2['coord_lat'] / 10000000.0
    droneData["Long"] = dict2['coord_lon'] / 10000000.0
    droneData["alt"]=dict3['alt']/100
    return droneData


def follow_boat_loop(msp,boatGps,altitude=15,heading=0):
    payload=payloadStart+[boatGps[0],boatGps[1],altitude,heading]+payloadEnd
    data=send_msp(msp,209,payload=payload)

def startFollowing(msp,deviceId,altitude=15,heading=0):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    msp.retLock.acquire()
    ret=msp.ret
    if (ret == 1):
        msp.retLock.release()
        return
    msp.ret=1
    msp.retLock.release()
    while ret == 1 :
        msp.retLock.acquire()
        ret=msp.ret
        data=mc.get("data")
        point=data[deviceId]["coords"]
        follow_boat_loop(msp,point,altitude,heading)
        msp.retLock.release()
        time.sleep(0.1)

def goToPosition(msp,gpsPos,altitude=20,heading=0):
    msp.retLock.acquire()
    ret=msp.ret
    if (ret == 1):
        msp.retLock.release()
        return
    msp.ret=1
    msp.retLock.release()
    follow_boat_loop(msp,gpsPos,altitude,heading)

def stopFollowing(msp):
    msp.retLock.acquire()
    msp.ret=0
    msp.retLock.release()

def go_to_buoy(msp, buoy_id,altitude,heading=0):
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    data = mc.get("data")
    if buoy_id in data:
        point = data[buoy_id]["coords"]
        payload=payloadStart+[point[0],point[1],altitude,heading]+payloadEnd
        data=send_msp(msp,209,payload=payload)






