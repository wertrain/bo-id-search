# -*- coding: utf-8 -*-
u"""
    2ch 関連ユーティリティ
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import urllib2
import urllib
import json
import re
import logging
from datetime import datetime
from my.util import psn
from my.db import datastore
from bs4 import BeautifulSoup
from google.appengine.api import urlfetch

def get_boards():
    u"""
        板一覧情報を取得する
    """
    # 2ch の板一覧情報を取得する
    # 下記 URL から取得するが Shift-js 形式のため、変換を行う
    url = 'http://azlucky.s25.xrea.com/2chboard/2channel.brd'
    html = urllib2.urlopen(url).read()
    utf8text = unicode(html, 'shift-jis').encode('utf-8')
    # 一行ごとに分割 + 一行ずつ処理
    title = ''
    boardlist = {}
    list = utf8text.splitlines()
    for line in list:
        splitline = line.split()
        # 分割して 2 のものはタイトル行とみなす
        if (len(splitline) == 2):
            title = splitline[0]
            boardlist[title] = []
        # 分割して 3 のものは板情報とみなす
        # すでに title に何か値が入っている前提で
        # title をキーに辞書オブジェクトを追加していく
        elif (len(splitline) == 3):
            boardlist[title].append({
                'host': splitline[0], 
                'name': splitline[1],
                'title': splitline[2]
            })
    return boardlist

def get_board_host_url(category, title):
    u"""
        板一覧情報を取得する
    """
    boards = get_boards()
    for board in boards[category]:
        if board['title'] == title:
            return board['host']
    return ''

def get_board_subject_url(category, title):
    u"""
        subject.txtを取得する
    """
    boards = get_boards()
    for board in boards[category]:
        if board['title'] == title:
            return 'http://' + board['host'] + '/' + board['name'] + '/subject.txt'
    return ''

def search_thread_list(category, title, thread):
    u"""
        板からスレッド取得する
    """
    target_board = None
    boards = get_boards()
    for board in boards[category]:
        if board['title'] == title:
            target_board = board
    if target_board == None:
        return ''
    
    url = 'http://' + target_board['host'] + '/' + target_board['name'] + '/subject.txt'
    subject = download_html(url)
    unicodesubject = unicode(subject, 'shift-jis', 'ignore')

    result = []
    list = unicodesubject.splitlines()
    for line in list:
        if (line.count('<>') == 0):
            logging.error(url + ': download failed.')
            return None
        splitline = line.split('<>')
        if thread.decode('utf-8') in splitline[1]:
            dat_value = splitline[0].replace('.dat', '')
            # タイトルは
            # 機動戦士ガンダムバトルオペレーション晒しスレ108 [無断転載禁止]©2ch.net	(618)
            # こんな感じになっているので分離する
            splittitle = splitline[1].split('\t')
            
            result.append({
                'title': splittitle[0],
                'url': 'http://' + target_board['host'] + '/test/read.cgi/' + target_board['name'] + '/' + dat_value,
                'id': dat_value,
                'response_num': int(splittitle[1][2:-1])
            })
    return result

def parse_dt(dt):
    u"""
        HTMLタグ dt の行から レス番号/名前/ID/時刻 をパースし、オブジェクトとして返す
    """
    dttext = dt.text.encode('utf-8', 'ignore')
    base = dttext.split('：')
    info = base[2].split()
    tdatetime = datetime.strptime(info[0][:10] + ' ' + info[1][:11], '%Y/%m/%d %H:%M:%S.%f')
    a = dt.find('a')
    mail = '' if a is None else a.get('href')[7:]
    return {
        'number': unicode(base[0], 'utf-8'), 
        'name': unicode(base[1], 'utf-8', 'ignore'),
        'mail': mail,
        'id': unicode(info[2][3:], 'utf-8'), 
        'datetime': tdatetime
    }

def __text_with_newlines(element):
    u"""
        <br> を改行に置き換えて返す
    """
    text = ''
    for e in element.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text

def get_user_list_from_html(html):
    u"""
        スレッドの URL から HTML を取得し、パースする
    """
    psnutil = psn.PSNUtil()
    # ID:*** , URL の削除
    r = re.compile('((?<=ID:)([a-zA-Z0-9\_-]){6,10})|((?:https?|ftp|ttp|ttps):\/\/[-_.!~*\'()a-zA-Z0-9;\/?:@&=+$,%#]+)')
    result = []
    # <dt>, <dd> の閉じタグが抜けているので適当な対策
    html = html.replace('<dd>', '</dt><dd>').replace('<br><br>\n', '</dd><br><br>\n').decode('shift_jis', 'ignore')
    bs = BeautifulSoup(html)
    for dt in bs.find_all('dt'):
        info = parse_dt(dt)
        dd = dt.findNextSibling('dd')
        info['body'] = __text_with_newlines(dd)
        ddtext = r.sub('', dd.text)
        ids = psnutil.get_psn_id_list_from_text(ddtext)
        result.append({
            'response': info,
            'ids': ids,
        })
    return result

def download_html(url,proxy=False):
    u"""
        URL から HTML を取得する
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'none',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'ja,en-US;q=0.8,en;q=0.6',
        'Connection': 'keep-alive'
    }
    # http://stackoverflow.com/questions/17528759/how-to-fetch-a-url-by-proxy-on-google-app-engine
    # Google App Engine 上では Proxy が使えないらしい
    #proxy = urllib2.ProxyHandler({'http': '127.0.0.1'})
    #opener = urllib2.build_opener(proxy)
    #urllib2.install_opener(opener)
    
    #urlfetch.set_default_fetch_deadline(60)
    result = None
    if proxy:
        easy_proxy_url = datastore.get_proxy_url()
        if easy_proxy_url is not None:
            result = urlfetch.fetch(easy_proxy_url, urllib.urlencode({'url': url}), urlfetch.POST)
    else:
        result = urlfetch.fetch(url)
    
    if result is None:
        return 'error'
    elif result.status_code == 200:
        return result.content
    else:
        logging.error(result.content)
        return 'error 2'
