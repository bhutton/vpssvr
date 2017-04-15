from subprocess import Popen
from subprocess import check_output
import mysql.connector
import os, subprocess
import shutil
import ConfigParser
import subprocess
import modules.database as database
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
Config = ConfigParser.ConfigParser()
Config.read("{}/../configuration.cfg".format(dir_path))

ShellInABoxPref = Config.get('Global', 'ShellInABoxPref')
RootPath = Config.get('Global', 'RootPath')
BasePath = Config.get('Global', 'BasePath')
ShellInABox = Config.get('Global', 'ShellInABox')
SrcImgFreeBSD = Config.get('Global', 'SrcImgFreeBSD')
SrcImgCentos = Config.get('Global', 'SrcImgCentos')
SrcImgDebian = Config.get('Global', 'SrcImgDebian')
SrcImgUbuntu = Config.get('Global', 'SrcImgUbuntu')
SrcImgWin10 = Config.get('Global', 'SrcImgWin10')
Bhyvectl = Config.get('Global', 'Bhyvectl')
PIDFile = Config.get('Global', 'PIDFile')
LogFile = Config.get('Global', 'LogFile')
HOST = str(Config.get('Global', 'HOST'))
PORT = int(Config.get('Global', 'PORT'))
PassString = Config.get('Global', 'PassString')
ZFSEnable = int(Config.get('Global', 'ZFSEnable'))
ZFSRoot = Config.get('Global', 'ZFSRoot')
ZFSCmd = Config.get('Global', 'ZFSCmd')
IFConfig = Config.get('Global', 'IFConfig')
Touch = Config.get('Global', 'Touch')
CP = Config.get('Global', 'CP')
RM = Config.get('Global', 'RM')

database_user = Config.get('Database', 'database_user')
database_password = Config.get('Database', 'database_password')
database_host = Config.get('Database', 'database_host')
database_database = Config.get('Database', 'database_name')
raise_on_warnings = str(Config.get('Database', 'raise_on_warnings'))

if (raise_on_warnings == "True"):
    raise_on_warnings = True
else:
    raise_on_warnings = False

config = {
    'user': database_user,
    'password': database_password,
    'host': database_host,
    'database': database_database,
    'raise_on_warnings': raise_on_warnings,
}


