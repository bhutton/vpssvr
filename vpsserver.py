#!virtualenv/bin/python

from flask import Flask, jsonify, abort, make_response
from flask import Flask, render_template, json, request, redirect, session, g

from flask_httpauth import HTTPBasicAuth
import modules.vps as vps
from sqlite3 import dbapi2 as sqlite3

auth = HTTPBasicAuth()

app = Flask(__name__)

description = 'this description'

v = vps.VMFunc()

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
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
    v = vps.VMFunc()
    v.checkStatus(vps_id)
    status = v.getStatus()
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/start/<int:vps_id>', methods=['GET'])
@auth.login_required
def start_vps(vps_id):
    v = vps.VMFunc()
    status = v.start(vps_id)
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/stop/<int:vps_id>', methods=['GET'])
@auth.login_required
def stop_vps(vps_id):
    v = vps.VMFunc()
    status = v.stop(vps_id)
    return jsonify({'status': status})

@app.route('/vpssvr/api/v1.0/tasks/createvps/<int:vps_id>', methods=['GET'])
@auth.login_required
def create_vps(vps_id):
    return jsonify({'status': v.createvps(vps_id)})


@app.route('/vpssvr/api/v1.0/tasks/createdisk/<int:vps_id>', methods=['GET'])
@auth.login_required
def create_disk(vps_id):
    return jsonify({'status': v.createDiskImg(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/deletedisk/<int:vps_id>', methods=['GET'])
@auth.login_required
def delete_disk(vps_id):
    return jsonify({'status': v.deleteDisk(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/delete/<int:vps_id>', methods=['GET'])
@auth.login_required
def delete(vps_id):
    return jsonify({'status': v.delete(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/restartConsole/<int:vps_id>', methods=['GET'])
@auth.login_required
def restart_console(vps_id):
    return jsonify({'status': v.restartConsole(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/updatevps/<int:vps_id>', methods=['GET'])
@auth.login_required
def updatevps(vps_id):
    return jsonify({'status': v.updateVPS(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/takeSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def take_snapshot(vps_id):
    return jsonify({'status': v.takeSnapshot(vps_id,'')})

@app.route('/vpssvr/api/v1.0/tasks/listSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def list_snapshot(vps_id):
    return jsonify({'status': v.listSnapshot(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/restoreSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def restore_snapshot(vps_id):
    return jsonify({'status': v.restoreSnapshot(vps_id,'')})

@app.route('/vpssvr/api/v1.0/tasks/removeSnapshot/<int:vps_id>', methods=['GET'])
@auth.login_required
def remove_snapshot(vps_id):
    return jsonify({'status': v.removeSnapshot(vps_id,'')})

@app.route('/vpssvr/api/v1.0/tasks/netStatus/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_network_status(vps_id):
    return jsonify({'status': v.getNetStatus(vps_id)})

@app.route('/vpssvr/api/v1.0/tasks/netStop/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_stop_network(vps_id):
    return jsonify({'status': v.stopNetwork(vps_id).decode('utf-8')})

@app.route('/vpssvr/api/v1.0/tasks/netStart/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_start_network(vps_id):
    return jsonify({'status': v.startNetwork(vps_id).decode('utf-8')})

if __name__ == '__main__':
    app.run(debug=True)