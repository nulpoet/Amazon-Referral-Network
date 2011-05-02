import sqlite3
import pickle
from numpy import *

conn = sqlite3.connect('cnt_arn.db')
curs = conn.cursor()

def print_Eij( Eij ):
	for i in range(24):
		s = ""
		for j in range(24):
			s += "%.5f " % Eij[i][j]
		print s


def get_coauthor_assortativity_wrt_pop():

#	dmap = get_coauth_dd()
	
	q = """
		SELECT author, SUM(rating), COUNT(rating)
		FROM idwala_abr
		GROUP BY author
	"""
	res = curs.execute(q)
	rmap = {}
	for a in res.fetchall():
		rmap [a[0]] = a[1] / a[2]

	Eij	= zeros([50+1,50+1])
	dmax = 50

	discardcount = 0
	edgecount = 0
	for i in rmap.keys():
		nlist = []

		q1 = """
			SELECT title2
			FROM coauthor_edges
			WHERE title1="{0}"
		""".format(i)
		try:
			res = curs.execute(q1)
		except sqlite3.OperationalError:
			print "discarding {0}".format (i)
			discardcount += 1
			continue
		nlist += res.fetchall()

		q2 = """
			SELECT title1
			FROM coauthor_edges
			WHERE title2="{0}"
		""".format(i)
		res = curs.execute(q2)
		nlist += res.fetchall()

		for n in nlist:
			try:
				r1 = rmap[i]
			except KeyError:
				r1 = 3.5
			try:
				r2 = rmap[n[0]]			
			except KeyError:
				r2 = 3.5

			try:				
				Eij [int(10*r1)] [int(10*r2)]  += 1
				Eij [int(10*r2)] [int(10*r1)]  += 1
			except IndexError:
				print "IndexError :  rmap[i]:{0}  rmap[n[0]:{1}".format (rmap[i], rmap[n[0]])
			edgecount += 2

		print "done for {0}   len(nlist):{1}".format (i, len(nlist))

	Eij = divide(Eij, edgecount)

	a = zeros([dmax+1])
	b = zeros([dmax+1])
	for i in range(dmax+1):
		a[i] = sum(Eij[i][:])
		b[i] = sum(Eij[:][i])

	r = (trace(Eij) - sum(multiply(a,b))) / (1 - sum(multiply(a,b)))

	return (r, Eij, edgecount, discardcount)





def get_coauthor_assortativity():

	dmap = get_coauth_dd()

	dmax = max( dmap.values() )
	
	Eij	= zeros([dmax+1,dmax+1])
	
	edgecount = 0
	for i in dmap.keys():
		nlist = []

		q1 = """
			SELECT title2
			FROM coauthor_edges
			WHERE title1="{0}"
		""".format(i)
		res = curs.execute(q1)
		nlist += res.fetchall()

		q2 = """
			SELECT title1
			FROM coauthor_edges
			WHERE title2="{0}"
		""".format(i)
		res = curs.execute(q2)
		nlist += res.fetchall()

		for n in nlist:
			try:
				Eij [dmap[i]]    [dmap[n[0]]] += 1
				Eij [dmap[n[0]]] [dmap[i]]    += 1
			except IndexError:
				print "IndexError :  dmap[i]:{0}  dmap[n[0]:{1}".format (dmap[i], dmap[n[0]])
			edgecount += 2

	Eij = divide(Eij, edgecount)

	a = zeros([dmax+1])
	b = zeros([dmax+1])
	for i in range(dmax+1):
		a[i] = sum(Eij[i][:])
		b[i] = sum(Eij[:][i])

	r = (trace(Eij) - sum(multiply(a,b))) / (1 - sum(multiply(a,b)))

	return (r, Eij, edgecount)


def get_coauth_cc():

	q = """
		SELECT DISTINCT title1
		FROM coauthor_edges
	"""
	res = curs.execute(q)
	lt = res.fetchall()
	
	cci = {}
	for t in lt:
		cci[t[0]] = -1

	for t in lt:		
		nlist = []

		q1 = """
			SELECT title2
			FROM coauthor_edges
			WHERE title1="{0}"
		""".format(t[0])

		res = curs.execute(q1)
		nlist += res.fetchall()

		q2 = """
			SELECT title1
			FROM coauthor_edges
			WHERE title2="{0}"
		""".format(t[0])
		res = curs.execute(q2)
		nlist += res.fetchall()

		
		if( len(nlist)<2 ):
			cci[t[0]] = 0
			continue

		triplets = len(nlist) * (len(nlist) - 1) / 2.0
		triangles = 0.0

		for i in range(len(nlist)):
			for j in range(i+1,len(nlist)):
				q = """
					SELECT *
					FROM coauthor_edges
					WHERE (title1="{0}" AND title2="{1}") OR (title1="{1}" AND title2="{0}")
				""".format (nlist[i][0], nlist[j][0])
				res = curs.execute(q)
				if len(res.fetchall()) > 0:
					triangles += 1

		cci[t[0]] = triangles / triplets;
	
	pickle.dump( cci, open('cci.p','wb') )
	
	return cci



