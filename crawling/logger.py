import time
logfile = "crawler-log.txt"

def log( data ):

	t = time.localtime()

	f = open(logfile, 'a')	
	f.write( "{0}:{1}:{2}  -  {3}\n".format (t.tm_hour, t.tm_min, t.tm_sec, data) )
	f.close()
