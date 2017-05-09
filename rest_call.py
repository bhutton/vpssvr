#Python 2.7.6
#RestfulClient.py

#import requests
from flask_httpauth import HTTPBasicAuth
import base64
import json
import requests

class TestRest:
    def open_with_auth(self, url, method, username, password):
        headers = {
            'Authorization': 'Basic %s' % base64.b64encode(b"miguel:python").decode("ascii")
        }
        return requests.get(url, headers=headers)

    def unauthorised_access(self):
        rv = self.open_with_auth('http://localhost:5000/vpssvr/api/v1.0/tasks/statustest/1',
                          'GET', 'miguel', 'python')
        print(rv.json())


r = TestRest()
r.unauthorised_access()
