import os
import vpsserver
import unittest
import tempfile
import base64
import modules.database as database
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

    @patch('modules.vps.VMFunctions.execute_command')
    @patch('os.path.exists')
    def test_get_status(self,
            exec_function_ospathexists,
            exec_function):

        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''
        exec_function.return_value = 'tap112: flags=8943<UP,BROADCAST,RUNNING,PROMISC,SIMPLEX,MULTICAST> metric 0 mtu 1500'

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_ospathexists('/dev/vmm/1').return_value = process_mock

        d = database.DatabaseVPS()

        d.create_vps_in_database(878,'test','mytest',512,1,1,'mypath','start','stop')

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/status/878',
                                 'GET','miguel','python')
        assert b'Running' in rv.data

    @patch('os.path.exists')
    @patch('subprocess.Popen')
    def test_start_vps(self,
                       exec_function_subprocess_Popen,
                       exec_function_ospathexists):
        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_ospathexists.return_value = process_mock
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/start/878',
                                 'GET', 'miguel', 'python')

        assert b'Started VPS 878' in rv.data

    @patch('os.path.exists')
    @patch('subprocess.Popen')
    def test_stop_vps(self,
                      exec_function_subprocess_Popen,
                      exec_function_ospathexists):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)

        exec_function_subprocess_Popen.return_value = process_mock
        exec_function_ospathexists.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/stop/878',
                                 'GET', 'miguel', 'python')
        assert b'Stopped' in rv.data

    @patch('os.path.exists')
    def test_create_vps(self, exec_function_ospathexists):
        exec_function_ospathexists('/Users/ben/repos/vpssvr').return_value = ''

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createvps/878',
                                 'GET', 'miguel', 'python')
        assert b'Created' in rv.data

    @patch('os.path.exists')
    def test_create_disk(self, exec_function_ospathexists):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)
        exec_function_ospathexists.return_value = process_mock

        d = database.DatabaseVPS()
        d.create_disk_in_database(878, 'mydisk', 1, 20, 878)
        d.create_disk_in_database(879, 'mydisk', 1, 20, 878)

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createdisk/878',
                                 'GET', 'miguel', 'python')
        assert b'Create Disk for VPS 878' in rv.data

    @patch('subprocess.Popen')
    def test_delete_disk(self, exec_function_fileopen):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'success')}
        process_mock.configure_mock(**attrs)
        exec_function_fileopen.return_value = process_mock

        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/deletedisk/878',
                                 'GET', 'miguel', 'python')
        assert b'Disk 878 Delete' in rv.data


    def test_delete(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/delete/878',
                                 'GET', 'miguel', 'python')
        assert b'null' in rv.data

    def test_restart_console(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/restartConsole/878',
                                 'GET', 'miguel', 'python')
        assert b'Terminal Restarted' in rv.data

    def test_update_vps(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/updatevps/878',
                                 'GET', 'miguel', 'python')
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
