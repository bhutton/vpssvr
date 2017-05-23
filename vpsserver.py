#!virtualenv/bin/python

import configparser, os
from flask import Flask, jsonify, make_response, g
from flask_httpauth import HTTPBasicAuth
import modules.vps as vps
from sqlite3 import dbapi2 as sqlite3

auth = HTTPBasicAuth()
app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
vps_configuration = configparser.ConfigParser()
vps_configuration.read("{}/configuration.cfg".format(dir_path))

host_address = vps_configuration.get('Global', 'HOST')
debug_status = vps_configuration.get('Global', 'DEBUG')
server_port = int(vps_configuration.get('Global', 'PORT'))

v = vps.VMFunctions()

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/vpssvr/api/v1.0/tasks/statustest/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_status_test(vps_id):
    return jsonify({'status': 'Running'})


@app.route('/vpssvr/api/v1.0/tasks/status/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_status(vps_id):
    v = vps.VMFunctions()
    v.check_vps_status(vps_id)
    status = v.get_status()
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/start/<int:vps_id>', methods=['GET'])
@auth.login_required
def start_vps(vps_id):
    v = vps.VMFunctions()
    status = v.start_vps(vps_id)
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/stop/<int:vps_id>', methods=['GET'])
@auth.login_required
def stop_vps(vps_id):
    v = vps.VMFunctions()
    status = v.stop_vps(vps_id)
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/createvps/<int:vps_id>', methods=['GET'])
@auth.login_required
def create_vps(vps_id):
    return jsonify({'status': v.create_vps(vps_id)})


@app.route('/vpssvr/api/v1.0/tasks/createdisk/<int:vps_id>', methods=['GET'])
@auth.login_required
def create_disk(vps_id):
    return jsonify({'status': v.create_disk_image(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/deletedisk/<int:vps_id>', methods=['GET'])
@auth.login_required
def delete_disk(vps_id):
    return jsonify({'status': v.delete_disk(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/delete/<int:vps_id>', methods=['GET'])
@auth.login_required
def delete(vps_id):
    return jsonify({'status': v.delete_vps(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/restartConsole/<int:vps_id>', methods=['GET'])
@auth.login_required
def restart_console(vps_id):
    return jsonify({'status': v.restart_console(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/updatevps/<int:vps_id>', methods=['GET'])
@auth.login_required
def updatevps(vps_id):
    return jsonify({'status': v.update_vps(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/takeSnapshot/<int:vps_id>/<string:snapshot_name>', methods=['GET'])
@auth.login_required
def take_snapshot(vps_id,snapshot_name):
    return jsonify({'status': v.take_snapshot_of_vps(vps_id,snapshot_name)})

@app.route('/vpssvr/api/v1.0/tasks/listSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def list_snapshot(vps_id):
    return jsonify({'status': v.list_snapshots(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/restoreSnapshot/<int:vps_id>/<string:snapshot_name>', methods=['GET'])
@auth.login_required
def restore_snapshot(vps_id,snapshot_name):
    return jsonify({'status': v.restore_snapshot(vps_id,snapshot_name)})

@app.route('/vpssvr/api/v1.0/tasks/removeSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def remove_snapshot(vps_id):
    return jsonify({'status': v.remove_snapshot(vps_id,'')})

@app.route('/vpssvr/api/v1.0/tasks/netStatus/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_network_status(vps_id):
    return jsonify({'status': v.get_network_status(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/netStop/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_stop_network(vps_id):
    return jsonify({'status': v.stop_network(vps_id).decode('utf-8')})

@app.route('/vpssvr/api/v1.0/tasks/netStart/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_start_network(vps_id):
    return jsonify({'status': v.start_network(vps_id).decode('utf-8')})

if __name__ == '__main__':
    app.run(debug=debug_status, host=host_address, port=server_port)