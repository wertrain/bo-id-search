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
    id = db.StringProperty()
    host_url = db.StringProperty()

class Response (db.Model):
    u"""
        レスを表すデータモデル
    """
    name = db.StringProperty()
    mail = db.StringProperty()
    body = db.StringProperty()
    thread = db.ReferenceProperty(Thread)
    at = db.DateTimeProperty(auto_now_add=False)
    users = db.ListProperty(db.Key)

class PSNUser (db.Model):
    u"""
        PSN ユーザーを表すデータモデル
    """
    id = db.StringProperty()
    count = db.IntegerProperty()
    responses = db.ListProperty(db.Key)