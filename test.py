# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import re
import urllib2
from bs4 import BeautifulSoup
from my.util import i2ch

if __name__ == '__main__':
    f = open('test.html')
    html = f.read().decode('shift_jis', 'ignore')
    f.close()
    
    p = re.compile(u'([a-zA-Z]{1})([a-zA-Z0-9\_-]){3,15}', re.IGNORECASE)
    bs = BeautifulSoup(html)
    for dt in bs.find_all('dt'):
        #print unicode(str(dt), 'utf-8', 'ignore')
        dd = dt.findNextSibling('dd')
        #print unicode(str(dd), 'utf-8', 'ignore')
        #match = p.search('([a-zA-Z]{1})([a-zA-Z0-9\_-]){3,15}', dd.text)
        iterator = p.finditer(dd.text)
        for match in iterator:
            print match.group()   # 1回目: ca      2回目: ca   