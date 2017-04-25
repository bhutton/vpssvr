#!/usr/local/bin/python

import mysql.connector
import sys
import netifaces as ni


class GetDetails:

    ip = ''
    config = {
        'user': 'ah_vps',
        'password': 'Mnie7865sh',
        'host': 'mysql',
        'database': 'ah_vps_dev',
        'raise_on_warnings': True,
    }

    def __init__(self):
        self.cnx = mysql.connector.connect(**self.config)
        self.cursor = self.cnx.cursor()

    def __del__(self):
        self.cnx.commit()
        self.cnx.close()

    def get_ip_address(self):
        self.ip = ni.ifaddresses('en0')[2][0]['addr']


    def return_ip_address(self):
        return self.ip

    def create_database_entry(self, id):
        sql_query = "update vps set ip=%s where id=%s"

        self.cursor.execute(sql_query, (self.ip, id,))


try:
    vps_id = sys.argv[1]
except:
    vps_id = ''

g = GetDetails()
g.get_ip_address()
g.create_database_entry(vps_id)