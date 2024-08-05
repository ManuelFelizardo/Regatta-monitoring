import logging
from MSP_Thread import *
import json
from MSP import MSP

ip = str(socket.gethostbyname(socket.gethostname()))
log = logging.getLogger('udp_server')

def udp_server(host=ip, port=8182):
    msp = MSP()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))
    f = s.makefile()
    lastOption=0
    while True:
        (data, addr) = s.recvfrom(128*1024)
        if data:
            values = data.decode("utf-8")
            d = json.loads(values)
            option= d['option']
            # Start Following
            if d['option']==1:
                t = threading.Thread(target=startFollowing, args=(msp,d['id']))
                t.start()
            # Stop Following
            if d['option']==2:
                t = threading.Thread(target=stopFollowing, args=())
                t.start()
            if d['option']==3:
                t = threading.Thread(target=go_to_buoy, args=(msp, d['id']))
                t.start()

            lastOption=d['option']

#udp_server()
