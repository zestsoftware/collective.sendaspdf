import os
from  threading import Thread, Timer
from Queue import Queue
import socket
import subprocess
import daemon
    
import logging
logger = logging.getLogger('collective.sendaspdf.wk_worker')

import simplejson as json

class WkWorkerThread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run_command(self, args, timeout = 30):
        """ Based on 
        http://stackoverflow.com/questions/1191374/subprocess-with-timeout
        """
        proc = subprocess.Popen(args)
        timer = Timer(timeout,
                      lambda p: p.kill(),
                      [proc])
        timer.start()
        stdo, stderr = proc.communicate()
        timer.cancel()
    
    def run(self):
        while 1:
            clientsock = self.queue.get()
            
            data = clientsock.recv(1024)
            if not data:
                break

            args = json.loads(data)
            print '----------------------------'
            print ' -> '.join([x for x in args if 'tmp' in x])
            self.run_command(args)
            clientsock.send('ok')

class WkWorker:
    host = 'localhost'
    port = 8081

    def __init__(self):
        custom_port = os.environ.get('WKHTMLTOPDF_WORKER_PORT')
        print 'Custom port: %s' % custom_port
        if custom_port:
            self.port = custom_port

        self.queue = Queue()

    def start_server(self):
        serversock = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM)
        serversock.bind((self.host, self.port,))
        serversock.listen(2)

        # We only use one thread to read the queue, this way
        # we ensure that only one process of wkhtmltopdf is ran.
        th = WkWorkerThread(
            self.queue,
        th.setDaemon(True)
        th.start()

        while 1:
            clientsock, addr = serversock.accept()
            self.queue.put(clientsock)

        serversock.close()

def start_worker():
    server = WkWorker()
    server.start_server()
