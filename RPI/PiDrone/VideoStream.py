import socket
import threading
import ffmpy
import numpy
import paho
import picamera
import memcache
import subprocess
import os
import paho.mqtt.client as paho
from MSP_Thread import *


class CameraBuffer:
    def __init__(self, sock, DEST):
        self.sock = sock
        self.DEST = DEST

    def write(self, buf):
        self.sock.sendto(buf, self.DEST)


class VideoCapture(threading.Thread):
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    def __init__(self, config, group=None, target=None, name=None):
        super().__init__(group=group, target=target, name=name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.config = config
        self.DEST = (config["DEFAULT"]["GroundStation_IP"], int(config["video-live"]["Port"]))
        self.recording = False
        self.recordingLaunch = False
        self.launchName = None
        self.camera = picamera.PiCamera(sensor_mode=int(config["video-main"]["Sensor_Mode"]))
        self.camera.resolution = (int(config["video-main"]["Width"]), int(config["video-main"]["Height"]))
        self.camera.framerate = int(config["video-main"]["Framerate"])
        self.camera.exposure_mode = 'sports'
        self.outputStream = CameraBuffer(self.server_socket, self.DEST)
        self.semSocket = threading.Lock()
        self.launchDataThread = False

    def run(self):
        try:
            self.camera.start_recording(self.outputStream, format='h264', splitter_port=2, resize=(int(self.config["video-live"]["Width"]), int(self.config["video-live"]["Height"])),
                                        bitrate=int(float(self.config["video-live"]["Bitrate"])*1000000))
            print('Video Stream Started')
            self.camera.wait_recording(1000000, splitter_port=2)
        finally:
            if self.recording:
                self.camera.stop_recording(splitter_port=1)
            if self.recordingLaunch:
                self.camera.stop_recording(splitter_port=3)
            self.camera.stop_recording(splitter_port=2)
            self.server_socket.close()

    def stop(self):
        if self.record:
            self.camera.stop_recording(splitter_port=1)
            print('Video Recording Stopped')
        self.camera.stop_recording(splitter_port=2)
        print('Video Stream Stopped')

    def readFrame(self):
        image = numpy.empty((int(self.config["image-processing"]["Height"]) * int(self.config["image-processing"]["Width"]) * 3,), dtype=numpy.uint8)
        self.camera.capture(image, 'bgr')
        image = image.reshape((int(self.config["image-processing"]["Height"]), int(self.config["image-processing"]["Width"]), 3))
        return image

    def record(self, name):
        if not self.recording:
            self.camera.start_recording("Videos/" + name + '.h264', splitter_port=1, format='h264',resize=(int(self.config["video-main"]["Width"]), int(self.config["video-main"]["Height"])),
                                        bitrate=int(float(self.config["video-main"]["Bitrate"])*1000000))
            self.recording = True
            return True
        return False

    def stopRecord(self):
        if self.recording:
            self.camera.stop_recording(splitter_port=1)
            self.recording = False
            return True
        return False

    def recordLaunch(self, name):
        msp = MSP()
        if not self.recordingLaunch:
            self.camera.start_recording(name + '.h264', splitter_port=3, format='h264',resize=(int(self.config["video-recording-launch"]["Width"]), int(self.config["video-recording-launch"]["Height"])),
                                        bitrate=int(float(self.config["video-recording-launch"]["Bitrate"])*1000000))
            self.launchName = name
            self.recordingLaunch = True
            return True
        return False

    def stopRecordLaunch(self):
        if self.recordingLaunch:
            self.camera.stop_recording(splitter_port=3)
            self.processVideoLaunch(self.launchName)
            name = self.launchName
            self.launchName = None
            self.recordingLaunch = False
            return name
        return None

    def sendFile(self, name):
        try:
            t = threading.Thread(target=self.sendFileAssist, args=(name,))
            t.start()
        except:
            pass

    def sendFileAssist(self, name):
        print('Binding socket for file transmission')
        self.semSocket.acquire()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 30000))
        s.listen(0)
        conn, addr = s.accept()  # Establish connection with client.
        print('Starting video transmission')
        f = open(name, 'rb')
        conn.send(name.split("/")[-1].encode())
        l = f.read(1024)
        while (l):
            conn.send(l)
            l = f.read(1024)
        f.close()
        conn.close()
        s.shutdown(2)
        s.close()
        self.semSocket.release()
        os.system('rm ' + name)
        print('Stopping file transmission')

    def listVideos(self):
        path_videos = 'Videos/'
        videos = os.listdir(path_videos)
        result = subprocess.run(['df', '-h'], stdout=subprocess.PIPE)
        r = result.stdout.decode('utf-8').split('\n')
        storage = {}
        for line in r:
            line_split = line.split(' ')
            if line_split[0].strip() == '/dev/root':
                cont = 0
                for s in line_split[1:]:
                    if s != '':
                        if cont ==0:
                            storage['total_space'] = s
                        elif cont ==1:
                            storage['used_space'] = s
                        elif cont ==2:
                            storage['availiable_space'] = s
                        elif cont ==3:
                            storage['percentage_used'] = s
                        cont += 1
        return [f.split('.')[0] for f in videos], storage

    def processVideo(self, name):
        try:
            os.system('mv Videos/' + name + '.h264 Processing/Videos/' + name + '.h264')
            ff = ffmpy.FFmpeg(global_options='-framerate ' + self.config["video-main"]["Framerate"] +' -y',
                              inputs={'Processing/Videos/' + name + '.h264': None},
                              outputs={'Processing/' + name + '.mp4': '-c:v copy -f mp4'})
            ff.run()
            os.system('rm Processing/Videos/' + name + '.h264')
        except:
            pass

    def processVideoLaunch(self, name):
        try:
            ff = ffmpy.FFmpeg(global_options='-framerate '+ self.config["video-main"]["Framerate"] +' -y',
                              inputs={name + '.h264': None},
                              outputs={name + '.mp4': '-c:v copy -f mp4'})
            ff.run()
            os.system('rm ' + name + '.h264')
        except:
            pass

    def launchDataGenerator(self, name):
        msp = MSP()
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        timestamp = 0
        requestsPerSecond = int(self.config["video-recording-launch"]["DataReadingsPerSecond"])
        info = {}
        while True:
            time.sleep(1 / requestsPerSecond)
            data = getDroneData(msp)
            info["timestamp"] = timestamp
            timestamp += 1
            info["lat"] = data["Lat"]
            info["log"] = data["Long"]
            info["ort"] = data["degree"]
            info["alt"] = data["alt"]
            info["angx"] = data["angx"]
            info["angy"] = data["angy"]
            info["name"] = name
            info["type"] = 'launch_data'
            gpsData = mc.get("data")
            gps = []
            if gpsData:
                gps = [[str(k), gpsData[k]] for k in gpsData]
            info["gpsData"] = gps
            #print(gps)
            yield (info)

    def launchData(self, name, client):
        if not self.launchDataThread:
            self.launchDataThread = True
            t = threading.Thread(target=self.launchDataAssist, args=(name, client))
            t.start()

    def launchDataAssist(self, name, client):
        for data in self.launchDataGenerator(name):
            if not self.launchDataThread:
                break
            # print("Launch data: " + str(data))
            print(data)
            client.publish("GS_TOPIC", payload=str(data), qos=2)

    def stopLaunchData(self):
        self.launchDataThread = False
