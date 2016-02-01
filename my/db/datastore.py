# -*- coding: utf-8 -*-
u"""
    Google App Engine Datastore ラッパー
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
from google.appengine.ext import db

class Thread (db.Model):
    u"""
        スレッドを表すデータモデル
    """
    id = db.IntegerProperty()
    host_url = db.StringProperty()

class Response (db.Model):
    u"""
        レスを表すデータモデル
    """