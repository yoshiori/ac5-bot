#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,urllib2,dbm,pickle
from BeautifulSoup import BeautifulSoup
from ircbot import SingleServerIRCBot
from irclib import nm_to_n
from pit import Pit

class FuncBot(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, realname=None, password=None,port=6667):
        SingleServerIRCBot.__init__(self, [(server, port,password)], nickname,realname,password)
        self.channel = channel
        self.funcs = []
    def on_welcome(self, c, e):
        print 'welcome',c,e
        c.join(self.channel)
        
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_join(self, c, e):
        nick = nm_to_n(e.source())
        if nick != c.get_nickname():
            text = u'ようこそチーム nicobook へ。%sの帰還を歓迎します。' % nick
            self.connection.notice(self.channel, text.encode('utf-8'))
            
    def do_command(self,c,e):
        for func in self.funcs:
            func(self,c,e)

    def add_execute_delayed(self, sec, callback, obj):
        self.ircobj.execute_delayed(sec, callback, obj)

    on_pubmsg = do_command
    on_privmsg = do_command

import threading
from TwitterStream import TwitterStream
from time import sleep

class ACVthread(threading.Thread):
    """
    """
    
    def __init__(self, bot):
        threading.Thread.__init__(self)
        """
        
        Arguments:
        - `bot`:
        """
        self.setDaemon(True)
        self._bot = bot

    def run(self):
        """
        """
        twitter_config = Pit.get('twitter.com',{'require' : {
            'user' : 'Your twitter name',
            'password' : 'Your twitter password'}})
        stream = TwitterStream(twitter_config['user'], twitter_config['password'])
        print 'start stream'
        while True:
            for status in stream.search('ACV_DEFPS3'):
                msg = status['text']
                print msg, type(msg)
                self._bot.connection.notice(self._bot.channel, msg.encode('utf-8'))
            self._bot.connection.privmsg(self._bot.channel, 'twitter から切断されました。再接続します'.encode('utf-8'))
            print 'end stream'
            sleep(60)

if __name__ == '__main__':
    irc_config = Pit.get('acv.nicobook.irc',{'require' : {
        'server' : 'ex, irc.freenode.net',
        'channel' : 'ex, java-ja'}})

    db = dbm.open('ac5-status','c')
    print 'start'
    server = irc_config['server']
    channel = irc_config['channel']
    IRC_TIMER_SEC = 60 * 5
    bot = FuncBot('#%s' % channel,'ac5-bot',server)
    def debug_command(myself,c,e):
        msg = unicode(e.arguments()[0], "utf8")
        print msg
        myself.connection.bprivmsg(myself.channel, msg.encode('utf-8'))

    def get_status():
        try:
            url = 'http://www.armoredcore.net/players/acv/'
            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup(html)
            status =  soup.find('div',id='status_info')
            text = status.find('div', id='ps3').find('span').string.strip()
            return text
        except:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            print exceptionType,exceptionValue,exceptionTraceback
            return None

    def status_command(myself,c,e):
        msg = unicode(e.arguments()[0], "utf8")
        if msg == 'unk':
            text = get_status()
            if not text:
                text = u'ステータスの取得に失敗しました'
            myself.connection.notice(myself.channel, text.encode('utf-8'))

                
    def call_timer(myself):
        status = get_status()
        if status:
            print status
            before_status = db.get('status')
            if before_status:
                before_status = pickle.loads(before_status)  
            if before_status != status:
                text = u'サーバステータスが変更されました %s' % status
                myself.connection.notice(myself.channel, text.encode('utf-8'))
            db['status'] = pickle.dumps(status)
        myself.add_execute_delayed( IRC_TIMER_SEC, call_timer, (myself,))

    bot.add_execute_delayed( IRC_TIMER_SEC, call_timer, (bot,))
    bot.funcs.append(status_command)
    t = ACVthread(bot)
    t.start()
    print bot.start()
    
