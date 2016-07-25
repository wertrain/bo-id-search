# -*- coding: utf-8 -*-
u"""
    Google App Engine Datastore ラッパー
    __author__ = 'wertrain'
    __version__ = '0.1'
"""
import json
from datetime import datetime
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
    u"""
        タスクで作成された複数のエントリーを表すデータモデル
    """
    responses = db.TextProperty(default='')

class Task (db.Model):
    u"""
        一つのタスクを表すデータモデル
    """
    url = db.StringProperty()
    id = db.StringProperty()
    dat_url = db.StringProperty()
    executed = db.DateTimeProperty(auto_now_add=True)

class ImportData  (db.Model):
    files = db.StringListProperty(default=[])

def update_task(id, param):
    task = __get_task(id)
    if task is None:
        task = Task()
        task.id = id
        task.url = param.get('url')
        task.dat_url = param.get('dat_url')
        task.put()
    else:
        # id は存在するが URL が違う場合は、移転されたと見なして URL を更新しておく
        if task.url != param.get('url'):
            task.url = param.get('url')
            task.put()
    return task

def get_next_task():
    task = db.Query(Task).order('executed').get()
    if task is None:
        return None
    task.executed = datetime.now()
    task.put()
    return task

def __get_task(id):
    return db.Query(Task).filter('id =', id).get()

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

def set_import_list(list):
    data = db.Query(ImportData).get()
    if data is None:
        data = ImportData()
    data.files = list
    data.put()

def delete_all():
    for thread in Thread.all():
        thread.delete()
    for response in Response.all():
        response.delete()
    for user in PSNUser.all():
        user.delete()
    for entries in TaskEntries.all():
        entries.delete()
    for task in Task.all():
        task.delete()
