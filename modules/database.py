import configparser
import os
import sqlite3 as sqlite
from flask import Flask
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.from_object(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

class DatabaseConnectivity:

    def __init__(self):
        self.configuration = configparser.ConfigParser()
        self.configuration.read("{}/../configuration.cfg".format(dir_path))
        self.database_driver = self.configuration.get('Database', 'database_driver')
        self.db_connection()

    def __del__(self):
        self.cnx.close()

    def db_connection(self):
        if self.database_driver == 'mysql':
            return self.db_connect_mysql()
        elif self.database_driver == 'sqlite':
            return self.db_connect_sqlite()

    def db_connect_sqlite(self):
        try:
            self.cnx = sqlite.connect(":memory:")
            self.cursor = self.cnx.cursor()
            self.initialise_sqlite_database()
            return 'connection successful'
        except:
            return 'an error occured'

    def initialise_sqlite_database(self):
        self.cursor.execute("CREATE TABLE disk(id int, name text, ord int, size int, vps_id int)")
        self.cursor.execute("CREATE TABLE vps "
                            "(id int,name text,description text,"
                            "ram int,console int,image int,path text,"
                            "startscript text,stopscript text)")
        self.cursor.execute("CREATE TABLE interface(bridge_id int,device int,id int,vps_id int)")
        self.cursor.execute("CREATE TABLE bridge(device int,id int)")
        self.cursor.execute("CREATE TABLE console(device int, id int)")

        self.cursor.execute("INSERT INTO vps VALUES(878,'test','mytest',512,1,1,'/tmp/','start','stop')")
        self.cursor.execute("INSERT INTO disk VALUES(878,'test',1,20,878)")

    def db_connect_mysql(self):
        try:
            self.database_user = self.configuration.get('Database', 'database_user')
            self.database_password = self.configuration.get('Database', 'database_password')
            self.database_host = self.configuration.get('Database', 'database_host')
            self.database_name = self.configuration.get('Database', 'database_name')
            self.raise_on_warnings = self.configuration.get('Database', 'raise_on_warnings')

            app.config['MYSQL_DATABASE_USER'] = self.database_user
            app.config['MYSQL_DATABASE_PASSWORD'] = self.database_password
            app.config['MYSQL_DATABASE_DB'] = self.database_name
            app.config['MYSQL_DATABASE_HOST'] = self.database_host

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

class DatabaseNetwork(DatabaseConnectivity):
    def __init__(self):
        #d = DatabaseConnectivity()
        #self.cursor = d.db_return_cursor()
        super().__init__()

    def __exit__(self):
        try:
            #self.cnx = db_connector.connect()
            self.cursor = self.cnx.cursor()
            self.cnx.close()
        except:
            print("Error closing database")

    def get_database_connection_status(self):
        return self.database_connected

    def get_interface(self):
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


class DatabaseVPS(DatabaseConnectivity):

    def __init__(self):
        super().__init__()

    def get_device(self, id):
        get_device_sql_query = (
            "select interface.id,interface.device,interface.vps_id,bridge.device "
            "from interface,bridge where vps_id=%s and interface.bridge_id = bridge.id")
        return self.db_get_all(get_device_sql_query)

    def get_devices(self, id):
        return self.db_get_all(
            "select interface.id,interface.device,interface.vps_id,bridge.device "
            "from interface,bridge "
            "where vps_id={} "
            "and interface.bridge_id = bridge.id".format(id))

    def get_vps_id_associated_with_disk(self, id):
        VPS = self.db_get_row("select vps_id from disk where id=" + str(id))

        return (VPS[0])

    def get_disk(self, id):
        return self.db_get_row("select size,vps_id from disk where id=" + str(id))

    def get_disks_details_from_database(self, id):
        return self.db_get_all("select id,size,name from disk where vps_id=" + str(id))

    def delete_disk_from_database(self, id):
        return self.db_execute_query("delete from disk where id=" + str(id))

    def create_disk_in_database(self, id, name, ord, size, vps_id):
        query = "insert into disk values(" + \
                str(id) + ",'" + \
                str(name) + "'," + \
                str(ord) + "," + \
                str(size) + "," + \
                str(vps_id) + ")"
        self.db_execute_query(query)

    def create_vps_in_database(self, id, name, description, ram, console, image, path, startscript, stopscript):
        return self.db_execute_query("insert into vps values(" + \
            str(id) + ",'" + \
            str(name) + "','" + \
            str(description) + "'," + \
            str(ram) + "," + \
            str(console) + "," + \
            str(image) + ",'" + \
            str(path) + "','" + \
            str(startscript) + "','" + \
            str(stopscript) + "')")

    def get_vps_details(self, id):
        self.vps = self.db_get_row(
            "select id,name,ram,console,image,path,startscript,stopscript "
            "from vps where vps.id=" + str(id))

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

    def get_console(self):
        return (self.console_number)

    def get_image(self):
        return (self.image)

    def get_path(self):
        return (self.file_system_path)

    def get_start_script(self):
        return (self.start_script_file)

    def get_stop_script(self):
        return (self.stop_script_path)

    def start_command(self, RootPath):
        vps_id = str(self.vps[0])
        vps_path = self.vps[5]
        vps_startscript = self.vps[6]

        if (vps_startscript == ""): vps_startscript = "start.sh"
        if (vps_path == ""): vps_path = RootPath + "/" + vps_id

        return ("/bin/sh " + vps_path + "/" + vps_startscript)

    def stop_command(self, RootPath):
        vps_id = str(self.vps[0])
        vps_path = self.vps[5]
        vps_startscript = self.vps[6]
        vps_stopscript = self.vps[7]

        if (vps_startscript == ""): vps_stopscript = "stop.sh"
        if (vps_path == ""): vps_path = RootPath + "/" + vps_id

        return ("/bin/sh " + vps_path + "/" + vps_stopscript)

    def stop_console(self, root_path):
        vps_id = str(self.vps[0])
        return ("sh " + root_path + "/" + vps_id + "/stopconsole.sh")