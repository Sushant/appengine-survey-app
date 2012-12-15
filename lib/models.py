from google.appengine.ext import db

class Category(db.Expando):
  name = db.StringProperty()
  owner = db.UserProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Item(db.Expando):
  name = db.StringProperty()
  category = db.ReferenceProperty(Category, collection_name='items')
  wins = db.IntegerProperty()
  losses = db.IntegerProperty()

class Comment(db.Expando):
  text = db.TextProperty()
  item = db.ReferenceProperty(Item, collection_name='comments')
  owner = db.UserProperty()
