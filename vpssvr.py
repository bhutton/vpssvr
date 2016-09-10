from subprocess import Popen
import SocketServer
import mysql.connector
import subprocess
import os
import shutil
import multiprocessing
import ConfigParser

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
Config = ConfigParser.ConfigParser()
Config.read("{}/configuration.cfg".format(dir_path))

ShellInABoxPref     = Config.get('Global','ShellInABoxPref')
RootPath            = Config.get('Global','RootPath')
ShellInABox         = Config.get('Global','ShellInABox')
#SrcImg              = Config.get('Global','SrcImg')
SrcImgFreeBSD       = Config.get('Global','SrcImgFreeBSD')
SrcImgCentos        = Config.get('Global','SrcImgCentos')
SrcImgDebian        = Config.get('Global','SrcImgDebian')
SrcImgUbuntu        = Config.get('Global','SrcImgUbuntu')
Bhyvectl            = Config.get('Global','Bhyvectl')
HOST                = str(Config.get('Global','HOST'))
PORT                = int(Config.get('Global','PORT'))

mysql_user          = Config.get('Database','mysql_user')
mysql_password      = Config.get('Database','mysql_password')
mysql_host          = Config.get('Database','mysql_host')
mysql_database      = Config.get('Database','mysql_database')
raise_on_warnings   = str(Config.get('Database','raise_on_warnings'))

if (raise_on_warnings == "True"): raise_on_warnings = True
else: raise_on_warnings = False

config = {
        'user': mysql_user,
        'password': mysql_password,
        'host': mysql_host,
        'database': mysql_database,
        'raise_on_warnings': raise_on_warnings,
    }

