# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from collections import Counter

from my.util import i2ch
from my.db import datastore
from google.appengine.api import memcache

from flask import Blueprint, Markup, request
apis = Blueprint('apis', __name__)

def replace_id(value, id):
    """ID に strong タグを付けて強調する"""
    result = value.replace(id, '<strong>' + id + '</strong>')
    return Markup(result)
apis.add_app_template_filter(replace_id)

@apis.route('/userlist.js')
def userlistjs():
    """ユーザー一覧を JavaScript の変数として出力する"""
    memcache_key = 'userlistjs';
    ids = memcache.get(memcache_key)
    if ids is None:
        ids = json.dumps(datastore.get_all_ids(), indent=0)
        memcache.add(memcache_key, ids, 60 * 60 * 24)
    return 'var userlist = ' + ids + ';';

# /system/ 以下の URL は cron などでアプリから実行される前提であるものとする

@apis.route('/system/delete')
def delete():
    datastore.delete_all()
    return request.url

@apis.route('/system/import-0')
def import_0():
    """ファイルリストをインポート"""
    file = open('import/list.txt')
    lines = file.readlines()
    file.close()
    list = []
    for line in lines:
        list.append(line.strip())
    datastore.set_import_list(list)
    return request.url

@apis.route('/system/import-1')
def import_1():
    file_name = datastore.pop_imported_list()
    if file_name is None:
        return
        
    file = open('import/' + file_name + '.txt')
    dat = '\n'.join(file.readlines())
    file.close()
    
    file = open('import/' + file_name + '.json')
    thread = '\n'.join(file.readlines())
    file.close()
    thread = json.loads(thread)

    unicodedat = unicode(dat, 'shift-jis', 'ignore')
    counter = Counter(unicodedat)
    users = i2ch.get_user_list_from_dat(unicodedat)
    
    entries = []
    for user in users:
        response_num = int(user['response']['number'])
        entries.append({
            'number': response_num,
            'author': user['response']['name'],
            'mail': user['response']['mail'],
            'body': user['response']['body'],
            'authorid': user['response']['id'],
            'thread': thread['url'],
            'at': user['response']['datetime'].strftime('%Y/%m/%d %H:%M:%S.%f'),
            'ids': user['ids']
        })
    thread_title = unicodedat.splitlines()[0].split('<>')[4] # 乱暴、データ形式が変わるとこける
    thread_title = thread_title.replace('&amp;', '&');
    datastore.add_entry_task(entries)
    datastore.update_thread(thread['id'], {
        'url': thread['url'],
        'response_num': counter['\n'],
        'title': thread['title']
    })
    return request.url

@apis.route('/system/task-1')
def task_1():
    """スレッドを取得し保存"""
    thread_list = []
    thread = i2ch.search_thread_list_2ch_sc(u'ロボットゲー', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)
    thread = i2ch.search_thread_list_2ch_sc(u'ネットwatch', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)
    
    for thread in thread_list:
        datastore.update_task(thread['id'], {
            'url': thread['url'],
            'dat_url': thread['dat'],
            'title': thread['title'],
        })
    return request.url

@apis.route('/system/task-2')
def task_2():
    """task-1 で保存したスレッドからタスク待ちオブジェクトを作成する"""
    task = datastore.get_next_task()
    if task is None:
        logging.info('task not found.')
        return request.url
    dat = i2ch.download_html(task.dat_url)
    if dat is None:
        logging.error('download failed. URL:' + task.dat_url)
        return request.url

    # スレッド情報を取得し、チェック済み番号を取得
    thread_data = datastore.get_thread(task.id)
    checked_response = 0
    if thread_data is not None:
        checked_response = thread_data.response_num
    
    unicodedat = unicode(dat, 'shift-jis', 'ignore')
    counter = Counter(unicodedat)
    users = i2ch.get_user_list_from_dat(unicodedat)
    
    entries = []
    for user in users:
        response_num = int(user['response']['number'])
        # まだ未チェックのレス番までスキップする
        if response_num < checked_response:
            continue
        entries.append({
            'number': response_num,
            'author': user['response']['name'],
            'mail': user['response']['mail'],
            'body': user['response']['body'],
            'authorid': user['response']['id'],
            'thread': task.id,
            'at': user['response']['datetime'].strftime('%Y/%m/%d %H:%M:%S.%f'),
            'ids': user['ids']
        })
    thread_title = unicodedat.splitlines()[0].split('<>')[4] # 乱暴、データ形式が変わるとこける
    thread_title = thread_title.replace('&amp;', '&');
    datastore.add_entry_task(entries)
    datastore.update_thread(task.id, {
        'url': task.url,
        'response_num': counter['\n'],
        'title': thread_title
    })
    return request.url

@apis.route('/system/task-3')
def task_3():
    """task-2 で保存した情報を展開して書き込む"""
    # 一回で処理するタスク数
    PROC_TASK_NUM = 20
    
    entries = datastore.get_entry_task()
    thread_dic = {}
    ids_dic = {}
    task_count = 0
    while entries:
        entry = entries.pop(0)
        
        thread = None
        if entry['thread'] in thread_dic:
            thread = thread_dic[entry['thread']]
        else:
            thread = datastore.get_thread(entry['thread'])
            thread_dic[entry['thread']] = thread
        
        response_data = datastore.create_response({
            'number': entry['number'],
            'author': entry['author'],
            'mail': entry['mail'],
            'body': entry['body'],
            'authorid': entry['authorid'],
            'thread': thread,
            'at': datetime.strptime(entry['at'], '%Y/%m/%d %H:%M:%S.%f')
        })
        for id in entry['ids']:
            # このループで新規に追加された ID の場合、
            # データベースに保存される前に取得が発生するようで、
            # 結果的に同じ ID が複数データベースに書き込まれる現象が発生する
            # （根本的な解決ではないが）これを避けるため、いったん ID を保存し一括で保存するようにする
            #datastore.update_psn_user(id, response_data.key())
            if id not in ids_dic:
                ids_dic[id] = []
            ids_dic[id].append(response_data.key())
        task_count += 1
        if task_count > PROC_TASK_NUM:
            break
    for id, keys in ids_dic.iteritems():
        datastore.increment_user_count(id, keys)
    datastore.set_entry_task(entries)
    return request.url
