import sqlite3

conn = sqlite3.connect('cnt_arn.db')
curs = conn.cursor()


def set_coauthors():

	try:
		q = """
			CREATE TABLE coauthor_edges (
			ID INTEGER PRIMARY KEY,
			title1 text,
			title2 text,
			coauthor_count INTEGER DEFAULT 0
			)
		"""
		curs.execute(q)
	except sqlite3.OperationalError:
		pass
	

	q = """
		SELECT DISTINCT author
		FROM idwala_abr
	"""
	res = curs.execute(q)
	al = res.fetchall()

	for a in al:
		auth = a[0]
		print "~~~~~~~~ for author : {0}".format (auth)
		q = """
			SELECT book_title
			FROM idwala_abr
			WHERE author="{0}"
		""".format(auth)
		try:
			res = curs.execute(q)
		except:
			print "canceled"
			pass

		al = res.fetchall()

		for i in range(len(al)):
			if i+1 > len(al)-1:
				break;
			for j in range(i+1, len(al)):
				t1 = min(al[i][0], al[j][0])
				t2 = max(al[i][0], al[j][0])
				
				q=""" SELECT *
				FROM coauthor_edges
				WHERE title1="{0}" AND title2="{1}"
				""".format (t1, t2)				
				res=curs.execute(q)
				bla = res.fetchall()
				if len(bla) == 0:
					q = """ 
						INSERT INTO coauthor_edges ("title1", "title2", "coauthor_count")
						VALUES ("{0}", "{1}", 1)
					""".format (t1, t2)
					curs.execute(q)
				else:
					q = """
						UPDATE coauthor_edges
						SET coauthor_count={2}
						WHERE title1="{0}" AND title2="{1}"
					""".format (t1, t2, bla[0][3]+1)
				
	conn.commit()
	
	return locals()


				

def clean():
	try:
		qcreate = """ create table idwala_abr (
				ID INTEGER PRIMARY KEY,
			    author text,
			    book_title text,
			    rating float
				); 
		"""
		curs.execute(qcreate)

		qtransfer = """
			INSERT INTO "idwala_abr" ("author", "book_title", "rating")
			SELECT author, book_title, rating
			FROM author_book_rating
		"""
		curs.execute(qtransfer)
	except sqlite3.OperationalError:
		pass


	q = "SELECT * FROM idwala_abr"	

	res = curs.execute(q)
	t = res.fetchone()

	while True:
		bad = False
		while t != None:
			print t
			id = t[0]
			try:
				t = res.fetchone()			
			except sqlite3.OperationalError:
				print "error here at {0}".format (id+1)
				bad = True
				break

		if bad:
			qdel = """
				UPDATE idwala_abr
				SET author="badstring"
				WHERE ID={0}
			""".format(id+1)
			curs.execute(qdel)

			res = curs.execute(q)
			t = res.fetchone()
			continue

		else:
			conn.commit()
			return "Sucess"

def check():
	
	q = """ SELECT COUNT(*) FROM idwala_abr WHERE author="badstring"
	"""	
	res = curs.execute(q)
	bads = res.fetchall()[0][0]

	q = """ SELECT * FROM idwala_abr """	
	res = curs.execute(q)
	abr = res.fetchall()
	return {'no of bad authors strings':bads, 'abr':abr}

