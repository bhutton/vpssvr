import socket
import threading
import os
from subprocess import Popen
import SocketServer
import mysql.connector
#import MySQLdb
import subprocess
import os
import shutil
import multiprocessing


class ThreadedServer(object):
    class VMFunc:
        def execbhyve(self,command):
            self.command = command

            #proc = Popen(['/bin/sh', '-c', self.command],
            #    cwd="/vm/vpsman/294/",
            #    stdout=subprocess.PIPE, 
            #    stderr=subprocess.STDOUT)
            
            pid = os.fork() 

            if (pid == 0):

                #os.system (self.command)
                #exit()
                proc = Popen(['/bin/sh', '-c', self.command],
                    cwd="/vm/vpsman/294/",
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    close_fds=True)

            


    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    client.send(response)
                    print (response)

                    self.command = "/bin/sh /vm/vpsman/294/start.sh &"
                    #self.command = "/vm/vpsman/294/start.sh"

                    vm = ThreadedServer.VMFunc()
                    vm.execbhyve(self.command)

                    
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    #port_num = input("Port? ")
    port_num = 9999
    ThreadedServer('',port_num).listen()

    #server.serve_forever()