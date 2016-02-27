# -*- coding: utf-8 -*-
u"""
    Google App Engine Datastore ラッパー
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import json
from google.appengine.ext import db

class Thread (db.Model):
    u"""
        スレッドを表すデータモデル
    """
    id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    response_num = db.IntegerProperty()

class Response (db.Model):
    u"""
        レスを表すデータモデル
    """
    number = db.IntegerProperty()
    author = db.StringProperty()
    mail = db.StringProperty()
    body = db.TextProperty()
    thread = db.ReferenceProperty(Thread)
    at = db.DateTimeProperty(auto_now_add=False)
#    users = db.ListProperty(db.Key, default=[])

class PSNUser (db.Model):
    u"""
        PSN ユーザーを表すデータモデル
    """
    id = db.StringProperty()
    count = db.IntegerProperty(default=0)
    responses = db.ListProperty(db.Key, default=[])

class TaskEntries  (db.Model):
    ids = db.TextProperty(default='')
    responses = db.TextProperty(default='')

def create_response(param):
    response = Response()
    response.number = param.get('number')
    response.author = param.get('author')
    response.mail = param.get('mail')
    response.body = param.get('body')
    response.thread = param.get('thread')
    response.at = param.get('at')
    response.put()
    return response

def get_psn_user(id):
    return db.Query(PSNUser).filter('id =', id).get()

def update_psn_user(id, key):
    user = get_psn_user(id)
    if user == None:
        user = PSNUser()
    user.id = id
    user.count = user.count + 1
    user.responses.append(key)
    user.put()
    return user

def get_thread(id):
    return db.Query(Thread).filter('id =', id).get()

def update_thread(id, param={}):
    thread = get_thread(id)
    if thread == None:
        thread = Thread()
    thread.id = id
    thread.url = param.get('url')
    thread.response_num = param.get('response_num')
    thread.title = param.get('title')
    thread.put()
    return thread

def add_task(new_ids, new_responses):
    task = db.Query(TaskEntries).get()
    if task == None:
        task = TaskEntries()
    
    ids = [] if len(task.ids) == 0 else json.loads(task.ids)
    ids.extend(new_ids)
    task.ids = json.dumps(ids)
    responses = [] if len(task.responses) == 0 else json.loads(task.responses)
    responses.extend(new_responses)
    task.responses = json.dumps(responses)
    task.put()

def get_all_ids():
    ids = []
    for user in PSNUser.all().order('-count'):
        ids.append(user.id)
    return ids

def delete_all():
    for thread in Thread.all():
        thread.delete()
    for response in Response.all():
        response.delete()
    for user in PSNUser.all():
        user.delete()
    for task in TaskEntries.all():
        task.delete()