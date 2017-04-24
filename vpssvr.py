#!/usr/local/bin/python

'''
BHyve Server for VPS Manager App

'''

from subprocess import Popen
import SocketServer
import os
import ConfigParser
import modules.database
import modules.vps

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
Config = ConfigParser.ConfigParser()
Config.read("{}/configuration.cfg".format(dir_path))

PIDFile             = Config.get('Global','PIDFile')
LogFile             = Config.get('Global','LogFile')
HOST                = str(Config.get('Global','HOST'))
PORT                = int(Config.get('Global','PORT'))

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        
        # Instanciate modules.vps passing in payload from calling application
        vpsConn = modules.vps.VMFunc(self.request.recv(1024).strip())
        vpsConn.executeCommand()
        vpsConn.logentry(vpsConn.getStatus())

        self.request.sendall(vpsConn.getStatus())

if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
