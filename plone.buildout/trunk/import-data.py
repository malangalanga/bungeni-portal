#!/usr/bin/python
import urllib

username = 'admin'
password = 'admin'
url = 'localhost:8082/plone'

ids_to_transfer = ['front-page','images', 'plone-bungeni-content-types']

for id in ids_to_transfer:

    urllib.urlopen('http://%s:%s@%s/manage_delObjects?ids=%s' % (username, password, url, id))
    urllib.urlopen('http://%s:%s@%s/manage_importObject?file=%s.zexp' % (username, password, url,id))

print "Data imported successfully"    
