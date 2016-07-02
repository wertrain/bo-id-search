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
            'url': thread['dat'],
            'title': thread['title'],
        })
    return request.url

@apis.route('/system/task-2')
def task_2():
    """task-1で保存したスレッドからタスク待ちオブジェクトを作成する"""
    task = datastore.get_next_task()
    if task is None:
        logging.info('task not found.')
        return request.url
    dat = i2ch.download_html(task.url)
    if dat is None:
        logging.error('download failed. URL:' + task.url)
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
    """task-2で保存した情報を展開して書き込む"""
    # 一回で処理するタスク数
    PROC_TASK_NUM = 10
    
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

@apis.route('/system/test')
def test():
    dat = i2ch.download_html('http://awabi.2ch.sc/net/dat/1465076427.dat')
    return unicode(dat, 'shift-jis', 'ignore')

@apis.route('/system/store')
def store():
    """スレッドを取得し保存、タスク処理用のオブジェクトを作成する"""
    thread_list = []
    thread = i2ch.search_thread_list_2ch_sc(u'ロボットゲー', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)
    thread = i2ch.search_thread_list_2ch_sc(u'ネットwatch', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)
        
    results = []
    for thread in thread_list:
        dat = i2ch.download_html(thread['dat'])
        unicodedat = unicode(dat, 'shift-jis', 'ignore').encode('utf-8', 'ignore')
        results.append({
            'thread': thread,
            'user_list': i2ch.get_user_list_from_dat(unicodedat)
        })
        results.append(thread['dat'])
    return str(results)

@apis.route('/system/update')
def update():
    """スレッドを取得し保存、タスク処理用のオブジェクトを作成する"""
    thread_list = []
    thread = i2ch.search_thread_list('ゲーム', 'ロボットゲー', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)
    thread = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    if thread is not None:
        thread_list.extend(thread)

    results = []
    for thread in thread_list:
        html = i2ch.download_html(thread['url'], proxy=True)
        results.append({
            'thread': thread,
            'user_list': i2ch.get_user_list_from_html(html)
        })
    
    entries = []
    for result in results:
        # スレッド情報を取得
        thread = result['thread']
        # データストアにスレッドの情報が保存されているかチェックする
        thread_data = datastore.get_thread(thread['id'])
        checked_response = 0
        if thread_data is not None:
            checked_response = thread_data.response_num

        last_response = 0
        users = result['user_list']
        for user in users:
            response_num = int(user['response']['number'])
            # まだ未チェックのレス番までスキップする
            if response_num < checked_response:
                continue
            last_response = response_num
            # ID が含まれないレスはスキップ
            if len(user['ids']) == 0:
                continue
            # 新しいレスの保存
            #response_data = datastore.create_response({
            #    'number': response_num,
            #    'author': user['response']['name'],
            #    'mail': user['response']['mail'],
            #    'body': user['response']['body'],
            #    'thread': thread_data,
            #    'at': user['response']['datetime']
            #})
            entries.append({
                'number': response_num,
                'author': user['response']['name'],
                'mail': user['response']['mail'],
                'body': user['response']['body'],
                'authorid': user['response']['id'],
                'thread': thread['id'],
                'at': user['response']['datetime'].strftime('%Y/%m/%d %H:%M:%S.%f'),
                'ids': user['ids']
            })
            #for id in user['ids']:
            #    datastore.update_psn_user(id, response_data.key())
        datastore.add_entry_task(entries)
        datastore.update_thread(thread['id'], {
            'url': thread['url'],
            'response_num': last_response,
            'title': thread['title']
        });
    return 'updated.'

@apis.route('/system/task')
def task():
    # 一回で処理するタスク数
    PROC_TASK_NUM = 10
    
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
    return 'task complete.'
