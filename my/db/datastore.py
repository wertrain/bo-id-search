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
    response_num = db.IntegerProperty()

class Response (db.Model):
    u"""
        レスを表すデータモデル
    """
    number = db.IntegerProperty()
    name = db.StringProperty()
    mail = db.StringProperty()
    body = db.StringProperty()
    thread = db.ReferenceProperty(Thread)
    at = db.DateTimeProperty(auto_now_add=False)
#    users = db.ListProperty(db.Key, default=[])

class PSNUser (db.Model):
    u"""
        PSN ユーザーを表すデータモデル
    """
    id = db.StringProperty()
    count = db.IntegerProperty()
    responses = db.ListProperty(db.Key, default=[])

def create_response(param):
    response = Response()
    response.number = int(param['number'])
        'number': unicode(base[0], 'utf-8'), 
        'name': unicode(base[1], 'utf-8', 'ignore'),
        'id': unicode(info[2][3:], 'utf-8'), 
        'datetime': tdatetime
        
def update_psn_user(id, key):
    user = db.Query(PSNUser).filter('id =', id).get()
    if user == None:
        user = PSNUser()
    user.id = id
    user.count = user.count + 1
    user.responses.append(key)
    user.put()
    return user