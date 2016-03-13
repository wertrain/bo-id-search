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
    authorid = db.StringProperty()
#    users = db.ListProperty(db.Key, default=[])

class PSNUser (db.Model):
    u"""
        PSN ユーザーを表すデータモデル
    """
    id = db.StringProperty()
    count = db.IntegerProperty(default=0)
    responses = db.ListProperty(db.Key, default=[])

class TaskEntries (db.Model):
    responses = db.TextProperty(default='')

class ProxyData (db.Model):
    url = db.StringProperty(default='')

def create_response(param):
    response = Response()
    response.number = param.get('number')
    response.author = param.get('author')
    response.mail = param.get('mail')
    response.body = param.get('body')
    response.thread = param.get('thread')
    response.at = param.get('at')
    response.authorid = param.get('authorid')
    response.put()
    return response

def get_psn_user(id):
    return db.Query(PSNUser).filter('id =', id).get()

def update_psn_user(id, key):
    user = get_psn_user(id)
    if user is None:
        user = PSNUser()
    user.id = id
    user.count = user.count + 1
    user.responses.append(key)
    user.put()
    return user

def increment_user_count(id, keys):
    user = get_psn_user(id)
    if user is None:
        user = PSNUser()
    user.id = id
    user.count = user.count + len(keys)
    for key in keys:
        user.responses.append(key)
    user.put()
    return user

def get_thread(id):
    return db.Query(Thread).filter('id =', id).get()

def update_thread(id, param={}):
    thread = get_thread(id)
    if thread is None:
        thread = Thread()
    thread.id = id
    thread.url = param.get('url')
    thread.response_num = param.get('response_num')
    thread.title = param.get('title')
    thread.put()
    return thread

def add_entry_task(new_responses):
    task = db.Query(TaskEntries).get()
    if task is None:
        task = TaskEntries()
    responses = [] if len(task.responses) == 0 else json.loads(task.responses)
    responses.extend(new_responses)
    task.responses = json.dumps(responses)
    task.put()

def set_entry_task(new_responses):
    task = db.Query(TaskEntries).get()
    if task is None:
        task = TaskEntries()
    task.responses = json.dumps(new_responses)
    task.put()

def get_entry_task():
    task = db.Query(TaskEntries).get()
    if task is None:
        task = TaskEntries()
    responses = [] if len(task.responses) == 0 else json.loads(task.responses)
    return responses

def get_ranking(limit=50):
    users = []
    for user in db.Query(PSNUser).order('-count').fetch(limit=limit):
        users.append({
            'id': user.id,
            'count': user.count
        })
    return users

def get_all_ids():
    ids = []
    for user in PSNUser.all().order('-count'):
        ids.append(user.id)
    return ids

def get_response_from_key(key):
    return db.get(key)

def get_all_psnuser_count():
    return db.Query(PSNUser).count()

def get_all_thread_count():
    return db.Query(Thread).count()

def get_proxy_url():
    data = db.Query(ProxyData).get()
    if data is None:
        return None
    return data.url

def set_proxy_url(url):
    data = db.Query(ProxyData).get()
    if data is None:
        data = ProxyData()
    data.url = url
    data.put()

def delete_all():
    for thread in Thread.all():
        thread.delete()
    for response in Response.all():
        response.delete()
    for user in PSNUser.all():
        user.delete()
    for task in TaskEntries.all():
        task.delete()
    #for data in ProxyData.all():
    #    data.delete()
