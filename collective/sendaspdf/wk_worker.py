import os
import threading
import socket
import subprocess

import simplejson as json

class WkWorkerThread(threading.Thread):
    def __init__(self, lock, clientsock):
        threading.Thread.__init__(self)
        self.lock = lock
        self.clientsock = clientsock
    
    def run(self):
        while 1:
            data = self.clientsock.recv(1024)
            if not data:
                break

            msg = 'ok'
            args = json.loads(data)

            print 'Waiting for the lock'
            self.lock.acquire()
            try:
                p = subprocess.Popen(args)
                p.wait()
            except:
                msg = 'ko'
                
            print 'Releasing the lock'
            self.lock.release()

            self.clientsock.send(msg)

        print 'Connection over'


class WkWorker:
    host = 'localhost'
    port = 8081

    def __init__(self):
        custom_port = os.environ.get('WKHTMLTOPDF_WORKER_PORT')
        if custom_port:
            self.port = custom_port

        self.lock = threading.Lock()

    def start_server(self):
        serversock = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)
        serversock.bind((self.host, self.port,))
        serversock.listen(2)

        while 1:
            print 'waiting for connection...'
            clientsock, addr = serversock.accept()
            print 'connected from:', addr
            th = WkWorkerThread(
                self.lock,
                clientsock)
            th.start()

        serversock.close()

def start_worker():
    server = WkWorker()
    server.start_server()
