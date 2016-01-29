# -*- coding: utf-8 -*-
u"""
    2ch 関連ユーティリティ
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import urllib2
import json

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
    subject = urllib2.urlopen(url).read()
    unicodesubject = unicode(subject, 'shift-jis', 'ignore')

    result = []
    list = unicodesubject.splitlines()
    for line in list:
        splitline = line.split('<>')
        if thread.decode('utf-8') in splitline[1]:
            dat_value = splitline[0].replace('.dat', '')
            result.append({
                'title': splitline[1],
                'url': 'http://' + target_board['host'] + '/test/read.cgi/' + target_board['name'] + '/' + dat_value,
            })
    return result

def parse_thread_html(url):
    u"""
        スレッドの URL から HTML を取得し、パースする
    """
    html = urllib2.urlopen(url).read()
    utf8text = unicode(html, 'shift-jis').encode('utf-8')
    
    