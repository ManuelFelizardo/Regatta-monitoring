import json
import os
import cv2
import numpy as np
from flask import Flask, render_template, Response
import flask_restful
from flask import request
from flask_restful import reqparse
from flask_cors import CORS
import memcache
import time
import socket

DRONE_IP = '192.168.1.102'
cam_uri = 'udp://127.0.0.1:'
#cam_uri = 1
app = Flask(__name__, static_url_path='/static')
api = flask_restful.Api(app)
CORS(app)

msgDrone = None
boats = {}
files_in_drone = {}

dataBoats = None
dataDrone = None

calibration = {
    'minHue': 0,
    'maxHue': 255,
    'minSat': 0,
    'maxSat': 255,
    'minBright': 0,
    'maxBright': 255,
}
parser = reqparse.RequestParser()
parser.add_argument('values')
parser.add_argument('name')


class Calibration(flask_restful.Resource):
    def get(self):
        return calibration

    def post(self):
        args = parser.parse_args()
        values = json.loads(str(args['values']).replace('\'', '\"'))
        for k in values.keys():
            calibration[k] = int(values[k])
        return '', 201


class File():
    def __init__(self, name, path, date):
        self.path = path
        self.name = name
        self.date = date


@app.route('/')
def index():
    return "REST APPLICATION"


# 'udp://192.168.1.65:1001/'
def gen():
    while True:
        try:
            cap = cv2.VideoCapture('udp://127.0.0.1:10001')
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            im_enc=None
            while True:
                res, frame = cap.read()
                if res:
                    # print(frame)
                    try :
                        im_enc = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 200])[1]
                    except Exception as e:
                        print(e)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + im_enc.tobytes() + b'\r\n')
        except Exception as e:
            print(e)


# 'udp://192.168.1.65:1002/'
def genMask():
    while True:
        try:
            cap = cv2.VideoCapture("udp://127.0.0.1:10002")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            while True:
                frame = cap.read()[1]
                frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                colorLow = np.array([calibration['minHue'], calibration['minSat'], calibration['minBright']])
                colorHigh = np.array([calibration['maxHue'], calibration['maxSat'], calibration['maxBright']])
                mask = cv2.inRange(frameHSV, colorLow, colorHigh)
                # print(frame)
                im_enc = cv2.imencode('.jpeg', mask, [cv2.IMWRITE_JPEG_QUALITY, 200])[1]
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + im_enc.tobytes() + b'\r\n')
        except Exception as e:
            print(e)

# udp://192.168.1.65:1003/'
def genFinal():
    while True:
        try:
            cap = cv2.VideoCapture('udp://127.0.0.1:10003')
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            while True:
                frame = cap.read()[1]
                frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                colorLow = np.array([calibration['minHue'], calibration['minSat'], calibration['minBright']])
                colorHigh = np.array([calibration['maxHue'], calibration['maxSat'], calibration['maxBright']])
                mask = cv2.inRange(frameHSV, colorLow, colorHigh)
                # HSV values to define a colour range we want to create a mask from.
                im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
                if len(contour_sizes) > 0:
                    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
                    cv2.drawContours(frame, biggest_contour, -1, (0, 255, 0), 3)

                    x, y, w, h = cv2.boundingRect(biggest_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # print(frame)
                im_enc = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 200])[1]
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + im_enc.tobytes() + b'\r\n')
        except Exception as e:
            print(e)


# 'udp://192.168.1.65:1004/'
def genIdOverlay():
    cap = cv2.VideoCapture(cam_uri + "10004")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    font = cv2.FONT_HERSHEY_DUPLEX
    i = 0
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    dict = mc.get("positions")
    while True:
        if i > 1:
            dict = mc.get("imagePositions")
            i = 0

        frame = cap.read()[1]
        #print("Dicionário de posições: ", dict)
        if (dict != None):
            for id in dict:
                cv2.putText(frame, str(id), (int(dict[id][0] * (854 / 500)), int(dict[id][1] * (450 / 500))), font, 1,
                            (255, 255, 255), 2, cv2.LINE_AA)
        im_enc = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 200])[1]
        i += 1
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + im_enc.tobytes() + b'\r\n')


