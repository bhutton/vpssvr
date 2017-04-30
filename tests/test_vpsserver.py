import os
import vpsserver
import unittest
import tempfile
import base64
import json
from flask import Flask, jsonify, abort, make_response
from flask import appcontext_pushed, g


class VPSServerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, vpsserver.app.config['DATABASE'] = tempfile.mkstemp()
        vpsserver.app.config['TESTING'] = True
        self.app = vpsserver.app.test_client()
        with vpsserver.app.app_context():
            vpsserver.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(vpsserver.app.config['DATABASE'])

    def open_with_auth(self, url, method, username, password):
        return self.app.open(url,
             method=method,
             headers={
                 'Authorization': 'Basic ' + base64.b64encode(username + \
                                                              ":" + password)
             }
         )

    def test_unauthorised_access(self):
        rv = self.app.get('/vpssvr/api/v1.0/tasks/status/878')
        assert b'Unauthorized' in rv.data

    def test_get_status(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/status/878',
                                 'GET','miguel','python')
        assert b'Stopped' in rv.data

    def test_start_vps(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/start/878',
                                 'GET', 'miguel', 'python')
        assert b'Started' in rv.data

    def test_stop_vps(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/stop/878',
                                 'GET', 'miguel', 'python')
        assert b'Stopped' in rv.data

    def test_create_vps(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createvps/878',
                                 'GET', 'miguel', 'python')
        assert b'Created' in rv.data

    '''def test_create_disk(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/createdisk/878',
                                 'GET', 'miguel', 'python')
        assert b'Created' in rv.data'''

    '''def test_delete_disk(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/deletedisk/878',
                                 'GET', 'miguel', 'python')
        print rv.data
        assert b'Deleted' in rv.data'''

    def test_delete(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/delete/878',
                                 'GET', 'miguel', 'python')
        assert b'null' in rv.data

    def test_restart_console(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/restartConsole/878',
                                 'GET', 'miguel', 'python')
        assert b'Terminal Restarted' in rv.data

    def test_updatevps(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/updatevps/878',
                                 'GET', 'miguel', 'python')
        assert b'VPS 878 Updated' in rv.data

    def test_take_snapshot(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/takeSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot name' in rv.data

    '''def test_list_snapshot(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/listSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot name' in rv.data'''

    '''def test_restore_snapshot(self):
        rv = self.open_with_auth('/vpssvr/api/v1.0/tasks/restoreSnapshot/878',
                                 'GET', 'miguel', 'python')
        assert b'Snapshot name' in rv.data'''

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
