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

def get_boards_2ch_sc():
    u"""
        板一覧情報を取得する（2ch.sc）
    """
    url = 'http://www.2ch.sc/bbsmenu.html'
    html = urllib2.urlopen(url).read()
    utf8text = unicode(html, 'shift-jis', 'ignore').encode('utf-8')
    # 一行ごとに分割 + 一行ずつ処理
    bs = BeautifulSoup(html)
    boardlist = {}
    for a in bs.find_all('a'):
        splitline = a['href'].split('/')
        boardlist[a.string] = {
            'host': splitline[2],
            'name': splitline[3],
        }
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
    
def get_board_host_url_2ch_sc(title):
    u"""
        板一覧情報を取得する（2ch.sc）
    """
    boards = get_boards_2ch_sc()
    if boards.has_key(title):
        return boards[title]['host']
    return None

def get_board_subject_url(category, title):
    u"""
        subject.txtを取得する
    """
    boards = get_boards()
    for board in boards[category]:
        if board['title'] == title:
            return 'http://' + board['host'] + '/' + board['name'] + '/subject.txt'
    return ''

def get_board_subject_url_2ch_sc(title):
    u"""
        subject.txtを取得する（2ch.sc）
    """
    boards = get_boards_2ch_sc()
    if boards.has_key(title):
        return 'http://' + boards[title]['host'] + '/' + boards[title]['name']  + '/subject.txt'
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

def search_thread_list_2ch_sc(title, thread):
    u"""
        板からスレッド取得する（2ch.sc）
    """
    target_board = None
    boards = get_boards_2ch_sc()
    if boards.has_key(title):
        target_board = boards[title]
    if target_board == None:
        return None
    
    url = 'http://' + target_board['host'] + '/' + target_board['name'] + '/subject.txt'
    subject = urllib2.urlopen(url).read()
    unicodesubject = unicode(subject, 'shift-jis', 'ignore').encode('utf-8')

    result = []
    list = unicodesubject.splitlines()
    for line in list:
        if (line.count('<>') == 0):
            logging.error(url + ': download failed.')
            return None
        splitline = line.split('<>')
        if splitline[1].find(thread) > -1:
            dat_value = splitline[0].replace('.dat', '')
            # タイトルは
            # 機動戦士ガンダムバトルオペレーション晒しスレ108 [無断転載禁止]©2ch.net	(618)
            # こんな感じになっているので分離する
            splittitle = re.split(r'\s', splitline[1])
            result.append({
                'title': splittitle[0].decode('utf-8'),
                'url': 'http://' + target_board['host'] + '/test/read.cgi/' + target_board['name'] + '/' + dat_value,
                'dat': 'http://' + target_board['host'] + '/' + target_board['name'] + '/dat/' + dat_value + '.dat',
                'id': dat_value,
                'response_num': int(splittitle[len(splittitle) - 1][1:-1])
            })
    return result

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

def get_user_list_from_dat(dat):
    psnutil = psn.PSNUtil()
    # HTML特殊文字, ID:*** , (ﾜｯﾁｮｲ ****-****) など, URL の削除
    r = re.compile('(&[a-z]+;)|((?<=ID:)([a-zA-Z0-9\_-]){6,10})|(\(.+ [a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}\))|((?:https?|ftp|ttp|ttps):\/\/[-_.!~*\'()a-zA-Z0-9;\/?:@&=+$,%#]+)')
    p = re.compile('<[^>]*?>')
    result = []
    number = 0
    for line in dat.splitlines():
        number = number + 1
        response_all = line.split('<>')
        if len(response_all) < 4:
            continue
        logging.error(response_all)
        body = p.sub('', response_all[3])
        body = r.sub('', body)
        ids = psnutil.get_psn_id_list_from_text(body)
        if len(ids) == 0: # 検出 id がゼロならスキップ
            continue
        date_time_id = response_all[2].split(' ')
        tdatetime = datetime.strptime(date_time_id[0][:10] + ' ' + date_time_id[1][:11], '%Y/%m/%d %H:%M:%S.%f')
        info = {
            'number': number, 
            'name': response_all[0],
            'mail': response_all[1],
            'id': date_time_id[2][3:] if len(date_time_id) > 2 else None,
            'body': response_all[3],
            'datetime': tdatetime
        }
        result.append({
            'response': info,
            'ids': ids,
        })
    return result

def download_html(url):
    u"""
        URL から HTML を取得する
    """
    result = urlfetch.fetch(url=url)
    if result.status_code == 200:
       return result.content
    else:
       logging.error(result.content)
       return None
