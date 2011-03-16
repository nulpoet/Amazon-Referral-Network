import re
import sys
from mechanize import Browser

# code to strip <script> tags from an HTML page
#from pyparsing import makeHTMLTags,SkipTo,quotedString

from pyparsing import *


from BeautifulSoup import BeautifulSoup


pat = re.compile ('<script.*/script>')

def cleanup (data):

	script,scriptEnd = makeHTMLTags("script")
	scriptBody = script + SkipTo(scriptEnd, ignore=quotedString) + scriptEnd

	descriptedHtml = scriptBody.suppress().transformString (data)

	return descriptedHtml


def dump (s, filename):
	f = open (filename, 'w')
	f.write (s)
	f.close ()

def load (filename):
	f = open(filename,'r')
	s = f.read()
	f.close()
	return s

def getdata (url):

	br = Browser ()

	# Ignore robots.txt
	br.set_handle_robots (False)
	# Google demands a user-agent that isn't a robot
	br.addheaders = [('User-agent', 'Firefox')]

	# Retrieve the Google home page, saving the response
	br.open (url)

	res = br.response()	
	data = res.get_data()

	return data

def getcleandata(url):
	data = getdata(url)
	cdata = cleanup(data)
	return cdata

"""
def getsoup(url):
	data = getdata (url)
	cdata = cleanup (data)
#	cdata_ = cdata.encode("utf-8")
	soup = BeautifulSoup (cdata)
	return soup
"""
"""
def get_rating_n_authors (datastr):
	soup = BeautifulSoup ( datastr.decode('utf-8', 'ignore') )
	
	n = soup.find("span", { "id" : "btAsinTitle" })

	temp = n.findNext('span')
	a = temp.findNext('span')
	alist = a.findChildren('a')

	authorlist = []
	for a in alist:
		authorlist.append( a.renderContents() )

	x = a.findNext('span')
	text = x.__str__()
	pat = re.compile('[.0-9]+ out of 5 stars')
	y = re.search(pat,text).group()
	rating = y[:3]		
#	temp = x.findChild('span',{'class':'swSprite s_star_5_0 '})
#	r = temp.findChild('span')
#	rating = float( r.renderContents()[:2] )
	
	return authorlist, rating
	
def t_get_rating_n_authors (datastr):
	soup = BeautifulSoup ( datastr.decode('utf-8', 'ignore') )
	
	n = soup.find("span", { "id" : "btAsinTitle" })

	temp = n.findNext('span')
	a = temp.findNext('span')
	alist = a.findChildren('a')

	authorlist = []
	for a in alist:
		authorlist.append( a.renderContents() )

	x = a.findNext('span')
	
	text = x
	
	temp = x.findChild('span',{'class':'swSprite s_star_5_0 '})
#	r = temp.findChild('span')
#	rating = float( r.renderContents()[:2] )

#	return authorlist, rating
	return authorlist, x, temp
"""

def foo(text):
	
	t1 = text.find('href="')
	if t1 == -1:
		return None, None
	text = text[t1:]
	
	t2 = text.find('">')
	t3 = text.find('</a>')
	
	author = text[t2+2:t3]
	text = text[t3:]

	return author, text


def get_authors (datastr):

	divS, divE = makeHTMLTags('div')
	spanS, spanE = makeHTMLTags('span')
	
	pdiv = originalTextFor( divS + SkipTo(divE) + divE )
#	pdiv = originalTextFor( divS + SkipTo(spanS) + spanS + SkipTo(spanE) + spanE + SkipTo(divE) + divE )
	
	divS.setParseAction( withAttribute( **{"class":"buying"} ) )
	spanS.setParseAction( withAttribute( **{"id":"'btAsinTitle'"} ) )	
	
	relist = pdiv.searchString(datastr)
	
	for re in relist:
		if re[0].find('id="btAsinTitle"') != -1:
	
			text = re[0]
	
#			return text
	
			authorlist = []
	
			while( text != None ):
				author, text = foo(text)
				if author != None:
					authorlist.append(author)

			return authorlist
		
	return None

"""	
# doesn't work!
def get_rating(datastr):

	spanS, spanE = makeHTMLTags('span')
	
	pspan = originalTextFor( spanS + SkipTo(spanE) + spanE )
	spanS.setParseAction( withAttribute( **{"class":"swSprite s_star_5_0"} ) )
	
	relist = pspan.searchString (datastr)
	return relist
"""	 

