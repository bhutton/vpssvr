import unittest
import os
import mock
from mock import patch
import modules.database
import modules.vps
import time


class TestStatus(unittest.TestCase):

    # See what happens if an invalid password is used
    def test_checkSecurity(self):
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
        assert vpsConn.executeCommand() == "Connection Failed"

    @patch('mysql.connector')
    def test_database_connectivity(self, exec_function_connect):
        m = modules.database.DatabaseNetwork()
        assert (m.get_database_connection_status() == True)

    # modify test for database exception!!!
    def test_database_connectivity(self):
        m = modules.database.DatabaseNetwork()
        assert(m.get_database_connection_status() == False)

    @patch('mysql.connector')
    def test_get_interface(self, exec_function_connect):
        exec_function_connect.connect.return_value.\
            cursor.return_value.\
            fetchall.return_value = [1,'tue-23-2000',3]
        m = modules.database.DatabaseNetwork()
        assert (len(m.get_interface()) > 0)

    @patch('mysql.connector')
    def test_get_traffic_data(self, exec_function_connect):
        m = modules.database.DatabaseNetwork()
        exec_function_connect.connect.return_value. \
            cursor.return_value. \
            fetchall.return_value = [1,3,4]
        assert(len(m.get_traffic_data(1)) > 0)

    # Test NetStatus Module via the Execute Command control function
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.execcmd')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_execute_command_netStatus(
            self,
            exec_function_dbconnect,
            exec_function_checkSecurity,
            exec_function_execcmd):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        # Check that tap interface associated with VM is UP
        modules.vps.VMFunc.execcmd.return_value = 'tap1: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,netStatus")
        assert vpsConn.executeCommand() == 'UP'

        # Check that tap interface associated with VM is DOWN
        modules.vps.VMFunc.execcmd.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,netStatus")
        assert vpsConn.executeCommand() == 'DOWN'


class TestStartStop(unittest.TestCase):
    @patch('modules.database.DatabaseVPS')
    @patch('modules.database.DatabaseVPS.stopConsole')
    @patch('modules.database.DatabaseVPS.stopCommand')
    @patch('modules.database.DatabaseVPS.startCommand')
    @patch('modules.database.DatabaseVPS.get_vps_details')
    @patch('modules.vps.VMFunc.execbhyve')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_start(
            self,
            exec_function_dbconnect,
            exec_function_checkSecurity,
            exec_function_execbhyve,
            exec_function_get_vps_details,
            exec_function_startCommand,
            exec_function_stopCommand,
            exec_function_stopConsole):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        # Starting a VPS
        modules.database.DatabaseVPS.get_vps_details.return_value = '1'
        modules.database.DatabaseVPS.startCommand.return_value = '/usr/bin/sh this command'

        modules.vps.VMFunc.execbhyve.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,start")
        assert vpsConn.executeCommand() == 'Started VPS 1\n'


    #
    # Stopping a VPS
    #
    @patch('modules.database.DatabaseVPS')
    @patch('modules.database.DatabaseVPS.stopConsole')
    @patch('modules.database.DatabaseVPS.stopCommand')
    @patch('modules.database.DatabaseVPS.get_vps_details')
    @patch('modules.vps.VMFunc.execbhyve')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_stop(
            self,
            exec_function_dbconnect,
            exec_function_checkSecurity,
            exec_function_execbhyve,
            exec_function_get_vps_details,
            exec_function_stopCommand,
            exec_function_stopConsole):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        # Stopping a VPS
        modules.database.DatabaseVPS.get_vps_details.return_value = '1'
        modules.database.DatabaseVPS.stopCommand.return_value = '/usr/bin/sh this command'
        modules.database.DatabaseVPS.stopConsole.return_value = '/usr/bin/sh this command'

        modules.vps.VMFunc.execbhyve.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,stop")
        assert vpsConn.executeCommand() == 'Stopped VPS 1\n'


