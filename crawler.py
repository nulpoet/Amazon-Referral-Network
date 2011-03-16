#import django.utils.html as djhtml
import traceback
#import memcache

import cache

#memc = memcache.Client(['127.0.0.1:11211'])
#memc.flush_all()

MAXTODOLEN = 1000

from logger import log
from cnt import *
import django.utils.html as djhtml
import graph


"""
def check_n_set( url, title ):

	q = " INSERT INTO {0} 	VALUES ('{1}', '{2}') ".format ('hashmap', djhtml.escape(url), djhtml.escape(title))
	try:
		curs.execute(q)
	except sqlite3.IntegrityError:
		log( "~(c)~" )
		traceback.print_stack()
		return False
		
	conn.commit()
	return True
"""

todolist = []

def explore (root):

	todolist.append( root )
	
	count = 0
	
	while len(todolist) != 0:
		
		log('[debug] todolist has {0} nodes'.format (len(todolist)))
		
		if len(todolist) == MAXTODOLEN:
			if (count == MAXTODOLEN):
				log  ('\n\n\n ******* Stuck in a loop.. hence exiting !! ********\n\n')
				print '\n\n\n ******* Stuck in a loop.. hence exiting !! ********\n\n'
				return
			count += 1
		else:
			count = 0
		
		n = todolist.pop(0)	
		blist = []
		#log('[debug] n.title : {0}\n does_exist returns : {1}'.format (n.title, graph.does_exist(n.title)) )
		
		if graph.does_exist (n.title) == False:
			try:
				n.setinfo ()
				if n.authorlist == None:
					log('\n\n[error] node.setinfo rendered authorlist None')	
					raise Exception
			except:
				log('[error] node.setinfo failed for : {0} url[{1}]\n'.format (n.title, n.url) )
				cache.add ( str(djhtml.escape(n.title)), djhtml.escape('[failure] '+n.url))
				continue
				
			graph.addnode (n)
			
			for b in n.blist:
				graph.addedge (n, b)
				
			blist = n.blist
		else:
			log('[debug] ** traversing already crawled node **')
			blist = graph.get_neighbours(n.title)
			
			
		cache.add ( str(djhtml.escape(n.title)), djhtml.escape(n.url) )
		
		print blist
		for b in blist:
			if len(todolist) == MAXTODOLEN :
				log('[debug] ** MAXTODOLEN hit !! **')
				continue
			if cache.get(str (djhtml.escape (b.title))) == None:
				todolist.append(b)
			else:
				log('[debug] ** Already cached !! **')
	
	log ('\n\n\n[finished] nothing left in todolist.\n\n')

	


if __name__ == "__main__":

	url = "http://www.amazon.com/Atlas-Shrugged-Ayn-Rand/dp/0451191145"
	title = "Atlas Shrugged [Mass Market Paperback]"
	
	r = node(title, url)	
	
	explore (r)
	
	
