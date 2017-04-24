#!/usr/local/bin/python

import mysql.connector
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

    def get_ip_address(self):
        self.ip = ni.ifaddresses('en0')[2][0]['addr']


    def return_ip_address(self):
        return self.ip

    def create_database_entry(self):
        sql_query = "update vps set ip=%s where id=%s"
        id = 878

        cnx = mysql.connector.connect(**self.config)
        cursor = cnx.cursor()

        cursor.execute(sql_query, (id,))

g = GetDetails()
g.get_ip_address()