class MyTCPHandler(SocketServer.BaseRequestHandler):

    class VMFunc:
        def execbhyve(self,command,ID):
            self.command = command
            self.id = ID

            pid = os.fork() 

            if (pid == 0):
            
                self.id = RootPath + self.id
                args = ("-c",self.command,self.id)

                self.env = {"PATH":self.id}
                print (self.env)

                proc = Popen(['/bin/sh', '-c', self.command, '999'],
                     cwd=self.id,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.STDOUT,
                     close_fds=True)

                print (self.command)
                os._exit(0)
                

    def start(self,id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        Get_Dev     = ("select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id")
        Get_VPS     = ("select id,name,ram,console from vps where vps.id=%s")
        Get_Disks   = ("select id,size from disk where vps_id=%s")

        cursor.execute(Get_VPS,(id,))
        VPS = cursor.fetchone()

        cursor.execute(Get_Disks,(id,))
        Disks = cursor.fetchall()

        cursor.execute(Get_Dev,(id,))
        Devices = cursor.fetchall()

        print ("ID: {}" .format(VPS[0]))
        print ("Name: {}".format(VPS[1]))
        print ("RAM: {}".format(VPS[2]))
        print ("Console: {}".format(VPS[3]))
        
        Count = 0
        for Disk in Disks:
            if (Count == 0):
                BootDrive = Disk[0]

            print ("Disk {}:{}".format(Disk[0],Disk[1]))

            Count += 1
            
        for Device in Devices:
            print ("Network {}:{}".format(Device[0],Device[1]))

        

        command = "/bin/sh " + RootPath + "/" + str(VPS[0]) + "/start.sh"
        
        args = ("test","abc")
        
        vm = MyTCPHandler.VMFunc()
        vm.execbhyve(command,str(VPS[0]))


    def stop(self,id):

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        Get_VPS     = ("select name from vps where id=%s")
        
        cursor.execute(Get_VPS,(id,))
        name = cursor.fetchone()

        command = "sh " + RootPath + "/" + str(id) + "/stop.sh"
        stopconsole = "sh " + RootPath + "/" + str(id) + "/stopconsole.sh"

        ps = "sh /usr/bin/sockstat -4 -l | grep :20379"

        output1 = subprocess.Popen(['/bin/sh', '-c', command], stdout=subprocess.PIPE)
        output2 = subprocess.Popen(['/bin/sh', '-c', stopconsole], stdout=subprocess.PIPE)

        out, err = output2.communicate()

        print (command)
        print (out)

        pid = out.split()

        if (len(pid) > 0): 
            term = "kill -TERM " + str(pid[2])
            print (term)
            output3 = subprocess.Popen(['/bin/sh', '-c', term], stdout=subprocess.PIPE)

    def generateScript(self,file,data):
        #print "writing file {}".format(file)
        #print "writing data {}".format(data)
        try:
            f = open(file, 'w')
            f.write("#!/bin/sh\n")
            f.write(data)
            f.close()
        except:
            print "Error with ".format(file)
            

    def getDevices(self,id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        Get_Dev     = ("select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id")

        cursor.execute(Get_Dev,(id,))
        
        return cursor.fetchall()

    def getDisks(self,id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        Get_Disks   = ("select id,size from disk where vps_id=%s")
        cursor.execute(Get_Disks,(id,))
        return cursor.fetchall()

    def getVPS(self,id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        cursor.execute("select id,name,ram,console,image from vps where vps.id=%s",(id,))
        VPS = cursor.fetchone()

        ID = VPS[0]
        Name = VPS[1]
        RAM = VPS[2]
        Console = VPS[3]
        Image = VPS[4]

        return(ID, Name, RAM, Console, Image)

    def genDevices(self,Devices,Interface):

        Count = 0
        Drives = ''
        NetInt = ''
        Interface = 2

        AddTaps = ''
        DelTaps = ''
        AddBridges = ''

        self.interface = Interface

        for Device in Devices:
            NetInt      = "{} -s {}:0,virtio-net,tap{}".format(NetInt,self.interface,Device[1])
            AddTaps     = "{}/sbin/ifconfig tap{} create\n".format(AddTaps,Device[1])
            DelTaps     = "{}/sbin/ifconfig tap{} destroy\n".format(DelTaps,Device[1])
            AddBridges  = "{}/sbin/ifconfig bridge{} addm tap{}\n".format(AddBridges,Device[3],Device[1])
            
            self.interface += 1
            Count += 1


        return (NetInt, AddTaps, DelTaps, AddBridges, self.interface)

    def genDisks(self,Disks,Interface,ID):

        Count = 0
        self.interface = Interface

        Drives = ''
        BootDrive = ''

        for Disk in Disks:
            if (Count == 0):
                BootDrive = "{}/{}/{}".format(RootPath,ID,Disk[0])
                LinuxBoot = "{}".format(Disk[0])
            
            Drives = "{} -s {}:0,virtio-blk,{}/{}/{}".format(Drives,self.interface,RootPath,ID,Disk[0])
            Count += 1
            self.interface += 1

        return (BootDrive,Drives,self.interface,LinuxBoot)

    def genBhyveCommands(self,RAM,BootDrive,Name,NetInt,Drives,Console,ID):
        BhyveLoad       = "/usr/sbin/bhyveload -m {} -d {} {}\n".format(RAM,BootDrive,ID)
        Bhyve           = "/usr/sbin/bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc {} {} -l com1,/dev/nmdm{}A -c 4 -m {} {} &\n".format(NetInt,Drives,Console,RAM,ID)
        ShellInABox     = "/usr/local/bin/shellinaboxd -t --service='/shell':'root':'wheel':'/root':'/usr/bin/cu -l /dev/nmdm{}B' --port={}{}".format(Console,ShellInABoxPref,ID)
        GrubBhyve       =  "grub-bhyve -m device.map -r hd0,msdos1 -M {} {}".format(RAM,ID)

        return (BhyveLoad,GrubBhyve,Bhyve,ShellInABox)

    
    def createvps(self,id):
        print ("Create: {}".format(id))
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        ID, Name, RAM, Console, Image = self.getVPS(id)

        Disks = self.getDisks(id)

        Devices = self.getDevices(id)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)

        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID)

        BhyveLoad,GrubBhyve,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID)
        
        StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(ShellInABoxPref,ID)
        Network         = "/sbin/ifconfig "
        
        Path = RootPath + "/" + str(ID)
        
        DstImg = Path + "/" + "disk.img"

        if (Image == 1): SrcImg = SrcImgFreeBSD
        elif (Image == 2): SrcImg = SrcImgUbuntu
        
        if not os.path.exists(Path):
            print ("Src: {}".format(SrcImg))
            print ("Dst: {}".format(DstImg))
            os.makedirs(Path)
            shutil.copyfile(SrcImg,BootDrive)
            
        StartScript = "{}{}/start.sh".format(RootPath,ID)
        StopScript = "{}{}/stop.sh".format(RootPath,ID)
        StartConsole = "{}{}/startconsole.sh".format(RootPath,ID)
        StopConsole = "{}{}/stopconsole.sh".format(RootPath,ID)
        DeviceMapScript = "{}{}/device.map".format(RootPath,ID)

        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

        elif (Image == 2):
            DevicemapData = "(hd0) ./{}\n(cd0) .\n".format(LinuxBoot)

            self.generateScript(DeviceMapScript,DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)



        StopScriptData = "{} --destroy --vm={}\n".format(Bhyvectl,ID)
        StartConsoleScript = ShellInABox
        StopConsoleScript = StopShellInABox

        self.generateScript(StartScript,StartScriptData)
        self.generateScript(StopScript,StopScriptData)
        self.generateScript(StartConsole,StartConsoleScript)
        self.generateScript(StopConsole,StopConsoleScript)
        

    def createDisk(self,id):

        print "Create Disk"
        
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("select size,vps_id from disk where id=%s",(id,))
        Disk = cursor.fetchone()

        vps_id = Disk[1]
        size = Disk[0]
        Interface = 2

        ID, Name, RAM, Console, Image = self.getVPS(vps_id)
        Disks = self.getDisks(vps_id)

        if (Image == 1): SrcImg = SrcImgFreeBSD
        elif (Image == 2): SrcImg = SrcImgUbuntu
       

        Devices = self.getDevices(vps_id)

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID)

        create_disk = "truncate -s {}GB {}/{}/{}".format(size,RootPath,vps_id,id)
        output = subprocess.Popen(['/bin/sh', '-c', create_disk], stdout=subprocess.PIPE)

        BhyveLoad,GrubBhyve,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID)

        StartScript = "{}{}/start.sh".format(RootPath,vps_id)

        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

        elif (Image == 2):
            #DevicemapData = "(hd0) ./{}\n(cd0) .\n".format(LinuxBoot)

            #self.generateScript(DeviceMapScript,DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)



        #StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)
        self.generateScript(StartScript,StartScriptData)


    def deleteDisk(self,id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("select vps_id from disk where id=%s",(id,))
        VPS = cursor.fetchone()

        vps_id = VPS[0]

        delete_disk = "rm {}/{}/{}".format(RootPath,vps_id,id)

        output = subprocess.Popen(['/bin/sh', '-c', delete_disk], stdout=subprocess.PIPE)

        cursor.execute("delete from disk where id=%s",(id,))
        cnx.commit()

        ID, Name, RAM, Console,Image = self.getVPS(vps_id)
        Disks = self.getDisks(vps_id)

        if (Image == 1): SrcImg = SrcImgFreeBSD
        elif (Image == 2): SrcImg = SrcImgUbuntu
       

        Devices = self.getDevices(vps_id)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID)

        BhyveLoad,GrubBhyve,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID)

        StartScript = "{}{}/start.sh".format(RootPath,vps_id)


        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

        elif (Image == 2):
            #DevicemapData = "(hd0) ./{}\n(cd0) .\n".format(LinuxBoot)

            #self.generateScript(DeviceMapScript,DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)


        StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)
        self.generateScript(StartScript,StartScriptData)

    def updateVPS(self,vps_id):
        ID, Name, RAM, Console, Image = self.getVPS(vps_id)
        Disks = self.getDisks(vps_id)

        if (Image == 1): SrcImg = SrcImgFreeBSD
        elif (Image == 2): SrcImg = SrcImgUbuntu
       

        Devices = self.getDevices(vps_id)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID)

        BhyveLoad,GrubBhyve,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID)

        StartScript = "{}{}/start.sh".format(RootPath,vps_id)

        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

        elif (Image == 2):
            #DevicemapData = "(hd0) ./{}\n(cd0) .\n".format(LinuxBoot)

            #self.generateScript(DeviceMapScript,DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)

        StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

        #print StartScript
        #print StartScriptData

        self.generateScript(StartScript,StartScriptData)

    def checkStatus(self,vps_id):
        self.id = vps_id

        """cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        Get_VPS     = ("select name from vps where vps.id=%s")
        
        cursor.execute(Get_VPS,(self.id,))
        VPS = cursor.fetchone()
        Name = VPS[0]"""
        
        command = "/bin/ls /dev/vmm/" + str(vps_id)

        output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

        if (len(output) > 0):
            return "Running"
        else:
            return "Stopped"


    def restartConsole(self,id):
        stopconsole = "sh " + RootPath + "/" + str(id) + "/stopconsole.sh"
        startconsole = "sh " + RootPath + "/" + str(id) + "/startconsole.sh"

        output = subprocess.Popen(['/bin/sh', '-c', stopconsole], stdout=subprocess.PIPE)

        out, err = output.communicate()

        pid = out.split()

        if (len(pid) > 0):
            term = "kill -TERM " + str(pid[2])
            print (term)
            output2 = subprocess.Popen(['/bin/sh', '-c', term], stdout=subprocess.PIPE)

        output3 = subprocess.Popen(['/bin/sh', '-c', startconsole], stdout=subprocess.PIPE)

    def delete(self,id):
        PathOrig = RootPath + str(id)
        PathDest = RootPath + "deleted/" + str(id)
        
        if os.path.exists(PathOrig):
            os.renames(PathOrig,PathDest)
            print ("Move From: {}" .format(PathOrig))
            print ("To: {}" .format(PathDest))
        

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print ("{} wrote:".format(self.client_address[0]))

        print "Data = ".format(self.data)

        Data = self.data.split(',')
        id = int(Data[0])
        Command = Data[1]

        status = ''

        if (Command == "start"):        
            self.start(id)
        elif (Command == "createvps"):
            self.createvps(id)
        elif (Command == "createdisk"):
            self.createDisk(id)
        elif (Command == "deletedisk"):
            self.deleteDisk(id)
        elif (Command == "delete"):
            self.delete(id)
        elif (Command == "stop"):
            self.stop(id)
        elif (Command == "restartConsole"):
            self.restartConsole(id)
        elif (Command == "status"):
            status = self.checkStatus(id)
        elif (Command == "updatevps"):
            self.updateVPS(id)

                
        # just send back the same data, but upper-cased
        if (len(status) > 0):
            self.request.sendall(status)
        else:
            self.request.sendall(self.data.upper())

if __name__ == "__main__":
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
