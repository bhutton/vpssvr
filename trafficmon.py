#!/usr/bin/env python

"""
Use Netstat to monitor traffic

"""

import subprocess
import mysql.connector

config = {
  'user': 'ah_vps',
  'password': 'Mnie7865sh',
  'host': 'mysql',
  'database': 'ah_vps_dev',
  'raise_on_warnings': True,
}

add_traffic = ("INSERT INTO traffic "
               "(interface, LastIpkts, LastOpkts, TotalIpkts, TotalOpkts) "
               "VALUES (%s, %s, %s, %s, %s)")

mod_traffic = ("UPDATE traffic "
               "SET LastIpkts=%s,LastOpkts=%s,TotalIpkts=%s,TotalOpkts=%s "
               "WHERE interface=%s")

get_traffic = ("SELECT `LastIpkts`,`LastOpkts`,`TotalIpkts`,`TotalOpkts`,`index`,`interface` "
              "FROM `traffic` WHERE `interface`=%s")

netstat_cmd	= "/usr/bin/netstat"
args		    = "-b -I"
interface	  = "tap0"

command     = netstat_cmd + ' ' + args + ' ' + interface

proc = subprocess.Popen(['/bin/sh', '-c', command], stdout=subprocess.PIPE)

# Process output of netstat command
for line in proc.stdout.readlines():
    str_contents = line.split( )

    # Live stats
    ipkts = str_contents[7]
    opkts = str_contents[10]

    # Process specified interface
    if (str_contents[0] == interface):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        cursor.execute(get_traffic, (interface,))
        
        row = cursor.fetchone()

        if (row): # If entry already exists in DB
            # DB stats
            last_ipkts  = row[0]
            last_opkts  = row[1]
            total_ipkts = row[2]
            total_opkts = row[3]
            index       = row[4]
            interface   = row[5]

            total_ipkgs = int(total_ipkts) + (int(ipkts) - int(last_ipkts))
            total_opkgs = int(total_opkts) + (int(opkts) - int(last_opkts))

            data_traffic_update = (ipkts,opkts,ipkts,opkts,interface)

            cursor.execute(mod_traffic, data_traffic_update)

        else:
            total_opkgs = opkts
            total_ipkgs = ipkts

            data_traffic_insert = (interface,ipkts,opkts,ipkts,opkts)
            cursor.execute(add_traffic, data_traffic_insert)
   
        cnx.commit()
        cnx.close()

        ipkts_kb = int(ipkts) / 1024
        opkts_kb = int(opkts) / 1024

        ipkts_mb = ipkts_kb / 1024
        opkts_mb = opkts_kb / 1024

        ipkts_gb = ipkts_mb / 1024
        opkts_gb = opkts_mb / 1024

        print "Interface:\t\t", str_contents[0]
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