class TestCreate(unittest.TestCase):

    #
    # Creating a VPS
    #
    @patch('modules.database.DatabaseVPS.getDevices')
    @patch('modules.database.DatabaseVPS.getDisks')
    @patch('modules.database.DatabaseVPS.getStopScript')
    @patch('modules.database.DatabaseVPS.getStartScript')
    @patch('modules.database.DatabaseVPS.getPath')
    @patch('modules.database.DatabaseVPS.getImage')
    @patch('modules.database.DatabaseVPS.getConsole')
    @patch('modules.database.DatabaseVPS.getRAM')
    @patch('modules.database.DatabaseVPS.getName')
    @patch('modules.database.DatabaseVPS.getID')
    @patch('modules.database.DatabaseVPS.get_vps_details')
    @patch('modules.database.DatabaseVPS')
    @patch('os.path.exists')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_createvps(
            self,
            exec_function_checkSecurity,
            exec_function_ospathexists,
            exec_function_dbconnect,
            exec_function_get_vps_details,
            exec_function_getid,
            exec_function_getName,
            exec_function_getRAM,
            exec_function_getConsole,
            exec_function_getImage,
            exec_function_getPath,
            exec_function_getStartScript,
            exec_function_getStopScript,
            exec_function_getDisks,
            exec_function_getDevices):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        modules.database.DatabaseVPS().get_vps_details.return_value = ''
        modules.database.DatabaseVPS().get_vps_id.return_value = '1'
        modules.database.DatabaseVPS().get_vps_name.return_value = 'MyTestVPS'
        modules.database.DatabaseVPS().get_vps_memory.return_value = '512'
        modules.database.DatabaseVPS().getConsole.return_value = 1
        modules.database.DatabaseVPS().getImage.return_value = 1
        modules.database.DatabaseVPS().getPath.return_value = '/Users/ben/repos/vpssvr'
        modules.database.DatabaseVPS().getStartScript.return_value = '/home/startme.sh'
        modules.database.DatabaseVPS().getStopScript.return_value = '/home/stopme.sh'
        #modules.database.DatabaseVPS().getDisks.return_value = [1]
        #modules.database.DatabaseVPS().getDevices.return_value = [1,3]

        os.path.exists('/Users/ben/repos/vpssvr').return_value = ''

        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,createvps")
        assert vpsConn.executeCommand() == 'Created VPS: 1\n'

    def altPOpen(self):
        return None

    @patch('modules.database.DatabaseVPS.getImage')
    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_creatediskimg(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript,
            getImageMock):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'

        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_genscript.return_value = 1

        exec_function_subprocess_Popen.return_value = process_mock


        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,createdisk")
        assert vpsConn.executeCommand() == 'Create Disk for VPS 1\n'


class TestDelete(unittest.TestCase):

    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_deletediskimg_success(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)
        exec_function_subprocess_Popen.return_value = process_mock

        exec_function_genscript.return_value = None

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,deletedisk")

        assert vpsConn.executeCommand() == 'Disk 1 Delete\n'


    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_deletediskimg_fail_on_script_creation(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)
        exec_function_subprocess_Popen.return_value = process_mock

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,deletedisk")

        assert vpsConn.executeCommand() == 'An error occurred generating script'

    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_deletediskimg_fail_on_delete(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error')}
        process_mock.configure_mock(**attrs)


        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)

        exec_function_subprocess_Popen.return_value = -1

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,deletedisk")

        assert vpsConn.executeCommand() == 'Delete disk failed'

    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_deletediskimg_fail_on_image(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None
        exec_function_dbconnect().getImage.return_value = 999
        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)

        exec_function_subprocess_Popen.return_value = process_mock

        exec_function_genscript.return_value = None

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,deletedisk")
        exec_function_dbconnect().getImage.return_value = 999

        assert vpsConn.executeCommand() == 'Error: no image found'

    @patch('os.path.exists')
    @patch('os.rename')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_delete(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_os_rename,
            exec_function_os_path_exists):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None
        exec_function_dbconnect().getImage.return_value = 999
        exec_function_os_rename.return_value = process_mock
        exec_function_os_path_exists.return_value = process_mock
        exec_function_dbconnect().get_disk.return_value = (1, 1, 3)


        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,delete")

        assert vpsConn.executeCommand() == None


