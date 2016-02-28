# -*- coding: utf-8 -*-
from api import apis

from flask import Flask, render_template
app = Flask(__name__)
app.register_blueprint(apis)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def top():
    """トップページを表示する"""
    return render_template('home.html', page_type=0)

@app.route('/ranking')
def ranking():
    """ランキングページを表示する"""
    return render_template('ranking.html', page_type=1)

@app.route('/about')
def about():
    """このサイトについてページを表示する"""
    return render_template('about.html', page_type=2)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500