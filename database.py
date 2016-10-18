#from flask import Flask
#from flaskext.mysql import MySQL
import mysql.connector
import ConfigParser
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class DB_Network:

	def __init__(self):
		Config = ConfigParser.ConfigParser()
		Config.read("{}/configuration.cfg".format(dir_path))

		config = {
		  'user': Config.get('Database','mysql_user'),
		  'password': Config.get('Database','mysql_password'),
		  'host': Config.get('Database','mysql_host'),
		  'database': Config.get('Database','mysql_database'),
		  'raise_on_warnings': True,
		}
		
		self.cnx = mysql.connector.connect(**config)
		self.cursor = self.cnx.cursor()

	def getInt(self):
		self.cursor.execute("select device from interface")
		self.int = self.cursor.fetchall()
		return self.int

	def getTrafficData(self,interface):
		self.cursor.execute("(SELECT `TotalIpkts`,`TotalOpkts`,`timestamp`,`index` FROM `traffic` where `interface`=%s ORDER BY `index` DESC LIMIT 10) ORDER BY `index` ASC", (interface,))
		self.row = self.cursor.fetchall()
		return self.row