class TestConsole(unittest.TestCase):

    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_restartConsole(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        exec_function_subprocess_Popen.return_value = process_mock

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,restartConsole")

        assert vpsConn.executeCommand() == "Terminal Restarted\n"


class TestUpdateVPS(unittest.TestCase):


    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_success(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        modules.database.DatabaseVPS.get_vps_details.return_value = ''
        modules.database.DatabaseVPS.get_vps_id.return_value = '1'
        modules.database.DatabaseVPS.get_vps_name.return_value = 'MyTestVPS'
        modules.database.DatabaseVPS.get_vps_memory.return_value = '512'
        modules.database.DatabaseVPS.getConsole.return_value = '1'
        modules.database.DatabaseVPS.getStartScript.return_value = '/home/startme.sh'
        modules.database.DatabaseVPS.getStopScript.return_value = '/home/stopme.sh'
        modules.database.DatabaseVPS.get_disks_details_from_database.return_value = '234'
        modules.database.DatabaseVPS.get_devices.return_value = '1'

        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/usr/mypath'

        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_genscript.return_value = None


        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,updatevps")

        assert vpsConn.executeCommand() == 'VPS 1 Update\n'


    @patch('modules.vps.VMFunc.generateScript')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_error(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen,
            exec_function_genscript):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        modules.database.DatabaseVPS.get_vps_details.return_value = ''
        modules.database.DatabaseVPS.get_vps_id.return_value = '1'
        modules.database.DatabaseVPS.get_vps_name.return_value = 'MyTestVPS'
        modules.database.DatabaseVPS.get_vps_memory.return_value = '512'
        modules.database.DatabaseVPS.getConsole.return_value = '1'
        modules.database.DatabaseVPS.getStartScript.return_value = '/home/startme.sh'
        modules.database.DatabaseVPS.getStopScript.return_value = '/home/stopme.sh'
        modules.database.DatabaseVPS.get_disks_details_from_database.return_value = '234'
        modules.database.DatabaseVPS.get_devices.return_value = '1'

        exec_function_dbconnect().getImage.return_value = 0
        exec_function_dbconnect().getPath.return_value = '/usr/mypath'

        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_genscript.return_value = None


        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,updatevps")

        assert vpsConn.executeCommand() == 'Error: no image specified'


class TestSnapShots(unittest.TestCase):
    @patch('mysql.connector')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_takeSnapshot(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_connect):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        snapshotReturnValue = "Snapshot name = " + str(time.time())

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,takeSnapshot")

        assert vpsConn.executeCommand() == snapshotReturnValue

    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_listSnapshot(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('my snapshot list', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        exec_function_subprocess_Popen.return_value = process_mock

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,listSnapshot")

        assert vpsConn.executeCommand() == 'my snapshot list'

    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_restoreSnapshot(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('Snapshot Restored', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        exec_function_subprocess_Popen.return_value = process_mock

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,restoreSnapshot")

        assert vpsConn.executeCommand() == 'Snapshot Restored'


    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.checkSecurity')
    def test_executeCommand_updateVPS_removeSnapshot(
            self,
            exec_function_checkSecurity,
            exec_function_dbconnect,
            exec_function_subprocess_Popen):

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('Snapshot Removed', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_checkSecurity.return_value = 'Pass'
        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        exec_function_subprocess_Popen.return_value = process_mock

        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,removeSnapshot")

        assert vpsConn.executeCommand() == 'Snapshot Removed'


class TestNetwork(unittest.TestCase):

    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.execcmd')
    def test_stopNetwork(self, exec_function_dbconnect, exec_function):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        vpsConn = modules.vps.VMFunc("1234,1,status\n")

        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'


    @patch('modules.database.DatabaseVPS')
    @patch('modules.vps.VMFunc.execcmd')
    def test_get_status(self, exec_function_dbconnect, exec_function):

        modules.database.DatabaseVPS.mysql.connector.connect.return_value = None

        vpsConn = modules.vps.VMFunc("1234,1,status\n")

        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'

        modules.vps.VMFunc.execcmd.return_value = ''
        assert vpsConn.getNetStatus(1) == 'DOWN'


if __name__ == '__main__':
    unittest.main()
