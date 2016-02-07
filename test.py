# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

from my.util import i2ch

if __name__ == '__main__':
    f = open('test.html')
    html = f.read().decode('shift_jis', 'ignore')
    f.close()

    ids = i2ch.get_user_list_at_html(html)
    for id in ids:
        print id