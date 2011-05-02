import graph
from cnt import *

def get_latestnode():
	q = "select * from nodes"
	res = graph.curs.execute (q)
	l =  res.fetchall()
		
	if len(l) == 0:
		return None

	title = l[-1][0]
	url = l[-1][1]
	
	r = node(title, url)
	
	return r
