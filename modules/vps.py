from subprocess import Popen
from subprocess import check_output
import mysql.connector
import os, subprocess
import shutil
import configparser
import subprocess
import modules.database as database
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
Config = configparser.ConfigParser()
Config.read("{}/../configuration.cfg".format(dir_path))

shell_in_a_box_prefix = Config.get('Global', 'ShellInABoxPref')
root_path = Config.get('Global', 'RootPath')
base_path = Config.get('Global', 'BasePath')
shell_in_a_box_command = Config.get('Global', 'ShellInABox')
freebsd_image_path = Config.get('Global', 'SrcImgFreeBSD')
centos_image_path = Config.get('Global', 'SrcImgCentos')
debian_image_path = Config.get('Global', 'SrcImgDebian')
ubuntu_image_path = Config.get('Global', 'SrcImgUbuntu')
windows10_image_path = Config.get('Global', 'SrcImgWin10')
bhyvectl_path = Config.get('Global', 'Bhyvectl')
pid_file_path = Config.get('Global', 'PIDFile')
log_file_path = Config.get('Global', 'LogFile')
host_address = str(Config.get('Global', 'HOST'))
port = int(Config.get('Global', 'PORT'))
password_string = Config.get('Global', 'PassString')
zfs_enable = int(Config.get('Global', 'ZFSEnable'))
zfs_root_path = Config.get('Global', 'ZFSRoot')
zfs_command_path = Config.get('Global', 'ZFSCmd')
ifconfig_command_path = Config.get('Global', 'IFConfig')
touch_command_path = Config.get('Global', 'Touch')
copy_command_path = Config.get('Global', 'CP')
delete_command_path = Config.get('Global', 'RM')

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


