import os
import threading
import socket
import subprocess

import simplejson as json

class WkWorker:
    host = 'localhost'
    port = 8081

    def __init__(self):
        custom_port = os.environ.get('WKHTMLTOPDF_WORKER_PORT')
        if custom_port:
            self.port = custom_port

        self.lock = threading.Lock()

    def handler(self, clientsock, addr):
        while 1:
            data = clientsock.recv(1024)
            if not data:
                break

            msg = 'ok'
            args = json.loads(data)
            try:
                p = subprocess.Popen(args)
                p.wait()
            except:
                msg = 'ko'

            clientsock.send(msg)

        print 'Connection over'

    def start_server(self):
        serversock = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)
        serversock.bind((self.host, self.port,))
        serversock.listen(2)

        while 1:
            print 'waiting for connection...'
            clientsock, addr = serversock.accept()
            print 'connected from:', addr
            th = threading.Thread(
                target = self.handler,
                args = (clientsock, addr))
            th.start()

        serversock.close()

def start_worker():
    server = WkWorker()
    server.start_server()
