# from flask import Flask
# from flaskext.mysql import MySQL
import mysql.connector
import ConfigParser
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

Config = ConfigParser.ConfigParser()
Config.read("{}/../configuration.cfg".format(dir_path))

config = {
    'driver': Config.get('Database', 'database_driver'),
    'user': Config.get('Database', 'database_user'),
    'password': Config.get('Database', 'database_password'),
    'host': Config.get('Database', 'database_host'),
    'database': Config.get('Database', 'database_name'),
    'raise_on_warnings': True,
}

class DB_Network:
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def getInt(self):
        self.cursor.execute("select device from interface")
        self.int = self.cursor.fetchall()
        return self.int

    def get_traffic_data(self, interface):
        self.cursor.execute(
            "(SELECT `TotalIpkts`,`TotalOpkts`,`timestamp`,`index` FROM `traffic` where `interface`=%s ORDER BY `index` DESC LIMIT 10) ORDER BY `index` ASC",
            (interface,))
        self.row = self.cursor.fetchall()
        return self.row


class DB_VPS:
    vps = []

    def __init__(self):
        Config = ConfigParser.ConfigParser()
        Config.read("{}/../configuration.cfg".format(dir_path))

        config = {
            'user': Config.get('Database', 'database_user'),
            'password': Config.get('Database', 'database_password'),
            'host': Config.get('Database', 'database_host'),
            'database': Config.get('Database', 'database_database'),
            'raise_on_warnings': True,
        }

        self.root_path = Config.get('Global', 'RootPath')

        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def get_device(self, id):
        get_device_sql_query = (
        "select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id")
        self.cursor.execute(get_device_sql_query, (id,))
        self.int = self.cursor.fetchall()

        return self.int

    def get_devices(self, id):
        self.cursor.execute(
            "select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id",
            (id,))

        return self.cursor.fetchall()

    def get_vps_id_associated_with_disk(self, id):
        self.cursor.execute("select vps_id from disk where id=%s", (id,))
        VPS = self.cursor.fetchone()

        return (VPS[0])

    def get_disk(self, id):
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        cursor.execute("select size,vps_id from disk where id=%s", (id,))
        return cursor.fetchone()

    def get_disks_details_from_database(self, id):

        self.cursor.execute("select id,size,name from disk where vps_id=%s", (id,))
        return self.cursor.fetchall()

    def delete_disk_from_database(self, id):
        self.cursor.execute("delete from disk where id=%s", (id,))
        self.cnx.commit()

    def getVPS(self, id):
        get_vps_details_sql_query = ("select id,name,ram,console,image,path,startscript,stopscript from vps where vps.id=%s")
        self.cursor.execute(get_vps_details_sql_query, (id,))
        self.vps = self.cursor.fetchone()

        self.ID = self.vps[0]
        self.Name = self.vps[1]
        self.RAM = self.vps[2]
        self.Console = self.vps[3]
        self.Image = self.vps[4]
        self.Path = self.vps[5]
        self.StartScript = self.vps[6]
        self.StopScript = self.vps[7]

        return self.vps

    def getID(self):
        return (self.ID)

    def getName(self):
        return (self.Name)

    def getRAM(self):
        return (self.RAM)

    def getConsole(self):
        return (self.Console)

    def getImage(self):
        return (self.Image)

    def getPath(self):
        return (self.Path)

    def getStartScript(self):
        return (self.StartScript)

    def getStopScript(self):
        return (self.StopScript)

    def startCommand(self, RootPath):

        vps_id = str(self.vps[0])
        vps_name = self.vps[1]
        vps_ram = self.vps[2]
        vps_console = self.vps[3]
        vps_path = self.vps[5]
        vps_startscript = self.vps[6]
        vps_stopscript = self.vps[7]

        if (vps_startscript == ""): vps_startscript = "start.sh"
        if (vps_path == ""): vps_path = self.root_path + "/" + vps_id

        print "command = " + str(vps_path) + "/" + vps_startscript

        return ("/bin/sh " + vps_path + "/" + vps_startscript)

    def stopCommand(self, RootPath):

        vps_id = str(self.vps[0])
        vps_name = self.vps[1]
        vps_ram = self.vps[2]
        vps_console = self.vps[3]
        vps_path = self.vps[5]
        vps_startscript = self.vps[6]
        vps_stopscript = self.vps[7]

        if (vps_startscript == ""): vps_stopscript = "stop.sh"
        if (vps_path == ""): vps_path = self.root_path + "/" + vps_id

        return ("/bin/sh " + vps_path + "/" + vps_stopscript)

    def stopConsole(self, RootPath):
        vps_id = str(self.vps[0])
        return ("sh " + RootPath + "/" + vps_id + "/stopconsole.sh")
