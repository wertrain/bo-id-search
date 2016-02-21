# -*- coding: utf-8 -*-
import urllib2

from bs4 import BeautifulSoup
from my.util import i2ch
from my.db import datastore
from google.appengine.api import memcache

from flask import Flask, render_template
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    thread_list = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    for thread in thread_list:
        return (thread['title'])

@app.route('/update')
def update():
    #thread_list = i2ch.search_thread_list('ゲーム', 'ロボットゲー', 'バトルオペレーション晒し')
    #thread_list = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    #for thread in thread_list:
    #    memcache_key = thread['url']
    #    data = memcache.get(memcache_key)
    #    if data is None:
    #        count = thread['url']
    #    memcache.add(memcache_key, str(count), 60 * 60 * 24)
    thread_list = i2ch.search_thread_list('ネット関係', 'ネットwatch', 'バトルオペレーション晒し')
    results = []
    for thread in thread_list:
        memcache_key = thread['url']
        html = memcache.get(memcache_key)
        if html is None:
            html = i2ch.download_html(thread['url'])
            memcache.add(memcache_key, html, 60 * 60 * 24)
        results.append({
            'thread': thread,
            'user_list': i2ch.get_user_list_from_html(html)
        })
    
    for result in results:
        # スレッド情報を取得
        thread = result['thread']
        # データストアにスレッドの情報が保存されているかチェックする
        thread_data = datastore.get_thread(thread['id'])
        checked_response = 0
        if thread_data is None:
            thread_data = datastore.update_thread(thread['id']);
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
            response_data = datastore.create_response({
                'number': response_num,
                'author': user['response']['name'],
                'mail': user['response']['mail'],
                'body': user['response']['body'],
                'thread': thread_data,
                'at': user['response']['datetime']
            })
            for id in user['ids']:
                datastore.update_psn_user(id, response_data.key())
        datastore.update_thread(thread['id'], {
            'url': thread['url'],
            'response_num': last_response,
            'title': thread['title']
        });
    return 'updated.'

@app.route('/delete')
def delete_all():
    datastore.delete_all()
    return 'deleted.'

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500