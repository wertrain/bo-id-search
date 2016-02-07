# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')
import codecs
import urllib2
from my.util import psn
from bs4 import BeautifulSoup

if __name__ == '__main__':
    html = urllib2.urlopen('http://yomogi.2ch.net/test/read.cgi/net/1453345266').read()
    print html