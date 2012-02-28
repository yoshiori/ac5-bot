#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json,urllib,urllib2
from pit import Pit

class TwitterStream(object):
    """
    """
    
    def __init__(self, userid,password):
        """
        
        Arguments:
        - `userid`:
        - `password`:
        """
        self._userid = userid
        self._password = password
        

    def search(self, *track):
        url = 'https://stream.twitter.com/1/statuses/filter.json'
        opener = self.getOpener(url)
        params = {'track':','.join(track)}
        res = opener.open(url, urllib.urlencode(params))
        for line in res:
            if line.strip():
                yield json.loads(line)
        
        
    def getOpener(self,url):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url , self._userid, self._password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        opener.addheaders = [('User-agent',
                              'TwitterCloneClient(http://d.hatena.ne.jp/jYoshiori/)')]
        return opener

if __name__ == '__main__':
    twitter_config = Pit.get('twitter.com',{'require' : {
        'user' : 'Your twitter name',
        'password' : 'Your twitter password'}})
    stream = TwitterStream(twitter_config['user'], twitter_config['password'])
    for status in stream.search('ACV'):
        print status['text']

