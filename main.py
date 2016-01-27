# -*- coding: utf-8 -*-
import urllib2

from bs4 import BeautifulSoup
from my.util import i2ch

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
    url = i2ch.get_board_subject_url('ゲーム', 'ロボットゲー')
    subject = urllib2.urlopen(url).read()
    unicodesubject = unicode(subject, 'shift-jis', 'ignore')
    list = unicodesubject.splitlines()
    for line in list:
        splitline = line.split('<>')
        return splitline[1]

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500