def get_related_books (datastr):

	divS, divE = makeHTMLTags('div')
	ulS, ulE = makeHTMLTags('ul')
	liS, liE = makeHTMLTags('li')

	pul = originalTextFor( ulS + SkipTo(ulE) + ulE )

	pdiv = divS + SkipTo(ulS) + pul("ultext") + SkipTo(divE)

	divS.setParseAction( withAttribute( id='purchaseButtonWrapper') )

	sl = pdiv.searchString (datastr)
	s = sl[0]
	

	datastr = s.ultext

	pli = originalTextFor( liS + SkipTo(liE) + liE )
	
	lilist = pli.searchString (datastr)

	blist = []

	for li in lilist :
		text = li[0]

		temp = re.search( re.compile('title="[^"]*"'), text).group()
		title = temp[temp.find('"')+1 : -1]

		temp = re.search( re.compile('href="[^"]*"'), text).group()
		link = temp[temp.find('"')+1 : -1]

		print title + " " + link		
		n = node (title, link)
		blist.append (n)

	return blist

def get_rating(data):
	
	off = data.find('btAsinTitle')
	text = data[off:]
	
	pat = re.compile('[.0-9]+ out of 5 stars')	
	y = re.search(pat, text).group()
	rating = float( y[:3] )
	return rating



class node():

	title = ""
	url = ""
	rating = 0.0
	authorlist = []
	
	blist = []


	def __init__ (self, title, url):
		self.title = title
		self.url = url
		
	def setinfo (self):	

		cdata = getcleandata (self.url)		
		self.authorlist = get_authors(cdata)
		self.rating = get_rating(cdata)
		self.blist = get_related_books (cdata)
		print "Info set for {0}".format (self.title)
		
	def __str__(self):
		output = ""
		output = output + "[******"
		output = output + "\n.. Title : {0}".format (self.title)
		output = output + "\n.. Rating : {0}".format (self.rating)
		output = output +'\n'+ ".. Authers : "
		for a in self.authorlist:
			output = output +'\n'+ ".... {0}".format (a)
			
		output = output +'\n'+ ".. Related Books : "
		for b in self.blist:
			output = output +'\n'+ ".... <title : {0}  |  url : {1} >".format (b.title, b.url)
		output = output +'\n'+ "******]"
		
		return output

def test():
	url  = "http://www.amazon.com/Life-Line-Chasing-Greatness-Redefining/dp/1592406017/ref=pd_sim_b_1"
	title = "Life, on the Line: A Chef's Story of Chasing Greatness, Facing Death, and Redefining the Way We Eat"
	
	r = node(title, url)
	r.setinfo()
	
	return r

def test_b1():
	url  = "http://www.amazon.com/Blood-Bones-Butter-Inadvertent-Education/dp/140006872X/ref=pd_sim_b_1"
	title = "Blood, Bones & Butter: The Inadvertent Education of a Reluctant Chef (Hardcover)"
	
	r = node(title, url)
	r.setinfo()
	
	return r
	
def test_b2():
	url  = "http://www.amazon.com/Alinea-Grant-Achatz/dp/1580089283/ref=pd_sim_b_2"
	title = "Alinea (Hardcover)"
	
	r = node(title, url)
	r.setinfo()
	
	return r
	


def test1_r():
	url = "http://www.amazon.com/Life-Line-Chasing-Greatness-Redefining/dp/1592406017/ref=pd_sim_b_1"
	data = getcleandata(url)
	return t_get_rating_n_authors (data)
	
def test1_b1():
	url  = "http://www.amazon.com/Blood-Bones-Butter-Inadvertent-Education/dp/140006872X/ref=pd_sim_b_1"
	data = getcleandata(url)
	return t_get_rating_n_authors (data)
	
def test1_b2():
	url  = "http://www.amazon.com/Alinea-Grant-Achatz/dp/1580089283/ref=pd_sim_b_2"
	data = getcleandata(url)
	return t_get_rating_n_authors (data)



if __name__ == "__main__":

	if len(sys.argv) == 1:
		print "usage : cnt.py -t <url> [ -t <url> ...]"
		
	for i in range( len(sys.argv[1:]) ):
		if sys.argv[1:][i] == '-t':
			url = sys.argv[1:][i+1]
			print "\n***** testing for url : {0}".format (url)
			
			cdata = getcleandata(url)
			print t_get_rating_n_authors (cdata)
			print get_related_books (cdata)
			
		
		
		
