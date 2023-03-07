import sqlite3 as sql

#connect to SQLite
con = sql.connect('app.db')

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
cur.execute("DROP TABLE IF EXISTS requests")

#Create users table  in db_web database
sql ='''CREATE TABLE requests (
	"UID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"URL"	TEXT,
	"PREDICTION"	TEXT,
	"ELAPSED_TIME"	INTEGER
)'''
cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()