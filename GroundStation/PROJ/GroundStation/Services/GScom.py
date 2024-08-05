import json
import socket
import threading

import paho.mqtt.client as paho
import requests
# Name of this client. Don't use identical client IDs for differenfMartinat clients
import time
from converter import getCanvasPosition
from math import radians

clientID = 'GS'
DEBUG = 0
TOPIC = 'GS_TOPIC'
DRONE_IP = '192.168.1.102'


class MosquittoEndpoint:
    def __init__(self):
        self.mqttc = paho.Client(clean_session=True)

        self.mqttc.on_connect = self.onConnect
        self.mqttc.on_subscribe = self.onSubscribe
        self.mqttc.on_message = self.onMessage
        self.mqttc.on_disconnect = self.onDisconnect
        self.mqttc.connect(DRONE_IP, 1883, 60)
        self.mqttc.loop_start()
        self.videoReceiveLock = threading.Lock()
        self.launchCache = {}

    def onConnect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.mqttc.subscribe(TOPIC)

    def onSubscribe(self, client, userdata, mid, granted_qos):
        print('Subscribed on topic.')

    def onMessage(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        msg = json.loads(payload.replace('\'', '\"'))
        if msg['type'] == 'launch_ready_for_transmit':
            self.videoReceiveLock.acquire()
            fetch_video(msg['name'])
            self.createDataFile(msg['name'])
            self.videoReceiveLock.release()
            self.mqttc.publish("videoProcessing", payload='{"status": "finish", "name": "' + msg['name'] + '"}')
        elif msg['type'] == 'video_ready_for_transmit':
            fetch_video(msg['name'])
        elif msg['type'] == 'video_list_updated':
            publish_on_rest(msg['list'], msg['storage'])
        elif msg['type'] == 'transfer_videos':
            self.transfer_videos(msg['list'])
        elif msg['type'] == 'launch_data':
            try:
                if msg['name'] not in self.launchCache:
                    self.launchCache[str(msg['name'])] = []
                gpsData = [((k[1]["coords"][1],k[1]["coords"][0]),int(k[0])) for k in msg["gpsData"]]
                #pos = getCanvasPosition((msg["lat"], msg["log"]), gpsData, -radians(msg["ort"]), max(msg["alt"],15), (-radians(msg["angy"]),radians(msg["angx"])))
                pos = getCanvasPosition((gpsData[0][0][0], gpsData[0][0][1]), gpsData, -radians(msg["ort"]), max(msg["alt"],15), (-radians(msg["angy"]),radians(msg["angx"])))
                self.launchCache[str(msg['name'])].append((msg["timestamp"], pos))
            except:
                pass

    def onDisconnect(self, client, userdata, message):
        print("Disconnected from the broker.")

    def sendCommand(self, topic, payload):
        self.mqttc.publish(topic, payload=payload, qos=1, retain=False)

    def transfer_videos(self, list):
        for v in list:
            self.mqttc.publish("videoRequest", payload='{"type": "process_video", "name": "' + v + '"}')

    def createDataFile(self, name):
        with open('static/data/'+ name + '.data', 'w') as out:
            print(str(self.launchCache))
            temp = []
            for t in self.launchCache[str(name)]:
                h = []
                for d in t[1]:
                    h.append({"id": d, "x": int(t[1][d][1]), "y": int(t[1][d][0])})
                temp.append(h)
            json.dump(temp, out)


def fetch_video(name='launch'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('File transmission socket opened')
    while True:
        try:
            s.connect((DRONE_IP, 30000))
            n = s.recv(1024).decode('utf-8')
            with open('static/videos/'+str(n), 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    f.write(data)
            break
        except:
            continue

    f.close()
    s.close()
    print('File transmission socket finished')

def publish_on_rest(lista, storage):
    try:
        data = '{ "list": ' + str(lista).replace('\'', '\"') + ',"storage": ' + str(storage).replace('\'', '\"') + '}';
        r = requests.post('http://127.0.0.1:5000/put_videos', data)
        print('Drone video storage updated')
    except:
        pass


mosqEndpoint = MosquittoEndpoint()
mosqEndpoint.mqttc.loop_start()
time.sleep(10000)
