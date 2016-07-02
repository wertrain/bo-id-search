# -*- coding: utf-8 -*-
import logging
import json
from api import apis

from my.db import datastore
from flask import Flask, render_template
from google.appengine.api import memcache

app = Flask(__name__, static_folder='static')
app.register_blueprint(apis)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
logging.getLogger().setLevel(logging.DEBUG)
    
@app.route('/')
def top():
    """トップページを表示する"""
    return render_template('home.html', page_type=0)

@app.route('/ranking')
def ranking():
    """ランキングページを表示する"""
    memcache_key = 'ranking';
    users = memcache.get(memcache_key)
    if users is None:
        users = json.dumps(datastore.get_ranking(50), indent=0)
        memcache.add(memcache_key, users, 60 * 60 * 24)
    users = json.loads(users)
    return render_template('ranking.html', page_type=1, users=users)

@app.route('/about')
def about():
    """このサイトについてページを表示する"""
    memcache_key = 'user_and_thread_count';
    counts = memcache.get(memcache_key)
    if counts is None:
        counts = json.dumps({
            'user': datastore.get_all_psnuser_count(),
            'thread': datastore.get_all_thread_count()
        }, indent=0)
        memcache.add(memcache_key, counts, 60 * 60 * 24)
    counts = json.loads(counts)
    return render_template('about.html', page_type=2, counts=counts)

@app.route('/id/<psnid>')
def search(psnid):
    """ID 詳細を表示する"""
    user = datastore.get_psn_user(psnid)
    params = []
    if user is not None:
        for key in user.responses[:5]:
            response = datastore.get_response_from_key(key)
            params.append(response)
    return render_template('id.html', user=user, id=psnid, params=params, page_type=0)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500