class VMFunc:
    def __init__(self, data):
        Data = data.split(',')
        self.Auth = Data[0]
        self.id = int(Data[1])
        Command = Data[2]

        try:
            createDisk = Data[3]
        except:
            createDisk = "no"

        try:
            Snapshot = Data[3]
        except:
            Snapshot = ""

        self.command = Command
        self.createDisk = createDisk
        self.snapShot = Snapshot

        self.log = ''

        self.FreeBSD = 1
        self.Ubuntu = 2
        self.Centos = 3
        self.Win10 = 4

    def checkSecurity(self):

        if (PassString == self.Auth):
            return "Pass"
        else:
            return "Fail"

    def executeCommand(self):

        if (self.checkSecurity() == "Pass"):

            if (self.getCommand() == "start"):
                self.status = self.start(self.getID())
            elif (self.getCommand() == "stop"):
                self.status = self.stop(self.getID())
            elif (self.getCommand() == "createvps"):
                self.status = self.createvps(self.getID())
            elif (self.getCommand() == "createdisk"):
                self.status = self.createDiskImg(self.getID())
            elif (self.getCommand() == "deletedisk"):
                self.status = self.deleteDisk(self.getID())
            elif (self.getCommand() == "delete"):
                self.status = self.delete(self.getID())
            elif (self.getCommand() == "restartConsole"):
                self.status = self.restartConsole(self.getID())
            elif (self.getCommand() == "status"):
                self.status = self.checkStatus(self.getID())
            elif (self.getCommand() == "updatevps"):
                self.status = self.updateVPS(self.getID())
            elif (self.getCommand() == "takeSnapshot"):
                self.status = self.takeSnapshot(self.getID(), self.snapShot)
            elif (self.getCommand() == "listSnapshot"):
                self.status = self.listSnapshot(self.getID())
            elif (self.getCommand() == "restoreSnapshot"):
                self.status = self.restoreSnapshot(self.getID(), self.snapShot)
            elif (self.getCommand() == "removeSnapshot"):
                self.status = self.removeSnapshot(self.getID(), self.snapShot)
            elif (self.getCommand() == "netStatus"):
                self.status = self.getNetStatus(self.getID())
            elif (self.getCommand() == "netStop"):
                self.status = self.stopNetwork(self.getID())
            elif (self.getCommand() == "netStart"):
                self.status = self.startNetwork(self.getID())

        else:
            self.status = "Connection Failed"

        return self.status

    def getStatus(self):
        return (self.status)

    def getNetStatus(self, id):
        vps = database.DatabaseVPS()
        devices = vps.get_devices(id)

        output = self.execcmd(IFConfig + ' tap' + format(id) + ' | grep UP')

        if (output == ""):
            output = "DOWN"
        else:
            output = "UP"

        return output

    def stopNetwork(self, id):
        output, error = self.execcmd(IFConfig + ' tap' + format(id) + ' down')

        return output

    def startNetwork(self, id):
        output, error = self.execcmd(IFConfig + ' tap' + format(id) + ' up')

        return output

    def getCommand(self):
        return self.command

    def getID(self):
        return self.id

    def logentry(self, data):

        try:
            f = open(LogFile, 'a')
            f.write(data)
            f.close()
        except:
            return "Error with ".format(LogFile)

    def execbhyve(self, command, ID):

        print "ID = {}".format(ID)
        self.command = command
        self.id = ID

        pid = os.fork()

        if (pid == 0):
            self.id = RootPath + self.id
            args = ("-c", self.command, self.id)

            proc = Popen(['/bin/sh', '-c', self.command, '999'],
                         cwd=self.id,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)

            os._exit(0)

    def execcmd(self, cmd):
        proc = subprocess.Popen(['/bin/sh', '-c', cmd],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)

        output, error = proc.communicate()

        return (output, error)

    def execcmdFork(self, cmd):
        pid = os.fork()

        if (pid == 0):
            proc = subprocess.Popen(['/bin/sh', '-c', cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            os._exit(0)

            output, error = proc.communicate()

    def takeSnapshot(self, id, snapshot):

        try:

            if (snapshot == ""): snapshot = str(time.time())

            self.command = ZFSCmd + ' snapshot ' + ZFSRoot + '/' + str(id) + '@' + str(snapshot)

            self.id = RootPath + str(id)

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            # output,error = proc.communicate()

            return "Snapshot name = {}".format(snapshot)
        except:
            return "An error occurred"

    def listSnapshot(self, id):

        try:
            self.command = ZFSCmd + ' list -rt snapshot ' + ZFSRoot + '/' + str(id)
            self.id = RootPath + str(id)

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            output, error = proc.communicate()
            return output
        except:
            return "An error occured"

    def restoreSnapshot(self, id, snapshot):

        try:
            self.command = ZFSCmd + ' rollback ' + snapshot

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            output, error = proc.communicate()
            return output

        except:
            return error

    def removeSnapshot(self, id, snapshot):

        self.command = ZFSCmd + ' destroy ' + snapshot

        proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)

        return "Snapshot Removed"

    def restartConsole(self, id):
        stopconsole = "sh " + RootPath + "/" + str(id) + "/stopconsole.sh"
        startconsole = "sh " + RootPath + "/" + str(id) + "/startconsole.sh"

        output = subprocess.Popen(['/bin/sh', '-c', stopconsole], stdout=subprocess.PIPE)

        out, err = output.communicate()

        pid = out.split()

        if (len(pid) > 1):
            term = "kill -TERM " + str(pid[2])
            output2 = subprocess.Popen(['/bin/sh', '-c', term], stdout=subprocess.PIPE)

        output3 = subprocess.Popen(['/bin/sh', '-c', startconsole], stdout=subprocess.PIPE)

        return "Terminal Restarted\n"

    def checkStatus(self, vps_id):
        self.id = vps_id

        VPS_Conn = database.DatabaseVPS()
        VPS = VPS_Conn.get_vps_details(self.id)

        vps_id = str(VPS[0])
        vps_startscript = VPS[5]

        if (vps_startscript == ""): vps_name = str(self.id)

        if (os.path.exists(RootPath + str(vps_id) + "/installing.txt")):
            return "Installing"

        if (os.path.exists("/dev/vmm/" + str(vps_id))):
            return "Running"
        else:
            return "Stopped"

    def start(self, id):
        VPS_DB = database.DatabaseVPS()
        VPS_DB.get_vps_details(id)
        self.execbhyve(VPS_DB.startCommand(RootPath), str(id))
        return "Started VPS {}\n".format(id)

    def stop(self, id):
        VPS_DB = database.DatabaseVPS()
        self.execbhyve(VPS_DB.stopCommand(RootPath), str(id))
        self.execbhyve(VPS_DB.stopConsole(RootPath), str(id))
        return "Stopped VPS {}\n".format(id)

    def delete(self, id):
        PathOrig = RootPath + str(id)
        PathDest = RootPath + "deleted/" + str(id)

        if (ZFSEnable == 1):
            cmd = ZFSCmd + " destroy " + ZFSRoot + "/" + str(id)
            output, error = self.execcmd(cmd)
            return error
        else:
            if os.path.exists(PathOrig):
                return os.renames(PathOrig, PathDest)
            else:
                return "Disk doesn't exist"

    def generateScript(self, file, data):

        self.file = file
        self.data = data

        try:
            f = open(self.file, 'w')
            f.write("#!/bin/sh\n")
            f.write(self.data)
            f.close()
        except:
            return "Error occurred generating script".format(self.file)

    def genBhyveCommands(self, RAM, BootDrive, Name, NetInt, Drives, Console, ID, Path):
        BhyveLoad = "/usr/sbin/bhyveload -m {} -d {} {}\n".format(RAM, BootDrive, ID)
        Bhyve = "/usr/sbin/bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc {} {} -l com1,/dev/nmdm{}A -c 4 -m {} {} &\n".format(
            NetInt, Drives, Console, RAM, ID)
        ShellInABox = "/usr/local/bin/shellinaboxd -t --service='/shell':'root':'wheel':'/root':'/usr/bin/cu -l /dev/nmdm{}B' --port={}{}".format(
            Console, ShellInABoxPref, ID)
        GrubBhyve = "/usr/local/sbin/grub-bhyve -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path, RAM, ID)
        GrubBhyve2 = "/usr/local/sbin/grub-bhyve -d /grub2 -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path, RAM,ID)

        return (BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox)

    def genDevices(self, Devices, Interface):
        Count = 0
        NetInt = ''
        Interface = 2
        AddTaps = ''
        DelTaps = ''
        AddBridges = ''

        self.interface = Interface

        for Device in Devices:
            NetInt = "{} -s {}:0,virtio-net,tap{}".format(NetInt, self.interface, Device[1])
            AddTaps = "{}/sbin/ifconfig tap{} create\n".format(AddTaps, Device[1])
            DelTaps = "{}/sbin/ifconfig tap{} destroy\n".format(DelTaps, Device[1])
            AddBridges = "{}/sbin/ifconfig bridge{} addm tap{}\n".format(AddBridges, Device[3], Device[1])

            self.interface += 1
            Count += 1

        return (NetInt, AddTaps, DelTaps, AddBridges, self.interface)

    def genDisks(self, Disks, Interface, ID, Path):
        Count = 0
        self.interface = Interface

        Drives = ''
        BootDrive = ''
        LinuxBoot = ''

        if (Path == ""):
            Path = RootPath + "/" + str(ID)

        for Disk in Disks:

            if (Disk[2] == ""):
                DiskDrive = Disk[0]
            else:
                DiskDrive = Disk[2]

            if (Count == 0):
                BootDrive = "{}/{}".format(Path, DiskDrive)
                LinuxBoot = "{}".format(DiskDrive)

            Drives = "{} -s {}:0,virtio-blk,{}/{}".format(Drives, self.interface, Path, DiskDrive)
            Count += 1
            self.interface += 1

        return (BootDrive, Drives, self.interface, LinuxBoot)

    def createvps(self, id):

        vps = database.DatabaseVPS()
        vps.get_vps_details(id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.getConsole()
        Image = vps.getImage()
        Path = vps.getPath()
        Disks = vps.get_disks_details_from_database(id)
        Devices = vps.get_devices(id)

        if (Path == ""):
            Path = RootPath + "/" + str(ID)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks, Interface, ID, Path)
        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.genBhyveCommands(RAM, BootDrive, Name, NetInt,
                                                                                     Drives, Console, ID, Path)

        StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(ShellInABoxPref, ID)
        Network = "/sbin/ifconfig "

        DstImg = Path + "/" + "disk.img"

        SrcImg = self.setImagePath(Image)

        if not os.path.exists(Path):
            if (ZFSEnable == 1):
                cmd = ZFSCmd + " create " + ZFSRoot + "/" + str(ID)
                self.execcmd(cmd)
            else:
                os.makedirs(Path)

        if (self.createDisk == "on"):
            cmd = Touch + " " + RootPath + str(
                ID) + "/installing.txt" + " && " + CP + " " + SrcImg + " " + BootDrive + " && " + RM + " " + RootPath + str(
                ID) + "/installing.txt"

            self.execcmdFork(cmd)

            StartScript = "{}/start.sh".format(Path)
            StopScript = "{}/stop.sh".format(Path)
            StartConsole = "{}/startconsole.sh".format(Path)
            StopConsole = "{}/stopconsole.sh".format(Path)
            DeviceMapScript = "{}/device.map".format(Path)

            if (Image == self.FreeBSD):
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)
            elif (Image == self.Ubuntu):
                DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path, LinuxBoot)
                self.generateScript(DeviceMapScript, DevicemapData)
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

            elif (Image == self.Centos):
                DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path, LinuxBoot)
                self.generateScript(DeviceMapScript, DevicemapData)
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)


            StopScriptData = "{} --destroy --vm={}\n".format(Bhyvectl, ID)
            StartConsoleScript = ShellInABox
            StopConsoleScript = StopShellInABox

            self.generateScript(StartScript, StartScriptData)
            self.generateScript(StopScript, StopScriptData)
            self.generateScript(StartConsole, StartConsoleScript)
            self.generateScript(StopConsole, StopConsoleScript)

        return "Created VPS: {}\n".format(id)

    def setImagePath(self, Image):
        if (Image == self.FreeBSD):
            SrcImg = SrcImgFreeBSD
        elif (Image == self.Ubuntu):
            SrcImg = SrcImgUbuntu
        elif (Image == self.Centos):
            SrcImg = SrcImgCentos
        elif (Image == self.Win10):
            SrcImg = SrcImgWin10

        return SrcImg

    def updateVPS(self, vps_id):

        vps = database.DatabaseVPS()
        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.getConsole()
        Image = vps.getImage()
        Path = vps.getPath()
        StartScript = vps.getStartScript()
        StopScript = vps.getStopScript()

        Disks = vps.get_disks_details_from_database(vps_id)

        if (Path == ""):
            VPSPath = RootPath + str(vps_id)
        else:
            VPSPath = Path

        # print "VPS Path: {}".format(VPSPath)

        Devices = vps.get_devices(vps_id)
        StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(ShellInABoxPref, ID)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks, Interface, ID, VPSPath)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.genBhyveCommands(RAM, BootDrive, Name, NetInt,
                                                                                     Drives, Console, ID, VPSPath)

        StartScript = "{}/start.sh".format(VPSPath)
        StopScript = "{}/stop.sh".format(VPSPath)
        DeviceMapScript = "{}/device.map".format(VPSPath)
        StartConsole = "{}/startconsole.sh".format(VPSPath)
        StopConsole = "{}/stopconsole.sh".format(VPSPath)

        StopScriptData = "{} --destroy --vm={}\n".format(Bhyvectl, ID)

        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        # Ubuntu
        elif (Image == 2):
            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath, LinuxBoot)

            self.generateScript(DeviceMapScript, DevicemapData)
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

            # print "Linux Device - Image 2 = {}".format(DevicemapData)

        # Centos
        elif (Image == 3):

            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath, LinuxBoot)

            self.generateScript(DeviceMapScript, DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

            # print "Linux Device - Image 3 = {}".format(StartScriptData)
        else:
            return "Error: no image specified"

        StartConsoleScript = ShellInABox
        StopConsoleScript = StopShellInABox

        self.generateScript(StartConsole, StartConsoleScript)
        self.generateScript(StopConsole, StopConsoleScript)

        self.generateScript(StartScript, StartScriptData)
        self.generateScript(StopScript, StopScriptData)

        return "VPS {} Update\n".format(vps_id)

    def createDiskImg(self, id):

        vps = database.DatabaseVPS()
        # return vps.getImage()

        '''cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("select size,vps_id from disk where id=%s",(id,))
        Disk = cursor.fetchone()'''

        Disk = vps.get_disk(id)

        vps_id = Disk[1]
        size = Disk[0]
        Interface = 2

        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.getConsole()
        Image = vps.getImage()
        Path = vps.getPath()
        StartScript = vps.getStartScript()
        StopScript = vps.getStopScript()

        # return "Create Disk for VPS 1\n"

        Disks = vps.get_disks_details_from_database(vps_id)

        if (Path == ""):
            VPSPath = RootPath + "/" + str(vps_id)
        else:
            VPSPath = Path

        SrcImg = self.setImagePath(Image)

        Devices = vps.get_devices(vps_id)

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks, Interface, ID, Path)

        create_disk = "truncate -s {}GB {}/{}/{}".format(size, RootPath, vps_id, id)
        output = subprocess.Popen(['/bin/sh', '-c', create_disk], stdout=subprocess.PIPE)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.genBhyveCommands(RAM, BootDrive, Name, NetInt,
                                                                                     Drives, Console, ID, VPSPath)

        StartScript = "{}{}/start.sh".format(RootPath, vps_id)

        # FreeBSD
        if (Image == self.FreeBSD):
            # return "Create Disk for VPS 1\n"
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.Ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.Centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

        self.generateScript(StartScript, StartScriptData)

        return "Create Disk for VPS {}\n".format(vps_id)

    def deleteDisk(self, id):

        vps = database.DatabaseVPS()

        vps_id = vps.get_vps_id_associated_with_disk(id)

        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.getConsole()
        Image = vps.getImage()
        Path = vps.getPath()
        StartScript = vps.getStartScript()
        StopScript = vps.getStopScript()

        if (Path == ""):
            VPSPath = RootPath + "/" + str(vps_id)
        else:
            VPSPath = Path

        if (Image == 1):
            SrcImg = SrcImgFreeBSD
        elif (Image == 2):
            SrcImg = SrcImgUbuntu
        elif (Image == 3):
            SrcImg = SrcImgCentos
        else:
            return "Error: no image found"

        delete_disk = "rm {}/{}".format(VPSPath, id)

        try:
            process = subprocess.Popen(['/bin/sh', '-c', delete_disk], stdout=subprocess.PIPE)
            output, err = process.communicate()
        except:
            # return process.returncode
            return "Delete disk failed"

        vps.delete_disk_from_database(id)

        ####
        #
        # Regenerate Scripts
        #
        ####

        Disks = vps.get_disks_details_from_database(vps_id)
        Devices = vps.get_devices(vps_id)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks, Interface, ID, VPSPath)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.genBhyveCommands(RAM, BootDrive, Name, NetInt,
                                                                                     Drives, Console, ID, VPSPath)

        StartScript = "{}/start.sh".format(VPSPath)

        # FreeBSD
        if (Image == self.FreeBSD):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.Ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.Centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

        StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        if (self.generateScript(StartScript, StartScriptData)):
            return "An error occurred generating script"

        return "Disk {} Delete\n".format(id)
