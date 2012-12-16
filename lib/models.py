from google.appengine.ext import db
from google.appengine.ext import search

class Category(search.SearchableModel):
  name = db.StringProperty()
  owner = db.UserProperty()
  date = db.DateTimeProperty(auto_now_add=True)

  @classmethod
  def SearchableProperties(cls):
    return [['name']]

class Item(search.SearchableModel):
  name = db.StringProperty()
  category = db.ReferenceProperty(Category, collection_name='items')
  wins = db.IntegerProperty()
  losses = db.IntegerProperty()

  @classmethod
  def SearchableProperties(cls):
    return [['name']]

class Comment(db.Expando):
  text = db.TextProperty()
  item = db.ReferenceProperty(Item, collection_name='comments')
  owner = db.UserProperty()
