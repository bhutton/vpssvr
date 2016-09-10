#!/usr/local/bin/python

import os, sys, getopt, SocketServer

"""
def forkcmd(command,ID):
    command = command
    id = ID

    pid = os.fork() 

    if (pid == 0):
        #proc = Popen(['/bin/sh', '-c', self.command]).pid
        self.id = RootPath + self.id
        args = ("-c",self.command)

        self.env = {"PATH":self.id}
        print self.env
        os.execvpe('/bin/sh',args,self.env)
        print self.command
"""

RootPath    = "/vm/vpsman/"


def main(argv):
  # print "arg=" + sys.argv[1]


  command = sys.argv[1]
  id = sys.argv[2]
  
  os._exec(0)
  os._exec(0)
  os._exec(0)
  os._exec(0)
  pid = os.fork() 

  if (pid == 0):
      #proc = Popen(['/bin/sh', '-c', self.command]).pid
      id = RootPath + id
      args = ("-c",command,id)

      env = {"PATH":id}
      print env
      #os.flush()
      os.execvpe('/bin/sh',args,env)
      print command
      os._exec(0)


if __name__ == "__main__":
  #running = False
  #socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect( (self.hostname, self.port))
  #self.socket.close()
  main(sys.argv[1:])