import os
import configparser
import subprocess
import shlex
import modules.database as database
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get VPS configurations from configuration.cfg
vps_configuration = configparser.ConfigParser()
vps_configuration.read("{}/../configuration.cfg".format(dir_path))

shell_in_a_box_prefix = vps_configuration.get('Global', 'ShellInABoxPref')
root_path = vps_configuration.get('Global', 'RootPath')
base_path = vps_configuration.get('Global', 'BasePath')
shell_in_a_box_command = vps_configuration.get('Global', 'ShellInABox')
freebsd_image_path = vps_configuration.get('Global', 'SrcImgFreeBSD')
centos_image_path = vps_configuration.get('Global', 'SrcImgCentos')
debian_image_path = vps_configuration.get('Global', 'SrcImgDebian')
ubuntu_image_path = vps_configuration.get('Global', 'SrcImgUbuntu')
windows10_image_path = vps_configuration.get('Global', 'SrcImgWin10')
bhyve_cmd = vps_configuration.get('Global', 'Bhyvecmd')
bhyveload_cmd = vps_configuration.get('Global', 'Bhyveload')
bhyvectl_cmd = vps_configuration.get('Global', 'Bhyvectl')
grub_cmd = vps_configuration.get('Global', 'Grubcmd')
pid_file_path = vps_configuration.get('Global', 'PIDFile')
log_file_path = vps_configuration.get('Global', 'LogFile')
host_address = str(vps_configuration.get('Global', 'HOST'))
port = int(vps_configuration.get('Global', 'PORT'))
password_string = vps_configuration.get('Global', 'PassString')
zfs_enable = int(vps_configuration.get('Global', 'ZFSEnable'))
zfs_root_path = vps_configuration.get('Global', 'ZFSRoot')
zfs_command_path = vps_configuration.get('Global', 'ZFSCmd')
ifconfig_command_path = vps_configuration.get('Global', 'IFConfig')
touch_command_path = vps_configuration.get('Global', 'Touch')
copy_command_path = vps_configuration.get('Global', 'CP')
delete_command_path = vps_configuration.get('Global', 'RM')
log_file_path = vps_configuration.get('Global', 'LogFile')
vm_status_path = vps_configuration.get('Global','VMStatusPath')
start_interface = int(vps_configuration.get('Global','InterfaceStartNumber'))
start_disk = int(vps_configuration.get('Global','DiskStartNumber'))

database_user = vps_configuration.get('Database', 'database_user')
database_password = vps_configuration.get('Database', 'database_password')
database_host = vps_configuration.get('Database', 'database_host')
database_database = vps_configuration.get('Database', 'database_name')
raise_on_warnings = str(vps_configuration.get('Database', 'raise_on_warnings'))

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


