import os
import vpsserver
import unittest
import tempfile
import base64
import modules.database as database
#import json
#from flask import Flask, jsonify, abort, make_response
#from flask import appcontext_pushed, g
from mock import patch
import mock

dir_path = os.path.dirname(os.path.realpath(__file__))

class VPSServerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, vpsserver.app.config['DATABASE'] = tempfile.mkstemp()
        vpsserver.app.config['TESTING'] = True
        self.app = vpsserver.app.test_client()
        with vpsserver.app.app_context():
            vpsserver.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(vpsserver.app.config['DATABASE'])
        except:
            print('cannot remove')

    def open_with_auth(self, url, method, username, password):
        headers = {
            'Authorization': 'Basic %s' % base64.b64encode(b"miguel:python").decode("ascii")
        }
        return self.app.get(url, headers=headers)

    def test_unauthorised_access(self):
        rv = self.app.get('/vpssvr/api/v1.0/tasks/status/878')
        assert b'Unauthorized' in rv.data

    @patch('modules.vps.VMFunc.execcmd')
    #@patch('modules.database.DatabaseVPS')
    @patch('os.path.exists')
    def test_get_status(self,
            exec_function_ospathexists,
            #exec_function_dbconnect,
            exec_function):
        '''exec_function_dbconnect.return_value.get_vps_details.return_value = [1,2,3,4,5,6,7,8]
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'
        '''
        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''
        exec_function.return_value = 'tap112: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_ospathexists('/dev/vmm/1').return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/status/878',
                                 'GET','miguel','python')
        assert b'Running' in rv.data

    @patch('os.path.exists')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_start_vps(self,
                       #mysql_connector,
                       exec_function_dbconnect,
                       exec_function_subprocess_Popen,
                       exec_function_ospathexists):
        #mysql_connector.return_value.connect.return_value = None
        exec_function_dbconnect().get_vps_details.return_value = ''
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'
        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        # exec_function_ospathexists('/zroot/vm/vpsman-dev/878/').return_value = process_mock
        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_ospathexists.return_value = process_mock
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/start/878',
                                 'GET', 'miguel', 'python')

        assert b'Started VPS 878' in rv.data

    @patch('os.path.exists')
    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_stop_vps(self,
               #mysql_connector,
                      exec_function_dbconnect,
               exec_function_subprocess_Popen,
               exec_function_ospathexists):
        exec_function_dbconnect().get_vps_details.return_value = ''
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        # exec_function_ospathexists('/zroot/vm/vpsman-dev/878/').return_value = process_mock
        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_ospathexists.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/stop/878',
                                 'GET', 'miguel', 'python')
        assert b'Stopped' in rv.data

    @patch('os.path.exists')
    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_create_vps(self,
                        #mysql_connector,
                        exec_function_dbconnect,
                        exec_function_ospathexists):
        #mysql_connector.return_value.connect.return_value = None
        exec_function_dbconnect().get_vps_details.return_value = ''
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'
        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createvps/878',
                                 'GET', 'miguel', 'python')
        assert b'Created' in rv.data

    @patch('os.path.exists')
    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_create_disk(self,
                         #mysql_connector,
                         exec_function_dbconnect,
                         exec_function_ospathexists):
        #mysql_connector.return_value.connect.return_value = None
        exec_function_dbconnect().get_vps_details.return_value = ''
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_disk.return_value = [1,1,3,4]
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_ospathexists.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createdisk/878',
                                 'GET', 'miguel', 'python')
        assert b'Create Disk for VPS 1' in rv.data

    @patch('subprocess.Popen')
    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_delete_disk(self,
                         #mysql_connector,
                         exec_function_dbconnect,
                         exec_function_fileopen):

        exec_function_dbconnect().get_disk.return_value = [1, 1, 3, 4]
        exec_function_dbconnect().getPath.return_value = \
            dir_path + '/../../vpsman-dev'

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_fileopen.return_value = process_mock

        #mysql_connector.return_value.connect.return_value = None
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/deletedisk/878',
                                 'GET', 'miguel', 'python')
        print(rv.data)
        assert b'Disk 878 Delete' in rv.data

    #@patch('flaskext.mysql.MySQL.connect')
    def test_delete_disk_no_image_found(self
                                        #,mysql_connector
                                        ):
        #mysql_connector.return_value.connect.return_value = None

        d = database.DatabaseVPS()
        d.create_disk_in_database(878,'mydisk',1,20,878)

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/deletedisk/878',
                                 'GET', 'miguel', 'python')
        assert(b'An error occurred generating script' in rv.data)

    def test_delete(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/delete/878',
                                 'GET', 'miguel', 'python')
        assert b'null' in rv.data

    def test_restart_console(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/restartConsole/878',
                                 'GET', 'miguel', 'python')
        assert b'Terminal Restarted' in rv.data

    @patch('modules.database.DatabaseVPS')
    #@patch('flaskext.mysql.MySQL.connect')
    def test_update_vps(self,
                        #mysql_connector,
                        exec_function_dbconnect):
        #mysql_connector.return_value.connect.return_value = None
        exec_function_dbconnect().get_vps_details.return_value = ''
        exec_function_dbconnect().get_vps_id.return_value = '1'
        exec_function_dbconnect().get_disk.return_value = [1, 1, 3, 4]
        exec_function_dbconnect().get_vps_name.return_value = 'MyTestVPS'
        exec_function_dbconnect().get_vps_memory.return_value = '512'
        exec_function_dbconnect().getConsole.return_value = 1
        exec_function_dbconnect().getImage.return_value = 1
        exec_function_dbconnect().getPath.return_value = '/Users/ben/repos/vpssvr'
        exec_function_dbconnect().getStartScript.return_value = '/home/startme.sh'
        exec_function_dbconnect().getStopScript.return_value = '/home/stopme.sh'

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/updatevps/878',
                                 'GET', 'miguel', 'python')
        print(rv.data)
        assert b'VPS 878 Updated' in rv.data

    def test_take_snapshot(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/takeSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot name' in rv.data

    @patch('subprocess.Popen')
    def test_list_snapshot(self, exec_function_popen):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('Snapshot name', 'success')}
        process_mock.configure_mock(**attrs)
        exec_function_popen.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/listSnapshot/878',
                                 'GET', 'miguel', 'python')

        assert b'Snapshot name' in rv.data

    @patch('subprocess.Popen')
    def test_restore_snapshot(self, exec_function_popen):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('Snapshot name', 'success')}
        process_mock.configure_mock(**attrs)
        exec_function_popen.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/restoreSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot name' in rv.data

    def test_remove_snapshot(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/removeSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot Removed' in rv.data

    def test_get_network_status(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/netStatus/878',
                                 'GET', 'miguel', 'python')
        assert b'UP' in rv.data

    def test_stop_network(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/netStop/878',
                                 'GET', 'miguel', 'python')
        assert b'ifconfig' in rv.data

    def test_start_network(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/netStart/878',
                                 'GET', 'miguel', 'python')
        assert b'ifconfig' in rv.data



if __name__ == '__main__':
    unittest.main()
