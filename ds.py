from datetime import datetime
from google.cloud import datastore

def insert(author, message):
  """
  Datastoreへ1件のEntityを追加する

  Parameters
  ----------
  author : str
    名前
  message : str
    メッセージ
  
  Returns
  -------
  entity : dict
    Datastoreの1Entity
  """
  client = datastore.Client()
  key = client.key("Greeting")

  entity = datastore.Entity(key=key)
  entity["author"] = author
  entity["message"] = message
  entity["created"] = datetime.now()

  client.put(entity)
  entity["id"] = entity.key.id

  return entity

def get_all():
  """
  DatastoreのEntityをすべて取得する

  Returns
  -------
  greetings : list
    DatastoreのすべてのEntityのリスト
  """
  client = datastore.Client()
  query = client.query(kind="Greeting")
  query.order = "-created"
  greetings = list(query.fetch())
  for entity in greetings:
    entity["id"] = entity.key.id
  
  return greetings

def get_by_id(key_id):
  """
  Datastoreのkey_idに合致するEntityを取得する

  Parameters
  ----------
  key_id : str
    EntityのKey

  Returns
  -------
  entity : dict
    Datastoreから取得したEntity
  """
  client = datastore.Client()
  key = client.key("Greeting", int(key_id))
  entity = client.get(key=key)
  if entity:
    entity["id"] = entity.key.id
  
  return entity

def update(entity):
  """
  Datastoreの1Entityを更新する

  Parameters
  ----------
  entity : dict
    更新するEntity

  Returns
  -------
  entity : dict
    更新したEntity
  """
  if "id" in entity: del entity["id"]
  client = datastore.Client()
  client.put(entity)
  entity["id"] = entity.key.id

  return entity

def delete(key_id):
  """
  Datastoreの1Entityを削除する

  Parameters
  ----------
  key_id : str
    削除対象EntityのKey
  """
  client = datastore.Client()
  key = client.key("Greeting", int(key_id))
  client.delete(key)

def insert_comment(parent_id, message):
  """
  Datastoreの1Entityを親とした子Entityを登録する
  なお、登録するKindは「Comment」

  Parameters
  ----------
  parent_id : str
    親Entityのkey
  message: str
    登録するコメント

  Returns
  -------
  entity : dict
    更新したEntity
  """
  client = datastore.Client()
  parent_key = client.key("Greeting", int(parent_id))
  key = client.key("Comment", parent=parent_key)
  entity = datastore.Entity(key=key)
  entity["message"] = message
  entity["created"] = datetime.now()
  client.put(entity)
  entity["id"] = entity.key.id

  return entity

def get_comments(parent_id):
  """
  Datastoreの1Entityを親とした子Entityをすべて取得する
  なお、取得するKindは「Comment」

  Parameters
  ----------
  parent_id : str
    選択したEntityのkey

  Returns
  -------
  entities : list
    取得したComment Entityのリスト
  """
  client = datastore.Client()
  ancestor = client.key("Greeting", int(parent_id))
  query = client.query(kind="Comment", ancestor=ancestor) # 親キーを使ってAncestor queryを実行する
  entities = list(query.fetch())
  for entity in entities:
    entity["id"] = entity.key.id

  return entities
