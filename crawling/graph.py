import pickle
import sqlite3
from cnt import *
from logger import log
import django.utils.html as djhtml

conn = sqlite3.connect('cnt_arn.db')
curs = conn.cursor()

try:
	q = """ create table edges (
		         title1 text,
		         url1 text,		         
		         title2 text,
		         url2 text
		 	) """
	curs.execute(q)
	q = "create index IDX_title1_edges on edges (title1) "
	curs.execute(q)


	q = """ create table nodes (
		         title text primary key unique,
		         url text,
		         rating float		         
		 	) """
	curs.execute(q)
	q = "create index IDX_title_nodes on nodes (title) "
	curs.execute(q)
	
	
	q = """ create table author_book_rating (
		         author text,
		         book_title text,
		         rating float		         
		 	) """
	curs.execute(q)
	q = "create index IDX_author_a_b_r on author_book_rating (author) "
	curs.execute(q)
	q = "create index IDX_book_title_a_b_r on author_book_rating (book_title) "
	curs.execute(q)
	
	
	log( "Database initialised." )
	
except sqlite3.OperationalError:
	log( "Database already initialised" )


def does_exist(title):
	q = "select * from nodes where title='{0}'".format ( myescape(title) )
	res = curs.execute (q)
	if len( res.fetchall() ) == 0:
		return False
	else:
		return True
		
#input node has all info set, simply add to nodetable and author vs book vs rating table
def addnode (node):
	
	q = "INSERT INTO nodes VALUES ('{0}','{1}','{2}')".format ( myescape(node.title), myescape(node.url), node.rating)
	curs.execute (q)

	for a in node.authorlist:
		q = "INSERT INTO author_book_rating VALUES ('{0}','{1}','{2}')".format ( a, myescape(node.url), node.rating)
		curs.execute (q)
	
	conn.commit()
	
	log( "[graph] node added with title : {0}".format (node.title) )	
	
# adds node1.url node1.title node2.url node2.title to edgetable indexed on node1.url
def addedge (node1, node2):

	try:
		q = "INSERT INTO edges VALUES ('{0}','{1}','{2}', '{3}') ".format ( myescape(node1.title), myescape(node1.url), myescape(node2.title), myescape(node2.url) )
	except UnicodeEncodeError:
		log( "\n\n[error]   *****  urlencode failed : edge not added \n----{0}\n----{1}\n\n".format (node1.title, '--' if node2 == None else node2.title ) )
		return False
	curs.execute (q)
	
	conn.commit()
	log( "[graph] edge added \n----{0}\n----{1}\n".format (node1.title, '--' if node2 == None else node2.title ) )
	return True
	
	
# return list of nodes with url n title filled
def get_neighbours (title):
	
	q = "SELECT url2, title2 FROM edges WHERE title1='{0}'".format (title)
	res = curs.execute (q)
	
	nlist = []
	for i in res.fetchall():
		url = i[0]
		title = i[1]
		n = node(title, url)
		nlist.append (n)
	
	return nlist
	

def myescape (datastr):

	#return datastr

		
	try:
		return djhtml.escape( datastr )
	except:	
		
		pickle.dump( datastr, open('badstring.p','wb') )
		
		log('[debug] ******** bad string : {0}'.format (datastr))
		t = datastr.decode('iso8859-2')
		#log('[debug] ******** good bad string : {0}'.format (t))
		#tt = djhtml.escape( t )
		return t
	
	
