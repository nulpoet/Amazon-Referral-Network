import sqlite3
from logger import log
from graph import myescape
conn = sqlite3.connect('cache.db')
curs = conn.cursor()

try:	
	q = "drop table cache"
	curs.execute(q)
	log( "[cache] Cache cleaned." )
	
except sqlite3.OperationalError:
	log( "[cache] Cache already clean." )
	
q = """ create table cache (
         key text primary key unique,
         data text
 	) """
curs.execute(q)
	

def add (key, val):
	try:
		q = "INSERT INTO cache VALUES ('{0}','{1}')".format (myescape(key), myescape(val))
		curs.execute (q)
		return True
	except:
		return False

def get (key):
	q = "select data from cache where key='{0}'".format (myescape(key))
	res = curs.execute (q)
	l = res.fetchall()
	if len (l) == 0:
		return None
	else:
		return l[0][0]
	
