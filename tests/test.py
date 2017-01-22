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
    @mock.patch('modules.vps.VMFunc.execcmd')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_netStatus(self, exec_function_checkSecurity, exec_function_execcmd):
        
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
    
    
    @mock.patch('modules.database.DB_VPS.startCommand')
    @mock.patch('modules.database.DB_VPS.getVPS')
    @mock.patch('modules.vps.VMFunc.execbhyve')
    @mock.patch('modules.vps.VMFunc.checkSecurity')  
    def test_executeCommand_start(
            self, 
            exec_function_checkSecurity, 
            exec_function_execbhyve, 
            exec_function_getvps,
            exec_function_startCommand):
    
        # Check starting a VPS
        modules.database.DB_VPS.getVPS.return_value = '1'
        modules.database.DB_VPS.startCommand.return_value = '/usr/bin/sh this command'
        modules.vps.VMFunc.execbhyve.return_value = ''
        modules.vps.VMFunc.checkSecurity.return_value = 'Pass'
        
        vpsConn = modules.vps.VMFunc("vdsoiu543um89dsf89y7895y7327@#@#--0934589,1,start")
        assert vpsConn.executeCommand() == 'Started VPS 1\n'
        

    @mock.patch('modules.vps.VMFunc.execcmd')    
    def test_get_status(self, exec_function):
        
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
                       
        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'
        
        modules.vps.VMFunc.execcmd.return_value = ''
        assert vpsConn.getNetStatus(1) == 'DOWN'
        
    @mock.patch('modules.vps.VMFunc.execcmd')
    def test_stopNetwork(self, exec_function):
        
        vpsConn = modules.vps.VMFunc("1234,1,status\n")
        modules.vps.VMFunc.execcmd.return_value = 'tap111: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'
        assert vpsConn.getNetStatus(1) == 'UP'
        
    