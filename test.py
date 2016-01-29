# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import urllib2
from bs4 import BeautifulSoup
from my.util import i2ch

if __name__ == '__main__':
    print 'スクリプトの時だけ  __name__ = %s' % __name__