class VMFunctions:
    def __init__(self):
        self.id = ''
        Command = ''

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

        self.freebsd = 1
        self.ubuntu = 2
        self.centos = 3
        self.win10 = 4
        self.status = ''

    '''def check_security(self):

        if (PassString == self.Auth):
            return "Pass"
        else:
            return "Fail"'''

    def get_status(self):
        return (self.status)

    def get_network_status(self, id):
        output = self.execute_command(ifconfig_command_path + ' tap' + format(id) + ' | grep UP')

        if (output == ""):
            output = "DOWN"
        else:
            output = "UP"

        return output

    def stop_network(self, id):
        output, error = self.execute_command(ifconfig_command_path +
                                    ' tap' + format(id) +
                                    ' down')
        return output

    def start_network(self, id):
        output, error = self.execute_command(ifconfig_command_path + ' tap' + format(id) + ' up')

        return output

    def get_command(self):
        return self.command

    def get_id(self):
        return self.id

    def logentry(self, data):
        try:
            f = open(log_file_path, 'a')
            f.write(data)
            f.close()
        except:
            return "Error with ".format(log_file_path)

    def execute_bhyve_command(self, command, ID):
        self.command = command
        self.id = ID

        try:
            pid = os.fork()

            if (pid == 0):
                self.id = root_path + self.id
                args = ("-c", self.command, self.id)
                proc = Popen(['/bin/sh', '-c', self.command, '999'],
                             cwd=self.id,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             close_fds=True)
                os._exit(0)
        except:
            return "failed to execute bhyve command"

    def execute_command(self, cmd):
        proc = subprocess.Popen(['/bin/sh', '-c', cmd],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)

        output, error = proc.communicate()

        return (output, error)

    def fork_and_execute_command(self, cmd):
        pid = os.fork()

        if (pid == 0):
            proc = subprocess.Popen(['/bin/sh', '-c', cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            os._exit(0)

            output, error = proc.communicate()

    def take_snapshot_of_vps(self, id, snapshot):

        try:

            if (snapshot == ""): snapshot = str(time.time())

            self.command = zfs_command_path + ' snapshot ' + zfs_root_path + '/' + str(id) + '@' + str(snapshot)

            self.id = root_path + str(id)

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            # output,error = proc.communicate()

            return "Snapshot name = {}".format(snapshot)
        except:
            return "An error occurred"

    def list_snapshots(self, id):

        try:
            self.command = zfs_command_path + ' list -rt snapshot ' + zfs_root_path + '/' + str(id)
            self.id = root_path + str(id)

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            output, error = proc.communicate()
            return output
        except:
            return "An error occured"

    def restore_snapshot(self, id, snapshot):

        try:
            self.command = zfs_command_path + ' rollback ' + snapshot

            proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)

            output, error = proc.communicate()
            return output

        except:
            return error

    def remove_snapshot(self, id, snapshot):

        self.command = zfs_command_path + ' destroy ' + snapshot

        proc = subprocess.Popen(['/bin/sh', '-c', self.command],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)

        return "Snapshot Removed"

    def restart_console(self, id):
        stopconsole = "sh " + root_path + "/" + str(id) + "/stopconsole.sh"
        startconsole = "sh " + root_path + "/" + str(id) + "/startconsole.sh"

        output = subprocess.Popen(['/bin/sh', '-c', stopconsole], stdout=subprocess.PIPE)

        out, err = output.communicate()

        pid = out.split()

        if (len(pid) > 1):
            term = "kill -TERM " + str(pid[2])
            output2 = subprocess.Popen(['/bin/sh', '-c', term], stdout=subprocess.PIPE)

        output3 = subprocess.Popen(['/bin/sh', '-c', startconsole], stdout=subprocess.PIPE)

        return "Terminal Restarted\n"

    def check_vps_status(self, vps_id):
        self.id = vps_id

        VPS_Conn = database.DatabaseVPS()
        VPS = VPS_Conn.get_vps_details(self.id)

        vps_startscript = VPS[5]

        if (vps_startscript == ""): vps_name = str(self.id)

        if (os.path.exists("/dev/vmm/" + str(vps_id))):
            self.status = "Running"
            return "Running"
        else:
            if (os.path.exists(root_path + str(vps_id) + "/installing.txt")):
                return "Installing"

            self.status = "Stopped"
            return "Stopped"



    def start_vps(self, id):
        VPS_DB = database.DatabaseVPS()
        VPS_DB.get_vps_details(id)
        self.execute_bhyve_command(VPS_DB.start_command(root_path), str(id))
        return "Started VPS {}\n".format(id)

    def stop_vps(self, id):
        VPS_DB = database.DatabaseVPS()
        VPS_DB.get_vps_details(id)
        self.execute_bhyve_command(VPS_DB.stop_command(root_path), str(id))
        self.execute_bhyve_command(VPS_DB.stop_console(root_path), str(id))
        return "Stopped VPS {}\n".format(id)

    def delete_vps(self, id):
        PathOrig = root_path + str(id)
        PathDest = root_path + "deleted/" + str(id)

        if (zfs_enable == 1):
            cmd = zfs_command_path + " destroy " + zfs_root_path + "/" + str(id)
            output, error = self.execute_command(cmd)
            return error
        else:
            if os.path.exists(PathOrig):
                return os.renames(PathOrig, PathDest)
            else:
                return "Disk doesn't exist"

    def create_script(self, file, data):

        self.file = file
        self.data = data

        try:
            f = open(self.file, 'w')
            f.write("#!/bin/sh\n")
            f.write(self.data)
            f.close()
        except:
            return "Error occurred generating script".format(self.file)

    def generate_bhyve_commands(self, RAM, BootDrive, Name, NetInt, Drives, Console, ID, Path):
        BhyveLoad = "/usr/sbin/bhyveload -m {} -d {} {}\n".format(RAM, BootDrive, ID)
        Bhyve = "/usr/sbin/bhyve -A -H -P -s 0:0,hostbridge -s 1:0,lpc {} {} -l com1,/dev/nmdm{}A -c 4 -m {} {} &\n".format(
            NetInt, Drives, Console, RAM, ID)
        ShellInABox = "/usr/local/bin/shellinaboxd -t --service='/shell':'root':'wheel':'/root':'/usr/bin/cu -l /dev/nmdm{}B' --port={}{}".format(
            Console, shell_in_a_box_prefix, ID)
        GrubBhyve = "/usr/local/sbin/grub-bhyve -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path, RAM, ID)
        GrubBhyve2 = "/usr/local/sbin/grub-bhyve -d /grub2 -m {}/device.map -r hd0,msdos1 -M {} {}".format(Path, RAM,ID)

        return (BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox)

    def generate_devices(self, Devices, Interface):
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

    def generate_disks(self, Disks, Interface, ID, Path):
        Count = 0
        self.interface = Interface

        Drives = ''
        BootDrive = ''
        LinuxBoot = ''

        if (Path == ""):
            Path = root_path + "/" + str(ID)

        #if Disks is not None:

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

    def create_vps(self, id):

        vps = database.DatabaseVPS()
        vps.get_vps_details(id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.get_console()
        Image = vps.get_image()
        Path = vps.get_path()
        Disks = vps.get_disks_details_from_database(id)
        Devices = vps.get_devices(id)

        if (Path == ""):
            Path = root_path + "/" + str(ID)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.generate_devices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.generate_disks(Disks, Interface, ID, Path)
        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.generate_bhyve_commands(RAM, BootDrive, Name, NetInt,
                                                                                            Drives, Console, ID, Path)

        StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(shell_in_a_box_prefix, ID)
        Network = "/sbin/ifconfig "

        DstImg = Path + "/" + "disk.img"

        SrcImg = self.set_image_path(Image)

        if not os.path.exists(Path):
            if (zfs_enable == 1):
                cmd = zfs_command_path + " create " + zfs_root_path + "/" + str(ID)
                self.execute_command(cmd)
            else:
                os.makedirs(Path)

        if (self.createDisk == "on"):
            cmd = touch_command_path + " " + root_path + str(
                ID) + "/installing.txt" + " && " + copy_command_path + " " + SrcImg + " " + BootDrive + " && " + delete_command_path + " " + root_path + str(
                ID) + "/installing.txt"

            self.fork_and_execute_command(cmd)

            StartScript = "{}/start.sh".format(Path)
            StopScript = "{}/stop.sh".format(Path)
            StartConsole = "{}/startconsole.sh".format(Path)
            StopConsole = "{}/stopconsole.sh".format(Path)
            DeviceMapScript = "{}/device.map".format(Path)

            if (Image == self.freebsd):
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)
            elif (Image == self.ubuntu):
                DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path, LinuxBoot)
                self.create_script(DeviceMapScript, DevicemapData)
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

            elif (Image == self.centos):
                DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(Path, LinuxBoot)
                self.create_script(DeviceMapScript, DevicemapData)
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)
            elif (Image == self.win10):
                StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)



            StopScriptData = "{} --destroy --vm={}\n".format(bhyvectl_path, ID)
            StartConsoleScript = ShellInABox
            StopConsoleScript = StopShellInABox

            self.create_script(StartScript, StartScriptData)
            self.create_script(StopScript, StopScriptData)
            self.create_script(StartConsole, StartConsoleScript)
            self.create_script(StopConsole, StopConsoleScript)

        return "Created VPS: {}\n".format(id)

    def set_image_path(self, Image):
        if (Image == self.freebsd):
            SrcImg = freebsd_image_path
        elif (Image == self.ubuntu):
            SrcImg = ubuntu_image_path
        elif (Image == self.centos):
            SrcImg = centos_image_path
        elif (Image == self.win10):
            SrcImg = windows10_image_path

        return SrcImg

    def update_vps(self, vps_id):

        vps = database.DatabaseVPS()
        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.get_console()
        Image = vps.get_image()
        Path = vps.get_path()
        StartScript = vps.get_start_script()
        StopScript = vps.get_stop_script()

        Disks = vps.get_disks_details_from_database(vps_id)

        if (Path == ""):
            VPSPath = root_path + str(vps_id)
        else:
            VPSPath = Path

        Devices = vps.get_devices(vps_id)
        StopShellInABox = "/usr/bin/sockstat -4 -l | grep :{}{}".format(shell_in_a_box_prefix, ID)

        Interface = 2

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.generate_devices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.generate_disks(Disks, Interface, ID, VPSPath)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.generate_bhyve_commands(RAM, BootDrive, Name, NetInt,
                                                                                            Drives, Console, ID, VPSPath)

        StartScript = "{}/start.sh".format(VPSPath)
        StopScript = "{}/stop.sh".format(VPSPath)
        DeviceMapScript = "{}/device.map".format(VPSPath)
        StartConsole = "{}/startconsole.sh".format(VPSPath)
        StopConsole = "{}/stopconsole.sh".format(VPSPath)

        StopScriptData = "{} --destroy --vm={}\n".format(bhyvectl_path, ID)

        # FreeBSD
        if (Image == 1):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        # Ubuntu
        elif (Image == 2):
            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath, LinuxBoot)

            self.create_script(DeviceMapScript, DevicemapData)
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

        # Centos
        elif (Image == 3):

            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(VPSPath, LinuxBoot)

            self.create_script(DeviceMapScript, DevicemapData)

            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

        else:
            return "Error: no image specified"

        StartConsoleScript = ShellInABox
        StopConsoleScript = StopShellInABox

        self.create_script(StartConsole, StartConsoleScript)
        self.create_script(StopConsole, StopConsoleScript)

        self.create_script(StartScript, StartScriptData)
        self.create_script(StopScript, StopScriptData)

        return "VPS {} Updated\n".format(vps_id)

    def create_disk_image(self, id):
        vps = database.DatabaseVPS()
        Disk = vps.get_disk(id)

        vps_id = Disk[1]
        size = Disk[0]
        Interface = 2

        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.get_console()
        Image = vps.get_image()
        Path = vps.get_path()
        StartScript = vps.get_start_script()
        StopScript = vps.get_stop_script()

        # return "Create Disk for VPS 1\n"

        Disks = vps.get_disks_details_from_database(vps_id)

        if (Path == ""):
            VPSPath = root_path + "/" + str(vps_id)
        else:
            VPSPath = Path

        SrcImg = self.set_image_path(Image)

        Devices = vps.get_devices(vps_id)

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.generate_devices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.generate_disks(Disks, Interface, ID, Path)

        create_disk = "truncate -s {}GB {}/{}/{}".format(size, root_path, vps_id, id)
        output = subprocess.Popen(['/bin/sh', '-c', create_disk], stdout=subprocess.PIPE)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.generate_bhyve_commands(RAM, BootDrive, Name, NetInt,
                                                                                            Drives, Console, ID, VPSPath)

        StartScript = "{}{}/start.sh".format(root_path, vps_id)

        # FreeBSD
        if (Image == self.freebsd):
            # return "Create Disk for VPS 1\n"
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

        self.create_script(StartScript, StartScriptData)

        return "Create Disk for VPS {}\n".format(vps_id)

    def delete_disk(self, id):

        vps = database.DatabaseVPS()

        vps_id = vps.get_vps_id_associated_with_disk(id)

        vps.get_vps_details(vps_id)

        ID = vps.get_vps_id()
        Name = vps.get_vps_name()
        RAM = vps.get_vps_memory()
        Console = vps.get_console()
        Image = vps.get_image()
        Path = vps.get_path()
        StartScript = vps.get_start_script()
        StopScript = vps.get_stop_script()

        if (Path == ""):
            VPSPath = root_path + "/" + str(vps_id)
        else:
            VPSPath = Path

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

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.generate_devices(Devices, Interface)
        BootDrive, Drives, Interface, LinuxBoot = self.generate_disks(Disks, Interface, ID, VPSPath)

        BhyveLoad, GrubBhyve, GrubBhyve2, Bhyve, ShellInABox = self.generate_bhyve_commands(RAM, BootDrive, Name, NetInt,
                                                                                            Drives, Console, ID, VPSPath)

        StartScript = "{}/start.sh".format(VPSPath)

        # FreeBSD
        if (Image == self.freebsd):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve, Bhyve, AddBridges, ShellInABox)

        elif (Image == self.centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, GrubBhyve2, Bhyve, AddBridges, ShellInABox)

        StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, BhyveLoad, Bhyve, AddBridges, ShellInABox)

        if (self.create_script(StartScript, StartScriptData)):
            return "An error occurred generating script"

        return "Disk {} Delete\n".format(id)