def genAnalog():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        frame = cap.read()[1]
        im_enc = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 200])[1]
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + im_enc.tobytes() + b'\r\n')


@app.route("/produce", methods=["POST"])
def produce():
    global boats
    msg1 = request.stream.read()
    message = json.loads(msg1.decode("utf-8"))
    boats[message['id']] = message
    return ""


@app.route("/produceDrone", methods=["POST"])
def produceDrone():
    global msgDrone
    msgDrone1 = request.stream.read()
    dataDrone = json.loads(msgDrone1.decode("utf-8"))
    msgDrone = json.dumps(dataDrone)
    return msgDrone


@app.route("/put_videos", methods=["POST"])
def produce_videos():
    global files_in_drone
    msg1 = request.stream.read()
    data = msg1.decode("utf-8")
    files_in_drone = data
    return ""


@app.route("/produceTimeID", methods=["POST"])
def produce_time_id():
    global msgTimeID
    msgTimeID = request.stream.read()
    return msgTimeID

@app.route("/launchData", methods=["POST"])
def produce_launchData():
    msg1 = request.stream.read()
    data = msg1.decode("utf-8")
    f = open('static/data/'+data+'.data')
    out = json.load(f)
    return str(out).replace('\'', '\"')

@app.route("/consumeTimeID")
def consume_time_id():
    return msgTimeID


@app.route("/GPSLocations.json")
def consume():
    data = {"type": "FeatureCollection", "features": []}
    if boats != {}:
        for x in boats:
            data["features"].append(boats[x])

    if msgDrone != None:
        data["features"].append(json.loads(msgDrone))

    return str(data).replace('\'', '\"')


@app.route('/video.mjpeg')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/mask.mjpeg')
def video_feed2():
    return Response(genMask(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/final.mjpeg')
def video_feed3():
    return Response(genFinal(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/analog.mjpeg')
def video_feed4():
    return Response(genAnalog(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/videoOverLay.mjpeg')
def video_feed5():
    return Response(genIdOverlay(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/videoParams')
def getValues():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/consume_videos_processing")
def consume_videos_processing():
    return str(files_in_drone).replace('\'', '\"')


@app.route("/getImages")
def consume_images():
    list_images = []

    path_images = 'static/images/'

    filelist_images = os.listdir(path_images)

    for file_images in filelist_images[:]:
        if not (file_images.endswith(".png")) and not file_images.endswith(".jpg"):
            filelist_images.remove(file_images)
        else:
            list_images.append(
                File("NAME", path_images + file_images, time.ctime(os.path.getctime(path_images + file_images))))
    json_images = '['
    for i, file in enumerate(list_images):
        s = len(list_images) - 1
        json_images += '{"imgPath": "' + file.path + '","name": "' + file.name + '", "date": "' + file.date + '"}'
        if i != s:
            json_images += ','
    json_images += ']'
    return json_images


@app.route("/getVideos")
def consume_videos():
    list_videos = []
    path_videos = 'static/videos/'
    filelist_videos = os.listdir(path_videos)
    for file_videos in filelist_videos[:]:
        if not (file_videos.endswith(".mp4")):
            filelist_videos.remove(file_videos)
        else:
            list_videos.append(
                File("NAME", path_videos + file_videos, time.ctime(os.path.getctime(path_videos + file_videos))))
    list_videos.sort(key=lambda x: x.path, reverse=True)
    json_videos = '['
    for i, file in enumerate(list_videos):
        s = len(list_videos) - 1
        json_videos += '{"videoPath": "' + file.path + '","name": "' + file.name + '", "date": "' + file.date + '"}'
        if i != s:
            json_videos += ','
    json_videos += ']'
    return json_videos


@app.route("/video_receive", methods=["POST"])
def video_receive():
    args = request.stream.read()

    name = json.loads(args.decode("utf-8"))
    s = socket.socket()
    time.sleep(5)
    s.connect((DRONE_IP, 30000))
    with open('static/videos/' + str(name['name']) + '.mp4', 'wb') as f:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)
    f.close()
    s.close()
    return '', 201


api.add_resource(Calibration, '/cal')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