class VMFunctions(database.DatabaseVPS, database.DatabaseNetwork):
    def __init__(self):
        self.id = ''
        Command = ''

        create_disk_on_vps_creation = 'no'
        snapshot_name = ""

        self.command = Command
        self.create_disk_selected = create_disk_on_vps_creation
        self.snapShot = snapshot_name

        self.log = ''

        self.freebsd = 1
        self.ubuntu = 2
        self.centos = 3
        self.win10 = 4
        self.status = ''

        self.vps = database.DatabaseVPS()

    def get_status(self):
        return (self.status)

    def get_network_status(self, id):
        output = self.execute_command(ifconfig_command_path + ' tap' + format(id) + ' | grep UP')

        if output == "":
            return "DOWN"

        return "UP"

    def stop_network(self, id):
        output, error = self.execute_command(ifconfig_command_path +
                                             ' tap' + format(id) +
                                             ' down')
        return output

    def start_network(self, id):
        output, error = self.execute_command(ifconfig_command_path + ' tap' + format(id) + ' up')

        return output

    def log_entry(data):
        try:
            f = open(log_file_path, 'a')
            f.write(data)
            f.close()
        except:
            return "Error with ".format(log_file_path)

    def execute_bhyve_command(self, command, ID):
        self.id = ID
        output = ''
        error = ''
        args = shlex.split('/bin/sh ' + command)

        try:
            f = open(log_file_path, 'a')
            pid = os.fork()
            f.write('created fork {}\n'.format(pid))

            if (pid == 0):
                f.write('executing command\n')
                # proc = subprocess.run(['/bin/sh', '-c', command],
                #                         stdout=subprocess.PIPE,
                #                         stderr=subprocess.STDOUT,
                #                         close_fds=True)

                proc = subprocess.Popen(args)

                os._exit(0)
                f.write('command executed\n')
                output, error = proc.communicate()
                f.write(output)
                f.write(error)
        except:
            f.write('an error occured executing command\n')
            f.write(output)
            f.write(error)
            f.close()
            return False

        f.close()

        return True

    def execute_command(self, cmd):
        proc = subprocess.Popen(['/bin/sh', '-c', cmd],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                close_fds=True)
        output, error = proc.communicate()

        return (output, error)

    @staticmethod
    def fork_and_execute_command(cmd):
        pid = os.fork()

        if pid == 0:
            process = subprocess.Popen(['/bin/sh', '-c', cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
            os._exit(0)

            return process.communicate()

    def take_snapshot_of_vps(self, id, snapshot):
        try:
            if (snapshot == ""): snapshot = str(time.time())

            self.command = zfs_command_path + \
                           ' snapshot ' + \
                           zfs_root_path + \
                           '/' + str(id) + \
                           '@' + str(snapshot)
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
        path = vm_status_path + str(vps_id)

        VPS = self.vps.get_vps_details(self.id)

        vps_startscript = VPS[5]

        if (vps_startscript == ""): vps_name = str(self.id)

        if (os.path.exists(path)):
            self.status = "Running"
            return "Running"
        else:
            if (os.path.exists(root_path + str(vps_id) + "/installing.txt")):
                return "Installing"

            self.status = "Stopped"
            return "Stopped"

    def start_vps(self, id):
        self.vps.get_vps_details(id)
        self.execute_bhyve_command(self.vps.start_command(root_path), str(id))
        return "Started VPS {}\n".format(id)

    def stop_vps(self, id):
        self.vps.get_vps_details(id)
        self.execute_bhyve_command(self.vps.stop_command(root_path), str(id))
        self.execute_bhyve_command(self.vps.stop_console(root_path), str(id))
        return "Stopped VPS {}\n".format(id)

    def delete_vps(self, id):
        source_path = root_path + str(id)
        destination_path = root_path + "deleted/" + str(id)

        if (zfs_enable == 1):
            cmd = zfs_command_path + " destroy " + zfs_root_path + "/" + str(id)
            output, error = self.execute_command(cmd)
            return error
        else:
            if os.path.exists(source_path):
                return os.renames(source_path, destination_path)
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

    def get_network_interface(self):
        return self.network_interface

    def generate_bhyve_commands(self):

        self.bhyve_load_command = bhyveload_cmd + " -m {} " \
                                  "-d {} {}\n".format(self.vps_memory,
                                                      self.boot_drive,
                                                      self.vps_id)
        self.bhyve_command = bhyve_cmd + " -A -H -P " \
                             "-s 0:0,hostbridge " \
                             "-s 1:0,lpc {} {} " \
                             "-l com1,/dev/nmdm{}A " \
                             "-c 4 -m {} {} &\n". \
            format(self.network_interface, self.attached_drives,
                   self.vps_console_number, self.vps_memory,
                   self.vps_id)
        self.shell_in_a_box = shell_in_a_box_command + " " \
                              "-t --service='/shell':'root':'wheel'" \
                              ":'/root':'/usr/bin/cu " \
                              "-l /dev/nmdm{}B' " \
                              "--port={}{}". \
            format(self.vps_console_number, shell_in_a_box_prefix,
                   self.vps_id)
        self.grub_bhyve_command = "/usr/local/sbin/grub-bhyve " \
                                  "-m {}/device.map " \
                                  "-r hd0,msdos1 " \
                                  "-M {} {}".format(self.vps_path, self.vps_memory,
                                                    self.vps_id)
        self.grub_bhyve2_command = grub_cmd + \
                                   "-d /grub2 " \
                                   "-m {}/device.map " \
                                   "-r hd0,msdos1 -M {} {}". \
            format(self.vps_path, self.vps_memory, self.vps_id)

    def generate_devices(self, Devices, Interface):
        Count = 0
        NetInt = ''
        # Interface = start_interface
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

        # if Disks is not None:

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

    def create_vps(self, vps_id):
        self.get_vps_details(vps_id)

        self.get_vps_path(vps_id)

        interface = start_interface
        self.disk_number = start_disk

        network_interfaces, network_tap_devices, del_taps, network_bridge_devices, interface = self.generate_devices(
            self.vps_attached_network_devices, interface)
        boot_drive, drives, interface, linux_boot_device = self.generate_disks(self.vps_attached_disks, self.disk_number,
                                                                               vps_id, self.vps_path)
        self.generate_bhyve_commands()

        stop_shell_in_a_box_command = "/usr/bin/sockstat -4 -l | grep :{}{}".format(shell_in_a_box_prefix, vps_id)
        # ifconfig_command = "/sbin/ifconfig "

        # destination_image_path = Path + "/" + "disk.img"

        source_image_path = self.set_image_path(self.vps_image_id)

        if not os.path.exists(self.vps_path):
            if (zfs_enable == 1):
                cmd = zfs_command_path + " create " + zfs_root_path + "/" + str(vps_id)
                self.execute_command(cmd)
            else:
                os.makedirs(self.vps_path)

        if (self.create_disk_selected == "on"):
            cmd = touch_command_path + " " + root_path + str(
                vps_id) + "/installing.txt" + " && " + copy_command_path + " " + source_image_path + " " + boot_drive + " && " + delete_command_path + " " + root_path + str(
                vps_id) + "/installing.txt"

            self.fork_and_execute_command(cmd)

            start_script = "{}/start.sh".format(self.vps_path)
            stop_script = "{}/stop.sh".format(self.vps_path)
            start_console = "{}/startconsole.sh".format(self.vps_path)
            stop_console = "{}/stopconsole.sh".format(self.vps_path)
            device_map_script = "{}/device.map".format(self.vps_path)

            if (self.vps_image_id == self.freebsd):
                start_script_data = "{}\n{}\n{}\n{}\n{}\n".format(network_tap_devices, self.bhyve_load_command,
                                                                  self.bhyve_command, network_bridge_devices,
                                                                  self.shell_in_a_box)
            elif (self.vps_image_id == self.ubuntu):
                devicemap_data = "(hd0) {}/{}\n(cd0) .\n".format(self.vps_path, linux_boot_device)
                self.create_script(device_map_script, devicemap_data)
                start_script_data = "{}\n{}\n{}\n{}\n{}\n".format(network_tap_devices, self.grub_bhyve_command,
                                                                  self.bhyve_command, network_bridge_devices,
                                                                  self.shell_in_a_box)

            elif (self.vps_image_id == self.centos):
                devicemap_data = "(hd0) {}/{}\n(cd0) .\n".format(self.vps_path, linux_boot_device)
                self.create_script(device_map_script, devicemap_data)
                start_script_data = "{}\n{}\n{}\n{}\n{}\n".format(network_tap_devices, self.grub_bhyve2_command,
                                                                  self.bhyve_command, network_bridge_devices,
                                                                  self.shell_in_a_box)
            elif (self.vps_image_id == self.win10):
                start_script_data = "{}\n{}\n{}\n{}\n{}\n".format(network_tap_devices, self.bhyve_load_command,
                                                                  self.bhyve_command, network_bridge_devices,
                                                                  self.shell_in_a_box)

            stop_script_data = "{} --destroy --vm={}\n".format(bhyvectl_cmd, vps_id)
            start_console_script = self.shell_in_a_box
            stop_console_script = stop_shell_in_a_box_command

            self.create_script(start_script, start_script_data)
            self.create_script(stop_script, stop_script_data)
            self.create_script(start_console, start_console_script)
            self.create_script(stop_console, stop_console_script)

        return "Created VPS: {}\n".format(id)

    def get_vps_path(self, vps_id):
        if (self.vps_path == ""):
            self.vps_path = root_path + "/" + str(vps_id)

    def get_vps_details(self, id):
        self.vps.get_vps_details(id)
        self.vps_id = self.vps.get_vps_id()
        self.vps_name = self.vps.get_vps_name()
        self.vps_memory = self.vps.get_vps_memory()
        self.vps_console_number = self.vps.get_console()
        self.vps_image_id = self.vps.get_image()
        self.vps_path = self.vps.get_path()
        self.vps_attached_disks = self.vps.get_disks_details_from_database(id)
        self.vps_attached_network_devices = self.vps.get_devices(id)
        return self.vps_attached_disks, self.vps_attached_network_devices, \
               self.vps_console_number, self.vps_id, self.vps_image_id, self.vps_memory, \
               self.vps_name, self.vps_path

    def set_image_path(self, image_id):
        if (image_id == self.freebsd):
            source_image_path = freebsd_image_path
        elif (image_id == self.ubuntu):
            source_image_path = ubuntu_image_path
        elif (image_id == self.centos):
            source_image_path = centos_image_path
        elif (image_id == self.win10):
            source_image_path = windows10_image_path

        return source_image_path

    def update_vps(self, vps_id):
        self.vps.get_vps_details(vps_id)
        self.get_vps_details(vps_id)
        self.get_vps_path(vps_id)

        vps_network_devices = self.vps.get_devices(vps_id)
        stop_shell_in_a_box = "/usr/bin/sockstat -4 -l | grep :{}{}". \
            format(shell_in_a_box_prefix, vps_id)

        interface = start_interface
        self.disk_number = start_disk

        self.network_interface, self.add_tap_device, self.delete_tap_device, self.add_bridge_interfaces, \
        self.interface = self.generate_devices(vps_network_devices, interface)
        self.boot_drive, self.attached_drives, self.interface, self.linux_boot_drive = \
            self.generate_disks(self.vps_attached_disks, self.disk_number, vps_id, self.vps_path)

        self.generate_bhyve_commands()

        start_script_path = "{}/start.sh".format(self.vps_path)
        stop_script_path = "{}/stop.sh".format(self.vps_path)
        device_map_script = "{}/device.map".format(self.vps_path)
        start_console_path = "{}/startconsole.sh".format(self.vps_path)
        stop_console_script_path = "{}/stopconsole.sh".format(self.vps_path)

        stop_script_data = "{} --destroy --vm={}\n".format(bhyvectl_cmd, vps_id)

        start_script_data = self.generate_script_data(self.add_bridge_interfaces, self.add_tap_device,
                                                      self.bhyve_command,
                                                      self.bhyve_load_command, device_map_script,
                                                      self.grub_bhyve2_command,
                                                      self.grub_bhyve_command, self.linux_boot_drive,
                                                      shell_in_a_box_command,
                                                      self.vps_image_id, self.vps_path)

        start_console_script = shell_in_a_box_command
        stop_console_script = stop_shell_in_a_box

        self.create_script(start_console_path, start_console_script)
        self.create_script(stop_console_script_path, stop_console_script)

        self.create_script(start_script_path, start_script_data)
        self.create_script(stop_script_path, stop_script_data)

        return "VPS {} Updated\n".format(vps_id)

    def generate_script_data(self, add_bridge_interfaces, add_tap_device, bhyve_command, bhyve_load_command,
                             device_map_script, grub2_bhyve_load_command, grub_bhyve_load_command, linux_boot_drive,
                             shell_in_a_box_command, vps_image_id, vps_path):
        if vps_image_id is self.freebsd:
            return "{}\n{}\n{}\n{}\n{}\n".format(add_tap_device, bhyve_load_command, bhyve_command,
                                                 add_bridge_interfaces, shell_in_a_box_command)
        elif vps_image_id is self.ubuntu:
            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(vps_path, linux_boot_drive)
            self.create_script(device_map_script, DevicemapData)
            return "{}\n{}\n{}\n{}\n{}\n".format(add_tap_device, grub_bhyve_load_command, bhyve_command,
                                                 add_bridge_interfaces, shell_in_a_box_command)
        elif vps_image_id is self.centos:
            DevicemapData = "(hd0) {}/{}\n(cd0) .\n".format(vps_path, linux_boot_drive)
            self.create_script(device_map_script, DevicemapData)
            return "{}\n{}\n{}\n{}\n{}\n".format(add_tap_device, grub2_bhyve_load_command, bhyve_command,
                                                 add_bridge_interfaces, shell_in_a_box_command)

    def create_disk_image(self, id):
        Disk = self.vps.get_disk(id)

        vps_id = Disk[1]
        size = Disk[0]

        vps_network_devices = self.vps.get_devices(vps_id)

        interface = start_interface

        self.vps.get_vps_details(vps_id)
        self.get_vps_details(vps_id)

        vps_attached_disks, vps_attached_network_devices, vps_console_number, \
        vps_id, vps_image_id, vps_memory, vps_name, vps_path = self.get_vps_details(
            id)

        if (self.vps_path == ""):
            self.vps_path = root_path + "/" + str(vps_id)

        SrcImg = self.set_image_path(self.vps_image_id)

        self.network_interface, self.add_tap_device, self.delete_tap_device, self.add_bridge_interfaces, \
        self.interface = self.generate_devices(vps_network_devices, interface)
        self.boot_drive, self.attached_drives, self.interface, self.linux_boot_drive = \
            self.generate_disks(self.vps_attached_disks, interface, vps_id, self.vps_path)

        create_disk = "truncate -s {}GB {}/{}/{}".format(size, root_path, vps_id, id)
        output = subprocess.Popen(['/bin/sh', '-c', create_disk], stdout=subprocess.PIPE)

        self.generate_bhyve_commands()

        StartScript = "{}{}/start.sh".format(root_path, vps_id)

        if (self.vps_image_id == self.freebsd):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(self.add_tap_device, self.bhyve_load_command,
                                                            self.bhyve_command, self.add_bridge_interfaces,
                                                            shell_in_a_box_command)
        elif (self.vps_image_id == self.ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(self.add_tap_device, self.grub_bhyve_command,
                                                            self.bhyve_command, self.add_bridge_interfaces,
                                                            shell_in_a_box_command)
        elif (self.vps_image_id == self.centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(self.add_tap_device, self.grub2_bhyve_command,
                                                            self.bhyve_command, self.add_bridge_interfaces,
                                                            shell_in_a_box_command)

        self.create_script(StartScript, StartScriptData)

        return "Create Disk for VPS {}\n".format(vps_id)

    def delete_disk(self, id):

        vps_id = self.vps.get_vps_id_associated_with_disk(id)

        self.vps.get_vps_details(vps_id)
        self.get_vps_details(vps_id)

        if (self.vps_path == ""):
            self.vps_path = root_path + "/" + str(vps_id)

        delete_disk = "rm {}/{}".format(self.vps_path, id)

        try:
            process = subprocess.Popen(['/bin/sh', '-c', delete_disk], stdout=subprocess.PIPE)
            output, err = process.communicate()
        except:
            # return process.returncode
            return "Delete disk failed"

        self.vps.delete_disk_from_database(id)

        ####
        #
        # Regenerate Scripts
        #
        ####

        Disks = self.vps.get_disks_details_from_database(vps_id)
        Devices = self.vps.get_devices(vps_id)

        Interface = start_interface

        NetInt, AddTaps, DelTaps, AddBridges, Interface = self.generate_devices(Devices, Interface)
        self.generate_disks(Disks, Interface, self.vps_id, self.vps_path)

        self.generate_bhyve_commands()

        StartScript = "{}/start.sh".format(self.vps_path)

        # FreeBSD
        if (self.vps_image_id == self.freebsd):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, self.bhyve_load_command, self.bhyve_command,
                                                            AddBridges, self.shell_in_a_box)

        elif (self.vps_image_id == self.ubuntu):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, self.grub_bhyve_command, self.bhyve_command,
                                                            AddBridges, self.shell_in_a_box)

        elif (self.vps_image_id == self.centos):
            StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, self.grub_bhyve2_command, self.bhyve_command,
                                                            AddBridges, self.shell_in_a_box)

        StartScriptData = "{}\n{}\n{}\n{}\n{}\n".format(AddTaps, self.bhyve_load_command, self.bhyve_command,
                                                        AddBridges, self.shell_in_a_box)

        if (self.create_script(StartScript, StartScriptData)):
            return "An error occurred generating script"

        return "Disk {} Delete\n".format(id)
