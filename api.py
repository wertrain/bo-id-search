# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

from my.util import i2ch
from my.db import datastore
from google.appengine.api import memcache

from flask import Blueprint
apis = Blueprint('apis', __name__)

@apis.route('/userlist.js')
def userlistjs():
    """ユーザー一覧を JavaScript の変数として出力する"""
    memcache_key = 'userlistjs';
    ids = memcache.get(memcache_key)
    if ids is None:
        ids = json.dumps(datastore.get_all_ids(), indent=0)
        memcache.add(memcache_key, ids, 60 * 60 * 24)
    return 'var userlist = ' + ids + ';';

@apis.route('/test')
def test():
#    return i2ch.search_thread_list('ゲーム', 'ロボットゲー', 'バトルオペレーション晒し')
    return str(i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し'))

@apis.route('/delete')
def delete():
    datastore.delete_all()
    return 'delete.'

@apis.route('/update')
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
        html = i2ch.download_html(thread['url'])
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
                'at': user['response']['datetime'].strftime('%Y/%m/%d %H:%M:%S'),
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

@apis.route('/task')
def task():
    entries = datastore.get_entry_task()
    thread_dic = {}
    ids_dic = {}
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
            'at': datetime.strptime(entry['at'], '%Y/%m/%d %H:%M:%S')
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
    for id, keys in ids_dic.iteritems():
        datastore.increment_user_count(id, keys)
    datastore.set_entry_task(entries)
    return 'task complete.'