def get_coauth_dd():

	q1 = """
		SELECT title1, count(title2)
		FROM coauthor_edges
		GROUP BY title1
	"""
	res = curs.execute(q1)
	l_t1 = res.fetchall()

	q2 = """
		SELECT title2, count(title1) 
		FROM coauthor_edges
		GROUP BY title2
	"""
	res = curs.execute(q2)
	l_t2 = res.fetchall()

	dmap = {}

	for i in l_t1:
		dmap[i[0]] = i[1]

	for i in l_t2:
		try:
			dmap[i[0]] += i[1]
		except KeyError:
			dmap[i[0]] = i[1]
			print "only in title2 for {0}".format (i[0])

	return dmap

"""	dd = []
	for i in l_t1:
		title = i[0]
		deg = i[1]
		for j in l_t1:
			if j[0] == title:
				deg += 1;
		dd.append({'title':title, 'deg':deg})

	return dd """



def get_deg_count(dd, degl):
	
	dcnt = {}
	for d in degl:
		dcnt[str(d)] = 0	
	for i in dd:
		try:
			ind = degl.index(i['deg'])
			dcnt[str(i['deg'])] += 1 
		except ValueError:
			pass
	return dcnt

def get_cocost_dd():
	q1 = """
		SELECT title1, count(title2) 
		FROM edges
		GROUP BY title1
	"""
	res = curs.execute(q1)
	l_t1 = res.fetchall()

	q2 = """
		SELECT title2, count(title1) 
		FROM edges
		GROUP BY title2
	"""
	res = curs.execute(q2)
	l_t2 = res.fetchall()

	dd = []
	for i in l_t1:
		title = i[0]
		deg = i[1]
		for j in l_t1:
			if j[0] == title:
				deg += 1;
		dd.append({'title':title, 'deg':deg})

	return dd

#	q = """
#		SELECT * 
#		FROM nodes
#		WHERE title="The Economic and Philosophic Manuscripts of 1844 and the Communist Manifesto (Great Books in Philosophy) (Paperback)"
#	"""


def if_b_is_a (p_th) :
	
	q = """
		SELECT DISTINCT COUNT(book_title)
		FROM author_book_rating
		WHERE rating > {0} 
			AND
			author IN (
				SELECT author
				FROM (
					SELECT author, AVG(rating) AS avg_r
					FROM author_book_rating
					GROUP BY author
				)
				WHERE avg_r > {0}
			)
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	pcount = l[0][0]




	q = "SELECT DISTINCT COUNT(book_title) FROM author_book_rating WHERE rating > {0}".format (p_th)
	res = curs.execute (q)
	l = res.fetchall()
	tcount = l[0][0]
	

	print "pcount : {0} , tcount : {1}".format (pcount, tcount)
	
	return float(pcount)/tcount




def f2 (p_th) :

	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount > 1
		AND
		rating > {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	ma_p = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount > 1
		AND
		rating <= {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	ma_np = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount = 1
		AND
		rating > {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	sa_p = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount = 1
		AND
		rating <= {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	sa_np = l[0][0]
	
	
	print "ma_p : {0}, ma_np : {1} , sa_p : {2} , sa_np : {3}".format (ma_p ,ma_np, sa_p, sa_np)
	
	return { 'ma': float(ma_p)/(ma_p + ma_np), 'sa': float(sa_p)/(sa_p + sa_np) }
	



def f3 (p_th) :
	""" Has a book been more popular if it is  recommended by very few popular authors or many less popular authors have recommended it ? """
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount = 1
		AND
		rating > {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	spa_p = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r > {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount = 1
		AND
		rating <= {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	spa_np = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r <= {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount > 1
		AND
		rating > {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	mnpa_p = l[0][0]
	
	
	q = """
	SELECT COUNT(book_title)
	FROM (
		SELECT book_title , rating, COUNT(author) AS acount
		FROM ( SELECT * 
				FROM author_book_rating	
				WHERE author IN (
					SELECT author
					FROM (
						SELECT author, AVG(rating) AS avg_r
						FROM author_book_rating
						GROUP BY author
					)
					WHERE avg_r <= {0}
				)
			)
		GROUP BY book_title
	)
	WHERE acount > 1
		AND
		rating <= {0}
	""".format (p_th)
	
	res = curs.execute (q)
	l = res.fetchall()
	
	mnpa_np = l[0][0]
	
	
	print "spa_p : {0}, spa_np : {1}, mnpa_p : {2}, mnpa_np : {3}".format (spa_p ,spa_np ,mnpa_p ,mnpa_np)
	
	return { 'spa': float(spa_p)/(spa_p + spa_np), 'mnpa': float(mnpa_p)/(mnpa_p + mnpa_np) }





def assort (p_th) :
	
	q = """
		CREATE VIEW author_rating
		SELECT author, AVG(rating) AS avg_r
		FROM author_book_rating
		GROUP BY author;
		
		CREATE VIEW distinct_books
		SELECT DISTNCT book_title
		FROM author_book_rating;
		
		
	"""
	
	
	
#def f3():


from pygooglechart import SparkLineChart as Chart

def plot1():
	chart = Chart(400, 300)

	l = []

	for i in range(50):
		p_th = float(i)/10
		r = if_b_is_a (p_th)
		l.append (r)
	
	print l
	
	chart.add_data (l)
	chart.download('p1.png')
