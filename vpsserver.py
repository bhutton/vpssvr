#!virtualenv/bin/python

from flask import Flask, jsonify, abort, make_response
from flask.ext.httpauth import HTTPBasicAuth
import modules.vps as vps

auth = HTTPBasicAuth()

app = Flask(__name__)

description = 'this description'

tasks = [
    {
        'id': 1,
        'name': u'server #1',
        'description': description,
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/vpssvr/api/v1.0/tasks/status/<int:vps_id>', methods=['GET'])
@auth.login_required
def get_status(vps_id):

    v = vps.VMFunc(878)
    status = get_status(vps_id)



#def get_task(task_id):
#    task = [task for task in tasks if task['id'] == task_id]
#    if len(task) == 0:
#        abort(404)
#    return jsonify({'task': task[0]})

if __name__ == '__main__':
    app.run(debug=True)