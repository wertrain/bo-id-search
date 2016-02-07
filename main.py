# -*- coding: utf-8 -*-
import urllib2

from bs4 import BeautifulSoup
from my.util import i2ch
from google.appengine.api import memcache

from flask import Flask
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/test')
def open():
    #thread_list = i2ch.search_thread_list('ゲーム', 'ロボットゲー', 'バトルオペレーション晒し')
    #thread_list = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    #for thread in thread_list:
    #    memcache_key = thread['url']
    #    data = memcache.get(memcache_key)
    #    if data is None:
    #        count = thread['url']
    #    memcache.add(memcache_key, str(count), 60 * 60 * 24)
    thread_list = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    for thread in thread_list:
        memcache_key = thread['url']
        html = memcache.get(memcache_key)
        if html is None:
            html = i2ch.download_html(thread['url'])
            memcache.add(memcache_key, html, 60 * 60 * 24)
        ids = i2ch.get_user_list_from_html(html)
        return str(ids)
    
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500