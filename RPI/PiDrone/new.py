import construct
from construct import *
import serial
import time
import structs
import sys, os

class msp:

    def __init__(self, serPort):

        self.ser = serial.Serial()
        self.ser.port = serPort
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        """Time to wait until the board becomes operational"""
        wakeup = 2
        try:
            self.ser.open()
            for i in range(1, wakeup):
                time.sleep(1)
        except Exception as error:
            print("\n\nError opening " + self.ser.port + " port.\n" + str(error) + "\n\n")

    def sendCMDreceive(self, function, data, plformat):
        format = structs.Message.struct
        checksumformat= structs.Message.checksumFormat
        if data==[]:
            payload=data
            data_length=0
        else:
            payload=plformat.build(data)
            payload=bytearray(bytes(payload))
            data_length=len(bytearray(bytes(payload)))
            
        
        parameters = checksumformat.build(dict(function=function, payloadSize=data_length, payload=payload))
        checksum=0
        for i in bytearray(bytes(parameters)):
            checksum = checkSum(checksum, i)
        bytes2 = format.build(dict(function=function, payloadSize=data_length, payload=payload, checksum=checksum))
        try:
            b = self.ser.write(bytes2)
            while True:
                header = self.ser.read()
                if header != b"":
                    blist = header
                    if header == b'$':
                        while header != b"":
                            header = self.ser.read()
                            blist = blist + header
                        break
            format = structs.Message.structRecv
            if  ((function==106 and len(blist)!=27) or (function==108 and len(blist)!=15) or (function==109 and len(blist)!=19) or (function==106 and len(blist)!=27)):
                return None
            if function==209:
                #print("lala ",blist)
                return blist
            #print(blist)
            #print(len(blist),function)
            parsed_data = dict(format.parse(blist))
            blist = parsed_data["payload"]
            payload1=construct.Array(parsed_data["payloadSize"], Int8ub).build(blist)

            parsed_data = dict(plformat.parse(payload1))
            #print("end")
            #print(parsed_data)
            return parsed_data

        except Exception as error:
            print("\n\nError in sendCMDreceive.")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(error,exc_type, fname, exc_tb.tb_lineno)
            sys.exc_clear()
            return None

def getCheckSum(bytes):
    for i in bytes:
        checksum = checkSum(checksum, i)
    return checksum


def checkSum(crc, a):
    crc ^= a
    for i in range(0, 8):

        if crc & 0x80:
            crc = ((crc & 127) << 1) ^ 0xD5
        else:
            crc = (crc & 127) << 1
    return crc


