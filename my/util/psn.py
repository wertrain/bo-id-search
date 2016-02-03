# -*- coding: utf-8 -*-
u"""
    PSN 関連ユーティリティ
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import re
from bs4 import BeautifulSoup

def is_valid_id(id):
    u"""
        有効な PSN ID か判定する
    """
    # 頻出単語BL
    list = ['wiki', 'twitter', 'href', 'target', 'blank', 
            'border', 'exam', 'youtube', 'skype', 'watch',
            'facebook', 'sage', 'line', 'psid', 'psnid', 
            'bb2ch', 'gp01', 'gp02', 'adsl']
    lowerid = id.lower()
    if lowerid in list:
        return False
    # その他正規表現で判定
    p = re.compile('^(ww+)|^(ll+)|^(ee+)|^(TUEE+)|^(HP[0-9]+)|^(AM([0-9]){1,2}$)|^(PM([0-9]){1,2}$)')
    return p.search(id) == None

def get_user_list_at_html(html):
    u"""
        スレッドの URL から HTML を取得し、パースする
    """
    # PSN ID の抽出
    p = re.compile('([a-zA-Z]{1})([a-zA-Z0-9\_-]){3,15}')
    # ID:*** , URL の削除
    r = re.compile('((?<=ID:)([a-zA-Z0-9\_-]){6,10})|((?:https?|ftp|ttp|ttps):\/\/[-_.!~*\'()a-zA-Z0-9;\/?:@&=+$,%#]+)')
    all_id = []
    bs = BeautifulSoup(html)
    for dt in bs.find_all('dt'):
        dd = dt.findNextSibling('dd')
        ddtext = r.sub('', dd.text)
        # 1レス分の投稿は重複判定のため、いったんこの配列へ
        ids = []
        iterator = p.finditer(ddtext)
        for match in iterator:
            id = match.group()
            if is_valid_id(id):
                ids.append(id)
        # 1レス分の投稿にある ID の重複削除
        ids = list(set(ids))
        for id in ids:
            all_id.append(id)
    return all_id
