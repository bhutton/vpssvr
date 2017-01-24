import unittest
import os
import mock
import modules.database
import modules.vps


class TestStatus(unittest.TestCase):
    
    # See what happens if an invalid password is used
    def test_checkSecurity(self):
        
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
        assert vpsConn.executeCommand() == "Connection Failed"
    
    
    
    # Test NetStatus Module via the Execute Command control function
    @mock.patch('modules.database.DB_VPS')
    @mock.patch('modules.vps.VMFunc.execcmd')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_netStatus(
            self, 
            exec_function_dbconnect,
            exec_function_checkSecurity, 
            exec_function_execcmd):
        
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
        
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
    
    
    
    
    #
    # Starting a VPS
    #
    @mock.patch('modules.database.DB_VPS')
    @mock.patch('modules.database.DB_VPS.stopConsole')
    @mock.patch('modules.database.DB_VPS.stopCommand')
    @mock.patch('modules.database.DB_VPS.startCommand')
    @mock.patch('modules.database.DB_VPS.getVPS')
    @mock.patch('modules.vps.VMFunc.execbhyve')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_start(
            self, 
            exec_function_dbconnect,
            exec_function_checkSecurity, 
            exec_function_execbhyve, 
            exec_function_getvps,
            exec_function_startCommand,
            exec_function_stopCommand,
            exec_function_stopConsole):
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
    
        # Starting a VPS
        modules.database.DB_VPS.getVPS.return_value = '1'
        modules.database.DB_VPS.startCommand.return_value = '/usr/bin/sh this command'
        
        modules.vps.VMFunc.execbhyve.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,start")
        assert vpsConn.executeCommand() == 'Started VPS 1\n'
    
    
    
    
    #
    # Stopping a VPS
    #
    @mock.patch('modules.database.DB_VPS')
    @mock.patch('modules.database.DB_VPS.stopConsole')
    @mock.patch('modules.database.DB_VPS.stopCommand')
    @mock.patch('modules.database.DB_VPS.getVPS')
    @mock.patch('modules.vps.VMFunc.execbhyve')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_stop(
            self, 
            exec_function_dbconnect,
            exec_function_checkSecurity, 
            exec_function_execbhyve, 
            exec_function_getvps,
            exec_function_stopCommand,
            exec_function_stopConsole):
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
        
        # Stopping a VPS
        modules.database.DB_VPS.getVPS.return_value = '1'
        modules.database.DB_VPS.stopCommand.return_value = '/usr/bin/sh this command'
        modules.database.DB_VPS.stopConsole.return_value = '/usr/bin/sh this command'
        
        modules.vps.VMFunc.execbhyve.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,stop")
        assert vpsConn.executeCommand() == 'Stopped VPS 1\n'
    
    
    
    
    #
    # Creating a VPS
    #
    @mock.patch('modules.database.DB_VPS.getDevices')
    @mock.patch('modules.database.DB_VPS.getDisks')
    @mock.patch('modules.database.DB_VPS.getStopScript')
    @mock.patch('modules.database.DB_VPS.getStartScript')
    @mock.patch('modules.database.DB_VPS.getPath')
    @mock.patch('modules.database.DB_VPS.getImage')
    @mock.patch('modules.database.DB_VPS.getConsole')
    @mock.patch('modules.database.DB_VPS.getRAM')
    @mock.patch('modules.database.DB_VPS.getName')
    @mock.patch('modules.database.DB_VPS.getID')
    @mock.patch('modules.database.DB_VPS.getVPS')
    @mock.patch('modules.database.DB_VPS')
    @mock.patch('os.path.exists')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_createvps(
            self, 
            exec_function_dbconnect,
            exec_function_ospathexists,
            exec_function_checkSecurity, 
            exec_function_getvps,
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
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
        
        # Stopping a VPS
        modules.database.DB_VPS.getVPS.return_value = ''
        modules.database.DB_VPS.getID.return_value = '1'
        modules.database.DB_VPS.getName.return_value = 'MyTestVPS'
        modules.database.DB_VPS.getRAM.return_value = '512'
        modules.database.DB_VPS.getConsole.return_value = '1'
        modules.database.DB_VPS.getImage.return_value = '1'
        modules.database.DB_VPS.getPath.return_value = '/Users/ben/repos/vpssvr'
        modules.database.DB_VPS.getStartScript.return_value = '/home/startme.sh'
        modules.database.DB_VPS.getStopScript.return_value = '/home/stopme.sh'
        modules.database.DB_VPS.getDisks.return_value = '234'
        modules.database.DB_VPS.getDevices.return_value = '1'
        
        modules.database.DB_VPS.getDevices.return_value = '1'
        
        os.path.exists('/Users/ben/repos/vpssvr').return_value = ''
        
        
        
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        #modules.vps.VMFunc.getID.return_value = '1'
        
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,createvps")
        assert vpsConn.executeCommand() == 'Created VPS: 1\n'
        
    
    def test_executeCommand_createdisk(self):
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,createdisk")
        assert vpsConn.executeCommand() == 'Create Disk for VPS 1\n'
        

    @mock.patch('modules.database.DB_VPS')
    @mock.patch('modules.vps.VMFunc.execcmd')    
    def test_get_status(self, exec_function_dbconnect, exec_function):
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
        
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
                       
        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'
        
        modules.vps.VMFunc.execcmd.return_value = ''
        assert vpsConn.getNetStatus(1) == 'DOWN'
    
    @mock.patch('modules.database.DB_VPS')    
    @mock.patch('modules.vps.VMFunc.execcmd')
    def test_stopNetwork(self, exec_function_dbconnect, exec_function):
        
        modules.database.DB_VPS.mysql.connector.connect.return_value = None
        
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'
        
    