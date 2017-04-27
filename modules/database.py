import ConfigParser
import os
from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.from_object(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

mysql = MySQL()

# Get MySQL configurations from configuration.cfg
Config = ConfigParser.ConfigParser()
Config.read("{}/../configuration.cfg".format(dir_path))
app.config['MYSQL_DATABASE_USER']       = Config.get('Database','database_user')
app.config['MYSQL_DATABASE_PASSWORD']   = Config.get('Database','database_password')
app.config['MYSQL_DATABASE_DB']         = Config.get('Database','database_name')
app.config['MYSQL_DATABASE_HOST']       = Config.get('Database','database_host')
mysql.init_app(app)

class DatabaseNetwork:
    def __init__(self):
        try:
            self.cnx = mysql.connect()
            self.cursor = self.cnx.cursor()
            self.database_connected = True
        except:
            print "error connecting to database"
            self.database_connected = False

    def __exit__(self):
        try:
            self.cnx = mysql.connect()
            #self.cnx = mysql.connector.connect(**config)
            self.cursor = self.cnx.cursor()
            self.cnx.close()
        except:
            print "Error closing database"

    def get_database_connection_status(self):
        return self.database_connected

    def get_interface(self):
        #self.cnx = mysql.connect()
        #self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()
        self.cursor.execute("select device from interface")
        self.int = self.cursor.fetchall()
        return self.int

    def get_traffic_data(self, interface):
        self.cursor.execute(
            "(SELECT `TotalIpkts`,"
            "`TotalOpkts`,"
            "`timestamp`,"
            "`index` FROM `traffic` "
            "where `interface`=%s "
            "ORDER BY `index` DESC LIMIT 10) "
            "ORDER BY `index` ASC",
            (interface,))
        self.row = self.cursor.fetchall()
        return self.row


class DatabaseVPS:
    vps = []

    def __init__(self):
        configuration_settings = ConfigParser.ConfigParser()
        configuration_settings.read("{}/../configuration.cfg".format(dir_path))

        configuration_settings = {
            'user': configuration_settings.get('Database', 'database_user'),
            'password': configuration_settings.get('Database', 'database_password'),
            'host': configuration_settings.get('Database', 'database_host'),
            'database': configuration_settings.get('Database', 'database_name'),
            'raise_on_warnings': True,
        }

        self.root_path = configuration_settings.get('Global', 'RootPath')

        self.cnx = mysql.connect()
        #self.cnx = mysql.connector.connect(**configuration_settings)
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
        #cnx = mysql.connector.connect(**config)
        #cursor = cnx.cursor()
        self.cnx.cursor.execute("select size,vps_id from disk where id=%s", (id,))
        return self.cnx.cursor.fetchone()

    def get_disks_details_from_database(self, id):

        self.cursor.execute("select id,size,name from disk where vps_id=%s", (id,))
        return self.cursor.fetchall()

    def delete_disk_from_database(self, id):
        self.cursor.execute("delete from disk where id=%s", (id,))
        self.cnx.commit()

    def get_vps_details(self, id):

        get_vps_details_sql_query = (
        "select id,name,ram,console,image,path,startscript,stopscript from vps where vps.id=%s")
        self.cursor.execute("select id,name,ram,console,image,path,startscript,stopscript from vps where vps.id=%s",
                            (id,))
        self.vps = self.cursor.fetchone()

        self.id = self.vps[0]
        self.name = self.vps[1]
        self.memory = self.vps[2]
        self.console_number = self.vps[3]
        self.image = self.vps[4]
        self.file_system_path = self.vps[5]
        self.start_script_file = self.vps[6]
        self.stop_script_path = self.vps[7]

        return self.vps

    def get_vps_id(self):
        return (self.id)

    def get_vps_name(self):
        return (self.name)

    def get_vps_memory(self):
        return (self.memory)

    def getConsole(self):
        return (self.console_number)

    def getImage(self):
        return (self.image)

    def getPath(self):
        return (self.file_system_path)

    def getStartScript(self):
        return (self.start_script_file)

    def getStopScript(self):
        return (self.stop_script_path)

    def startCommand(self, RootPath):

        # print "Rootpath = ".format(RootPath)
        # print "Get VPS ID = {}".format(self.get_vps_id())
        # self.vps = self.get_vps_details(self.get_vps_id())
        vps_id = str(self.vps[0])
        vps_name = self.vps[1]
        vps_ram = self.vps[2]
        vps_console = self.vps[3]
        vps_path = self.vps[5]
        vps_startscript = self.vps[6]
        vps_stopscript = self.vps[7]

        print "vps_path = {}".format(vps_path)

        if (vps_startscript == ""): vps_startscript = "start.sh"
        if (vps_path == ""): vps_path = RootPath + "/" + vps_id

        print "vps_path = {}".format(vps_path)

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
        if (vps_path == ""): vps_path = RootPath + "/" + vps_id

        return ("/bin/sh " + vps_path + "/" + vps_stopscript)

    def stopConsole(self, root_path):
        vps_id = str(self.vps[0])
        return ("sh " + root_path + "/" + vps_id + "/stopconsole.sh")
