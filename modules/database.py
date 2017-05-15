import configparser
import os
import sqlite3 as sqlite
from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.from_object(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

# Get database configurations from configuration.cfg
'''configuration = configparser.ConfigParser()
configuration.read("{}/../configuration.cfg".format(dir_path))
database_driver = configuration.get('Database', 'database_driver')
database_user = configuration.get('Database', 'database_user')
database_password = configuration.get('Database', 'database_password')
database_host = configuration.get('Database', 'database_host')
database_name = configuration.get('Database', 'database_name')
raise_on_warnings = configuration.get('Database', 'raise_on_warnings')

if database_driver is 'mysql':
    app.config['MYSQL_DATABASE_USER'] = database_user
    app.config['MYSQL_DATABASE_PASSWORD'] = database_password
    app.config['MYSQL_DATABASE_DB'] = database_name
    app.config['MYSQL_DATABASE_HOST'] = database_host

db_connector = MySQL()
db_connector.init_app(app)'''

class DatabaseConnectivity():

    def __init__(self, database_driver):
        # Get database configurations from configuration.cfg
        configuration = configparser.ConfigParser()
        configuration.read("{}/../configuration.cfg".format(dir_path))
        database_driver = configuration.get('Database', 'database_driver')
        database_user = configuration.get('Database', 'database_user')
        database_password = configuration.get('Database', 'database_password')
        database_host = configuration.get('Database', 'database_host')
        database_name = configuration.get('Database', 'database_name')
        raise_on_warnings = configuration.get('Database', 'raise_on_warnings')

        if database_driver is 'mysql':
            app.config['MYSQL_DATABASE_USER'] = database_user
            app.config['MYSQL_DATABASE_PASSWORD'] = database_password
            app.config['MYSQL_DATABASE_DB'] = database_name
            app.config['MYSQL_DATABASE_HOST'] = database_host

        self.cursor = None
        self.db_connection(database_driver)

    def __del__(self):
        self.cnx.close()

    def db_connection(self, database_driver):
        if database_driver == 'mysql':
            return self.db_connect_mysql()
        if database_driver == 'sqlite':
            return self.db_connect_sqlite()

    def db_connect_sqlite(self):
        try:
            if(os._exists("/tmp/database.db")):
                self.cnx = sqlite.connect("/tmp/database.db")
                #self.d.db_execute_query("CREATE TABLE vps (id,name,ram,console,image,path,startscript,stopscript)")
                #self.d.db_execute_query("CREATE TABLE disk (id,name,size,vps_id)")
            else:
                self.cnx = sqlite.connect("/tmp/database.db")

            #self.cnx.row_factory = sqlite.Row
            self.cursor = self.cnx.cursor()
            return 'connection successful'
        except:
            return 'an error occured'

    def db_connect_mysql(self):
        try:
            db_connector = MySQL()
            db_connector.init_app(app)
            self.cnx = db_connector.connect()
            self.cursor = self.cnx.cursor()
            self.database_connected = True
        except:
            self.database_connected = False
            return "error connecting to database"

    def db_return_cursor(self):
        return self.cursor

    def db_execute_query(self, query):
        self.cursor.execute(query)
        return self.cnx.commit()

    def db_get_row(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def db_get_all(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

'''class DBMySQL(DatabaseConnectivity):
    def db_connection(self, database_driver):
        return self.db_connect_mysql()

class DBSqlite(DatabaseConnectivity):
    def db_connection(self, database_driver):
        return self.db_connect_sqlite()'''


class DatabaseNetwork:
    def __init__(self):
        '''try:
            self.cnx = db_connector.connect()
            self.cursor = self.cnx.cursor()
            self.database_connected = True
        except:
            print("error connecting to database")
            self.database_connected = False'''
        d = DatabaseConnectivity(database_driver)
        self.cursor = d.db_return_cursor()

    def __exit__(self):
        try:
            self.cnx = db_connector.connect()
            #self.cnx = mysql.connector.connect(**config)
            self.cursor = self.cnx.cursor()
            self.cnx.close()
        except:
            print("Error closing database")





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
        configuration = configparser.ConfigParser()
        configuration.read("{}/../configuration.cfg".format(dir_path))
        database_driver = configuration.get('Database', 'database_driver')
        database_user = configuration.get('Database', 'database_user')
        database_password = configuration.get('Database', 'database_password')
        database_host = configuration.get('Database', 'database_host')
        database_name = configuration.get('Database', 'database_name')
        raise_on_warnings = configuration.get('Database', 'raise_on_warnings')
        '''configuration_settings = configparser.ConfigParser()
        configuration_settings.read("{}/../configuration.cfg".format(dir_path))

        configuration_settings = {
            'user': configuration_settings.get('Database', 'database_user'),
            'password': configuration_settings.get('Database', 'database_password'),
            'host': configuration_settings.get('Database', 'database_host'),
            'database': configuration_settings.get('Database', 'database_name'),
            'raise_on_warnings': True,
        }

        self.root_path = configuration_settings.get('Global', 'RootPath')

        self.cnx = db_connector.connect()'''
        #self.cnx = mysql.connector.connect(**configuration_settings)
        #self.cursor = self.cnx.cursor()
        #self.db_connection(database_driver)

        self.d = DatabaseConnectivity(database_driver)
        self.cursor = self.d.db_return_cursor()

    def db_connection(self, database_driver):
        if database_driver == 'mysql':
            return self.db_connect_mysql()
        if database_driver == 'sqlite':
            return self.db_connect_sqlite()

    def db_connect_sqlite(self):
        try:
            self.cnx = sqlite.connect("/tmp/database.db")
            self.cnx.row_factory = sqlite.Row
            self.cursor = self.cnx.cursor()
            return 'connection successful'
        except:
            return 'an error occured'

    def db_connect_mysql(self):
        try:
            self.cnx = db_connector.connect()
            self.cursor = self.cnx.cursor()
            self.database_connected = True
        except:
            self.database_connected = False
            return "error connecting to database"

    def get_device(self, id):
        get_device_sql_query = (
            "select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id")
        self.cursor.execute(get_device_sql_query, (id,))
        self.int = self.cursor.fetchall()

        return self.int

    def get_devices(self, id):
        self.cursor.execute(
            "select interface.id,interface.device,interface.vps_id,bridge.device from interface,bridge where vps_id=? and interface.bridge_id = bridge.id",
            (id,))

        return self.cursor.fetchall()

    def get_vps_id_associated_with_disk(self, id):
        #self.cnx = db_connector.connect()
        #self.cursor = self.cnx.cursor()

        #self.cursor.execute("select vps_id from disk where id=%s", (id,))

        #VPS = self.cursor.fetchone()

        VPS = self.d.db_get_row("select vps_id from disk where id=" + str(id))

        return (VPS[0])

    def get_disk(self, id):
        self.cnx = db_connector.connect()
        self.cursor = self.cnx.cursor()

        self.cursor.execute("select size,vps_id from disk where id=%s", (id,))
        return self.cursor.fetchone()

    def get_disks_details_from_database(self, id):
        #self.cursor.execute("select id,size,name from disk where vps_id=%s", (id,))
        #return self.cursor.fetchall()

        self.d.db_get_all("select id,size,name from disk where vps_id=" + str(id))

    def delete_disk_from_database(self, id):
        #self.cursor.execute("delete from disk where id=%s", (id,))
        #self.cnx.commit()
        self.d.db_execute_query("delete from disk where id=" + str(id))

    def create_disk_in_database(self, id, name, ord, size, vps_id):
        query = "insert into disk values(" + \
                str(id) + ",'" + \
                str(name) + "'," + \
                str(ord) + "," + \
                str(size) + "," + \
                str(vps_id) + ")"
        self.d.db_execute_query(query)

    def create_vps_in_database(self, id, name, description, ram, console, image, path, startscript, stopscript):
        query = "insert into vps values(" + \
            str(id) + ",'" + \
            str(name) + "','" + \
            str(description) + "'," + \
            str(ram) + "," + \
            str(console) + "," + \
            str(image) + ",'" + \
            str(path) + "','" + \
            str(startscript) + "','" + \
            str(stopscript) + "')"
        print(query)
        self.d.db_execute_query(query)

    def get_vps_details(self, id):
        get_vps_details_sql_query = (
            "select "
                "id,name,ram,console,image,path,startscript,stopscript "
            "from "
                "vps where vps.id=" + str(id))
        #self.cursor.execute("CREATE TABLE vps (id,name,ram,console,image,path,startscript,stopscript,vps.id)")
        #self.cursor.execute("INSERT INTO vps VALUES (1,'test',512,1,1,'/tmp/','abc','def',1)")
        #self.d.db_execute_query("INSERT INTO vps VALUES (1,'test',512,1,1,'/tmp/','abc','def')")
        #self.cnx.commit()

        self.vps = self.d.db_get_row(get_vps_details_sql_query)

        #self.cursor.execute(get_vps_details_sql_query,(id,))
        #self.vps = self.cursor.fetchone()

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

        print("vps_path = {}".format(vps_path))

        if (vps_startscript == ""): vps_startscript = "start.sh"
        if (vps_path == ""): vps_path = RootPath + "/" + vps_id

        print("vps_path = {}".format(vps_path))

        print("command = " + str(vps_path) + "/" + vps_startscript)

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
