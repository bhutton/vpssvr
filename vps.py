from subprocess import Popen
import mysql.connector
import os
import shutil
import ConfigParser
import subprocess
import database


dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
Config = ConfigParser.ConfigParser()
Config.read("{}/../configuration.cfg".format(dir_path))
#Config.read("/vm/vpsmanager-dev/configuration.cfg")

ShellInABoxPref     = Config.get('Global','ShellInABoxPref')
RootPath            = Config.get('Global','RootPath')
ShellInABox         = Config.get('Global','ShellInABox')
SrcImgFreeBSD       = Config.get('Global','SrcImgFreeBSD')
SrcImgCentos        = Config.get('Global','SrcImgCentos')
SrcImgDebian        = Config.get('Global','SrcImgDebian')
SrcImgUbuntu        = Config.get('Global','SrcImgUbuntu')
Bhyvectl            = Config.get('Global','Bhyvectl')
PIDFile             = Config.get('Global','PIDFile')
LogFile             = Config.get('Global','LogFile')
HOST                = str(Config.get('Global','HOST'))
PORT                = int(Config.get('Global','PORT'))
PassString 			= Config.get('Global','PassString')

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

class VMFunc:

	def __init__(self,data):

		Data 	 	= data.split(',')
		self.Auth	= Data[0]
		self.id 	= int(Data[1])
		Command 	= Data[2]
		
		try:
			createDisk = Data[2]
		except:
			createDisk = "no"

		self.command = Command
		self.createDisk = createDisk

	def checkSecurity(self):

		if (PassString == self.Auth):
			return "Pass"
		else:
			return "Fail"

	def executeCommand(self):

		if (self.checkSecurity() == "Pass"):

			if   (self.getCommand() == "start"): self.status = self.start(self.getID())
			elif (self.getCommand() == "createvps"): self.status = self.createvps(self.getID())
			elif (self.getCommand() == "createdisk"): self.status = self.createDisk(self.getID())
			elif (self.getCommand() == "deletedisk"): self.status = self.deleteDisk(self.getID())
			elif (self.getCommand() == "delete"): self.status = self.delete(self.getID())
			elif (self.getCommand() == "stop"): self.status = self.stop(self.getID())
			elif (self.getCommand() == "restartConsole"): self.status = self.restartConsole(self.getID())
			elif (self.getCommand() == "status"): self.status = self.checkStatus(self.getID())
			elif (self.getCommand() == "updatevps"): self.status = self.updateVPS(self.getID())

		else:
			#print "Security issue"
			#return "Connection Failed"
			self.status = "Connection Failed"

	def getStatus(self):
		return (self.status)

	def getCommand(self):
		return self.command

	def getID(self):
		return self.id

	def logentry(self,data):
        
		try:
			f = open(LogFile, 'a')
			f.write(data)
			f.close()
		except:
			print "Error with ".format(LogFile)

	def execbhyve(self,command,ID):
		self.command = command
		self.id = ID

		pid = os.fork() 

		if (pid == 0):

			self.id = RootPath + self.id
			args = ("-c",self.command,self.id)

			#self.env = {"PATH":self.id}

			#self.env = {"PATH":"/vm/centos"}
			#print (self.env)

			proc = Popen(['/bin/sh', '-c', self.command, '999'],
			     cwd=self.id,
			     stdout=subprocess.PIPE, 
			     stderr=subprocess.STDOUT,
			     close_fds=True)

			#print (self.command)
			os._exit(0)

	def restartConsole(self,id):
		stopconsole = "sh " + RootPath + "/" + str(id) + "/stopconsole.sh"
		startconsole = "sh " + RootPath + "/" + str(id) + "/startconsole.sh"

		output = subprocess.Popen(['/bin/sh', '-c', stopconsole], stdout=subprocess.PIPE)

		out, err = output.communicate()

		pid = out.split()

		if (len(pid) > 0):
		    term = "kill -TERM " + str(pid[2])
		    output2 = subprocess.Popen(['/bin/sh', '-c', term], stdout=subprocess.PIPE)

		output3 = subprocess.Popen(['/bin/sh', '-c', startconsole], stdout=subprocess.PIPE)

		return "Terminal Restarted\n"

	def checkStatus(self,vps_id):
		self.id = vps_id

		VPS_Conn = database.DB_VPS()
		VPS = VPS_Conn.getVPS(self.id)

		vps_id          = str(VPS[0])
		vps_name        = VPS[1]
		vps_startscript = VPS[5]
		
		if (vps_startscript == ""): vps_name = str(self.id)

		if (os.path.exists("/dev/vmm/" + str(vps_id))):
			return "Running"
		else:
			return "Stopped"

	def start(self,id):
        
		VPS_DB = database.DB_VPS()
		VPS = VPS_DB.getVPS(id)

		self.execbhyve(VPS_DB.startCommand(RootPath),str(id))

		return "Started VPS {}\n".format(id)

	def stop(self,id):

		VPS_DB = database.DB_VPS()
		VPS = VPS_DB.getVPS(id)

		#VPS_Con = modules.vps.VMFunc()
		self.execbhyve(VPS_DB.stopCommand(RootPath),str(id))
		self.execbhyve(VPS_DB.stopConsole(RootPath),str(id))

		return "Stopped VPS {}\n".format(id)

	def delete(self,id):
		PathOrig = RootPath + str(id)
		PathDest = RootPath + "deleted/" + str(id)

		if os.path.exists(PathOrig):
			os.renames(PathOrig,PathDest)
		    
		status = "Move From: {}\nTo: {}\n".format(PathOrig,PathDest)

	def generateScript(self,file,data):

		self.file = file
		self.data = data
        
		try:
			f = open(self.file, 'w')
			f.write("#!/bin/sh\n")
			f.write(self.data)
			f.close()
		except:
			print "Error with ".format(self.file)

	def genBhyveCommands(self,RAM,BootDrive,Name,NetInt,Drives,Console,ID,Path):
		BhyveLoad       = "/usr/sbin/bhyveload -m {} -d {} {}\n".format(RAM,BootDrive,ID)
		Bhyve           = "/usr/sbin/bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc {} {} -l com1,/dev/nmdm{}A -c 4 -m {} {} &\n".format(NetInt,Drives,Console,RAM,ID)
		ShellInABox     = "/usr/local/bin/shellinaboxd -t --service='/shell':'root':'wheel':'/root':'/usr/bin/cu -l /dev/nmdm{}B' --port={}{}".format(Console,ShellInABoxPref,ID)
		GrubBhyve       = "/usr/local/sbin/grub-bhyve -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path,RAM,ID)
		GrubBhyve2      = "/usr/local/sbin/grub-bhyve -d /grub2 -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path,RAM,ID)

		return (BhyveLoad,GrubBhyve,GrubBhyve2,Bhyve,ShellInABox)

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

	def genDisks(self,Disks,Interface,ID,Path):

		Count = 0
		self.interface = Interface

		Drives = ''
		BootDrive = ''

		if (Path == ""): Path = RootPath + "/" + str(ID)

		for Disk in Disks:

			if (Disk[2] == ""): DiskDrive = Disk[0]
			else: DiskDrive = Disk[2]

			if (Count == 0):
				BootDrive = "{}/{}".format(Path,DiskDrive)
				LinuxBoot = "{}".format(DiskDrive)

			Drives = "{} -s {}:0,virtio-blk,{}/{}".format(Drives,self.interface,Path,DiskDrive)
			Count += 1
			self.interface += 1

		return (BootDrive,Drives,self.interface,LinuxBoot)

	def createvps(self,id):
		
		vps = database.DB_VPS()
		vps.getVPS(id)

		ID 			= vps.getID()
		Name 		= vps.getName()
		RAM 		= vps.getRAM()
		Console 	= vps.getConsole()
		Image 		= vps.getImage()
		Path 		= vps.getPath()
		StartScript = vps.getStartScript()
		StopScript 	= vps.getStopScript()
		Disks 		= vps.getDisks(id)
		Devices 	= vps.getDevices(id)

		if (Path == ""): Path = RootPath + "/" + str(ID)

		Interface = 2

		NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)

		BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID,Path)

		BhyveLoad,GrubBhyve,GrubBhyve2,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID,Path)

		StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(ShellInABoxPref,ID)
		Network = "/sbin/ifconfig "

		DstImg = Path + "/" + "disk.img"

		if (Image == 1): SrcImg = SrcImgFreeBSD
		elif (Image == 2): SrcImg = SrcImgUbuntu
		elif (Image == 3): SrcImg = SrcImgCentos

		if not os.path.exists(Path):
			os.makedirs(Path)

		    
		if (self.createDisk == "on"):
			print "Copying file..."
			shutil.copyfile(SrcImg,BootDrive)

			StartScript = "{}/start.sh".format(Path)
			StopScript = "{}/stop.sh".format(Path)
			StartConsole = "{}/startconsole.sh".format(Path)
			StopConsole = "{}/stopconsole.sh".format(Path)
			DeviceMapScript = "{}/device.map".format(Path)

			# FreeBSD
			if (Image == 1):
				StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

			elif (Image == 2):
				DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path,LinuxBoot)

				self.generateScript(DeviceMapScript,DevicemapData)

				StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)
				print "Linux Device - Image 2 = {}".format(DevicemapData)

			elif (Image == 3):
				DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path,LinuxBoot)

				self.generateScript(DeviceMapScript,DevicemapData)

				StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve2,Bhyve,AddBridges,ShellInABox)
				print "Linux Device - Image 3 = {}".format(DevicemapData)
 

			StopScriptData = "{} --destroy --vm={}\n".format(Bhyvectl,ID)
			StartConsoleScript = ShellInABox
			StopConsoleScript = StopShellInABox

			self.generateScript(StartScript,StartScriptData)
			self.generateScript(StopScript,StopScriptData)
			self.generateScript(StartConsole,StartConsoleScript)
			self.generateScript(StopConsole,StopConsoleScript)

		return "Created VPS: {}\n".format(id)


	def updateVPS(self,vps_id):
		
		vps = database.DB_VPS()
		#vpsConn = modules.vps.VMFunc()
		vps.getVPS(vps_id)

		ID = vps.getID()
		Name = vps.getName()
		RAM = vps.getRAM()
		Console = vps.getConsole()
		Image = vps.getImage()
		Path = vps.getPath()
		StartScript = vps.getStartScript()
		StopScript = vps.getStopScript()

		Disks = vps.getDisks(vps_id)

		if (Path == ""): VPSPath = RootPath + "/" + str(vps_id)
		else: VPSPath = Path

		print "VPS Path: {}".format(VPSPath)

		Devices = vps.getDevices(vps_id)
		StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(ShellInABoxPref,ID)


		Interface = 2

		NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
		BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID,VPSPath)

		BhyveLoad,GrubBhyve,GrubBhyve2,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID,VPSPath)

		StartScript = "{}/start.sh".format(VPSPath)
		StopScript = "{}/stop.sh".format(VPSPath)
		DeviceMapScript = "{}/device.map".format(VPSPath)
		StartConsole = "{}/startconsole.sh".format(VPSPath)
		StopConsole = "{}/stopconsole.sh".format(VPSPath)

		StopScriptData = "{} --destroy --vm={}\n".format(Bhyvectl,ID)

		# FreeBSD
		if (Image == 1):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

		# Ubuntu
		elif (Image == 2):
			DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath,LinuxBoot)

			self.generateScript(DeviceMapScript,DevicemapData)
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)

			print "Linux Device - Image 2 = {}".format(DevicemapData)

		# Centos
		elif (Image == 3):

			DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath,LinuxBoot)

			self.generateScript(DeviceMapScript,DevicemapData)

			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve2,Bhyve,AddBridges,ShellInABox)

			print "Linux Device - Image 3 = {}".format(StartScriptData)

		StartConsoleScript = ShellInABox
		StopConsoleScript = StopShellInABox

		self.generateScript(StartConsole,StartConsoleScript)
		self.generateScript(StopConsole,StopConsoleScript)        

		self.generateScript(StartScript,StartScriptData)
		self.generateScript(StopScript,StopScriptData)

		return "Updated"

	def createDisk(self,id):

		cnx = mysql.connector.connect(**config)
		cursor = cnx.cursor()
		cursor.execute("select size,vps_id from disk where id=%s",(id,))
		Disk = cursor.fetchone()

		vps_id = Disk[1]
		size = Disk[0]
		Interface = 2

		vps = database.DB_VPS()
		vps.getVPS(vps_id)

		ID = vps.getID()
		Name = vps.getName()
		RAM = vps.getRAM()
		Console = vps.getConsole()
		Image = vps.getImage()
		Path = vps.getPath()
		StartScript = vps.getStartScript()
		StopScript = vps.getStopScript()


		Disks = vps.getDisks(vps_id)

		if (Path == ""): VPSPath = RootPath + "/" + str(vps_id)
		else: VPSPath = Path

		if (Image == 1): SrcImg = SrcImgFreeBSD
		elif (Image == 2): SrcImg = SrcImgUbuntu
		elif (Image == 3): SrcImg = SrcImgCentos


		Devices = vps.getDevices(vps_id)

		NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
		BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID,Path)

		create_disk = "truncate -s {}GB {}/{}/{}".format(size,RootPath,vps_id,id)
		output = subprocess.Popen(['/bin/sh', '-c', create_disk], stdout=subprocess.PIPE)

		BhyveLoad,GrubBhyve,GrubBhyve2,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID,VPSPath)

		StartScript = "{}{}/start.sh".format(RootPath,vps_id)

		# FreeBSD
		if (Image == 1):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

		elif (Image == 2):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)

		elif (Image == 3):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve2,Bhyve,AddBridges,ShellInABox)


		self.generateScript(StartScript,StartScriptData)

		return "Create Disk for VPS {}\n".format(vps_id)

	def deleteDisk(self,id):
		
		vps = database.DB_VPS()

		vps_id = vps.getDiskVPSID(id)

				
		vps.getVPS(vps_id)

		ID = vps.getID()
		Name = vps.getName()
		RAM = vps.getRAM()
		Console = vps.getConsole()
		Image = vps.getImage()
		Path = vps.getPath()
		StartScript = vps.getStartScript()
		StopScript = vps.getStopScript()
		

		if (Path == ""): VPSPath = RootPath + "/" + str(vps_id)
		else: VPSPath = Path

		if (Image == 1): SrcImg = SrcImgFreeBSD
		elif (Image == 2): SrcImg = SrcImgUbuntu
		elif (Image == 3): SrcImg = SrcImgCentos

		delete_disk = "rm {}/{}".format(VPSPath,id)

		output = subprocess.Popen(['/bin/sh', '-c', delete_disk], stdout=subprocess.PIPE)

		vps.deleteDisk(id)

		####
		#
		# Regenerate Scripts
		#
		####

		Disks = vps.getDisks(vps_id)
		Devices = vps.getDevices(vps_id)

		Interface = 2

		NetInt, AddTaps, DelTaps, AddBridges, Interface = self.genDevices(Devices, Interface)
		BootDrive, Drives, Interface, LinuxBoot = self.genDisks(Disks,Interface,ID,VPSPath)

		BhyveLoad,GrubBhyve,GrubBhyve2,Bhyve,ShellInABox = self.genBhyveCommands(RAM,BootDrive,Name,NetInt,Drives,Console,ID,VPSPath)

		StartScript = "{}/start.sh".format(VPSPath)


		# FreeBSD
		if (Image == 1):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)

		elif (Image == 2):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve,Bhyve,AddBridges,ShellInABox)

		elif (Image == 3):
			StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,GrubBhyve2,Bhyve,AddBridges,ShellInABox)



		StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps,BhyveLoad,Bhyve,AddBridges,ShellInABox)
		self.generateScript(StartScript,StartScriptData)

		return "Disk Delete"
