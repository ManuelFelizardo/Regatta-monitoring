import json
import threading
import time
import paho.mqtt.client as paho
import memcache
from threading import Thread
import socket
from math import radians
from Api import *
from converter import getCanvasPosition
import requests

DRONE_IP = "192.168.1.102"


def on_message_drone(mosq, obj, msg):
    if msg.topic == 'droneInfo':
        data = json.loads(msg.payload.decode("utf-8"))
        modules = {}
        modules['id'] = 0
        modules['deviceId'] = 1
        modules['type'] = 'drone'
        modules['degree'] = data["ort"]
        lst = [data['log'], data['lat']]
        modules['coords'] = lst
        publish_on_rest(modules)
        if get_running(mosq) == 1:
            set_running(mosq, 2)
            mc = memcache.Client(['127.0.0.1:11211'], debug=0)
            dic = mc.get("id")
            if (dic != None):
                thread = Thread(target=calculate_positions, args=(mosq, data, dic, mc,))
                thread.start()
            else:
                set_running(mosq,1)

    elif msg.topic == 'calculate':
        data = json.loads(msg.payload.decode("utf-8"))
        if data["value"] == 1:
            if get_running(mosq) == 0:
                set_running(mosq, 1)
        elif data["value"] == 0:
            mc = memcache.Client(['127.0.0.1:11211'], debug=0)
            mc.set("imagePositions", None)
            set_running(mosq, 0)


def calculate_positions(instance, data, dic, mc):
    gpsList = [(dic[t], t) for t in dic]
    gyroscope = (-radians(data["angy"]), radians(data["angx"]))
    gps = (data["lat"], data["log"])\

    cameraOrientation = radians(data["ort"])
    if data["alt"] <= 2:
        droneHeight = 25
    else:
        droneHeight = data["alt"]
    result = getCanvasPosition(gpsList[0][0], gpsList, cameraOrientation, droneHeight, gyroscope)
    mc.set("imagePositions", result)
    time.sleep(0.1)
    set_running(instance, 1)


def on_message_boat(mosq, obj, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    dict = mc.get("id")
    if dict == None:
        dict = {}
    dict[data["id"]] = (data["coords"][1], data["coords"][0])
    mc.set("id", dict)
    publish_on_rest(data)


def publish_on_rest(dic, ip="192.168.1.103"):
    try:
        r = requests.post('http://' + ip + ':5000/produce', json.dumps(dic))
    except:
        pass


def on_publish(mosq, obj, mid):
    pass


class CalculateImagePositions(threading.Thread):
    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message_drone
        self.on_publish = on_publish

    def run(self):

        while True:
            client = paho.Client(clean_session=True)
            client.on_message = self.on_message
            client.on_publish = self.on_publish
            client.connect(DRONE_IP, 1883, 60)
            client.subscribe("droneInfo", 2)
            client.subscribe("calculate", 1)
            client.lockRun = threading.Lock()
            client.running = 0
            client.set_running = set_running
            client.get_running = get_running
            while client.loop() == 0:
                pass


def set_running(mosq, i):
    mosq.lockRun.acquire()
    mosq.running = i
    mosq.lockRun.release()


def get_running(mosq):
    mosq.lockRun.acquire()
    var = mosq.running
    mosq.lockRun.release()
    return var


class UpdateBoatPosition(threading.Thread):
    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message_boat
        self.on_publish = on_publish

    def run(self):
        client = paho.Client()
        client.on_message = self.on_message
        client.on_publish = self.on_publish
        client.connect(DRONE_IP, 1883, 60)
        client.subscribe("id", 0)

        while client.loop() == 0:
            pass


class VideoSplitter(threading.Thread):
    def run(self):
        NUM = 4
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', 10000))
        while True:
            try:
                data, addr = s.recvfrom(4096 * 100)
                for i in range(0, NUM):
                    try:
                        s.sendto(data, ('127.0.0.1', 10001 + i))
                    except:
                        continue
            except:
                continue


if __name__ == '__main__':
    updateBoatPosition = UpdateBoatPosition(on_message_boat, on_publish)
    updateBoatPosition.start()
    calculateImagePositions = CalculateImagePositions(on_message_drone, on_publish)
    calculateImagePositions.start()
    videoSplitter = VideoSplitter()
    videoSplitter.start()

    # app.run(host='0.0.0.0', debug=True, threaded=True)
