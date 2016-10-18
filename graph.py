import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as md
import mysql.connector
import database

config = {
  'user': 'ah_vps',
  'password': 'Mnie7865sh',
  'host': 'mysql',
  'database': 'ah_vps_dev',
  'raise_on_warnings': True,
}

#class display_graph


#sql = ("SELECT `TotalIpkts`,`TotalOpkts`,`timestamp` FROM `traffic` WHERE `interface`=%s")
#interface = "tap200"
sql = ("SELECT `TotalIpkts`,`TotalOpkts`,`timestamp` FROM `traffic`")


print sql

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

#cursor.execute(sql,(interface,))
#row = cursor.fetchall()

network = database.DB_Network()
row = network.getTrafficData(interface)

opackets = []
ipackets = []
timestamp = []

for line in row:
	
	ipkgs = line[0]/1024/1024
	opkts = line[1]/1024/1024
	tmestmp = dt.datetime.fromtimestamp(line[2])

	opackets.append(opkts)
	ipackets.append(ipkgs)
	timestamp.append(tmestmp)



# plot
plt.subplots_adjust(bottom=0.2)

plt.xticks( rotation=25 )
ax=plt.gca()
xfmt = md.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(xfmt)

plt.plot(timestamp,ipackets)
plt.plot(timestamp,opackets)
# beautify the x-labels
plt.gcf().autofmt_xdate()
plt.grid(True)
plt.legend(['In', 'Out'], loc='best')
plt.savefig('foo.png')
plt.show()