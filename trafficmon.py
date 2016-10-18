#!/usr/bin/env python

"""
Use Netstat to monitor traffic

"""

import subprocess
import mysql.connector
import database
import time

config = {
  'user': 'ah_vps',
  'password': 'Mnie7865sh',
  'host': 'mysql',
  'database': 'ah_vps_dev',
  'raise_on_warnings': True,
}

add_traffic = ("INSERT INTO traffic "
               "(interface, LastIpkts, LastOpkts, TotalIpkts, TotalOpkts,timestamp) "
               "VALUES (%s, %s, %s, %s, %s, %s)")

last_timezone = ("select max(timestamp) from `traffic` where `interface`=%s")

netstat_cmd	= "/usr/bin/netstat"
args = "-b -I"

network = database.DB_Network()
tunnel = network.getInt()

for interface in tunnel:

    interface = 'tap' + str(interface[0])

    print interface

    command     = netstat_cmd + ' ' + args + ' ' + interface

    proc = subprocess.Popen(['/bin/sh', '-c', command], stdout=subprocess.PIPE)

    # Process output of netstat command
    for line in proc.stdout.readlines():
        str_contents = line.split( )

        # Live stats
        ipkts = str_contents[4]
        opkts = str_contents[8]

        totipkts = str_contents[7]
        totopkts = str_contents[10]


        # Process specified interface
        if (str_contents[0] in interface):
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            cursor.execute(last_timezone, (interface,))
            
            row = cursor.fetchone()
            db_timestamp = row[0]

            total_opkgs = opkts
            total_ipkgs = ipkts
            timestamp = int(time.time())

            if (db_timestamp == None):
                db_timestamp = int(time.time() - 5 * 60)


            if (timestamp >= (db_timestamp + 5 * 60)):

                data_traffic_insert = (interface,ipkts,opkts,totipkts,totopkts,timestamp)

                cursor.execute(add_traffic, data_traffic_insert)
           
                cnx.commit()
                cnx.close()

                ipkts_kb = int(ipkts) / 1024
                opkts_kb = int(opkts) / 1024

                ipkts_mb = ipkts_kb / 1024
                opkts_mb = opkts_kb / 1024

                ipkts_gb = ipkts_mb / 1024
                opkts_gb = opkts_mb / 1024

                print "Interface:\t\t", interface
                print "Current Inbound:\t", ipkts,"B"
                print "Current Outbound:\t", opkts,"B"
                print "Current Inbound:\t", ipkts_kb,"KB"
                print "Current Outbound:\t", opkts_kb,"KB"
                print "Current Inbound:\t", ipkts_mb,"MB"
                print "Current Outbound:\t", opkts_mb,"MB"
                print "Current Inbound:\t", ipkts_gb,"GB"
                print "Current Outbound:\t", opkts_gb,"GB"
                
                print "Total Inbound:\t\t", total_ipkgs
                print "Total Outbound:\t\t", total_opkgs

    # End Process output of netstat command    	