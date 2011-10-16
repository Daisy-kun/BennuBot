from json import loads
from urllib2 import urlopen
from urllib import urlencode
plugName = 'Google Plugin'

#TODO Descriptions

def google_search(query, method):
	return loads(urlopen('http://ajax.googleapis.com/ajax/services/search/'+method+'?v=1.0&'+
		urlencode({'q':query})).read())

def google_firstResult(inMSG, method):
	result = google_search(inMSG[0].split(None, 1)[1], method)['responseData']['results']
	if result:
		sendMSG((result[0]['titleNoFormatting'] + ' -- ' + result[0]['unescapedUrl']).encode('utf-8'),
			inMSG[1], inMSG[2], inMSG[3])
	else:
		sendMSG('No results found.', inMSG[1], inMSG[2], inMSG[3])

def load():
	return {'g':(lambda x: google_firstResult(x, 'web')), 'gi':(lambda x: google_firstResult(x, 'images'))}
