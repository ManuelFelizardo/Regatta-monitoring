import socket
import threading
from new import *
import structs


class MSP:

    messageDict = {
        '108': structs.Message.msp_attitude,
        '109': structs.Message.msp_altitude,
        '106': structs.Message.msp_raw_gps,
        '209': structs.Message.msp_set_wp,
        '104': structs.Message.msp_motor
    }

    class __MSP:
        def __init__(self, port=8182, mock=False):
            self.ip = str(socket.gethostbyname(socket.gethostname()))
            if not mock:
                self.multiWii = msp('/dev/ttyACM0')
            self.lock = threading.Lock()
            self.port = port
            self.ret=0
            self.retLock = threading.Lock()
        def __str__(self):
            return repr(self)
    instance = None
    def __init__(self):
        if not MSP.instance:
            MSP.instance = MSP.__MSP()
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def getInstance(self):
        return self.instance

    # Function to send a single msp message to the drone controller via usb
    def MSP_message(self,data=None):
        if data:
            self.lock.acquire()
            payload = data['payload']
            function = data['function']
            dictDrone = self.multiWii.sendCMDreceive(function, payload, MSP.messageDict[str(function)])
            while dictDrone == None:
                dictDrone = self.multiWii.sendCMDreceive(function, payload, MSP.messageDict[str(function)])
            if "_io" in dictDrone:
                del dictDrone['_io']
            self.lock.release()
            return dictDrone
        return
  
    def MSP_message_mock(self,data=None):
        self.lock.acquire()
        #print(123)
        self.lock.release()
        if data:
            return data

    def MSP_message_mock(self,data=None):
        self.lock.acquire()
        #print(123)
        self.lock.release()
        if data:
            return data
