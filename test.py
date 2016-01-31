# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import re
import urllib2
from bs4 import BeautifulSoup
from my.util import i2ch

def is_valid_id(id):
    list = ['wiki', 'twitter', 'href', 'target', 'blank', 
            'border', 'exam', 'youtube', 'skype', 'watch',
            'facebook', 'sage', 'line', 'psid', 'psnid', 
            'bb2ch', 'gp01', 'gp02']
    lowerid = id.lower()
    if lowerid in list:
        return False
    p = re.compile('^(ww+)|^(ll+)|^(TUEE+)|^(HP[0-9]+)|^(AM([0-9]){1,2}$)|^(PM([0-9]){1,2}$)')
    return p.search(id) == None

if __name__ == '__main__':
    f = open('test.html')
    html = f.read().decode('shift_jis', 'ignore')
    f.close()
    
    # PSN ID の抽出
    p = re.compile('([a-zA-Z]{1})([a-zA-Z0-9\_-]){3,15}')
    # ID:*** , URL の削除
    r = re.compile('((?<=ID:)([a-zA-Z0-9\_-]){6,10})|((?:https?|ftp|ttp|ttps):\/\/[-_.!~*\'()a-zA-Z0-9;\/?:@&=+$,%#]+)')
    
    bs = BeautifulSoup(html)
    for dt in bs.find_all('dt'):
        dd = dt.findNextSibling('dd')
        ddtext = r.sub('', dd.text)
        iterator = p.finditer(ddtext)
        for match in iterator:
            if is_valid_id(match.group()):
                print match.group()