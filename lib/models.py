from google.appengine.ext import db

class Category(db.Expando):
  name = db.StringProperty()
  owner = db.UserProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Item(db.Expando):
  name = db.StringProperty()
  cat_id = db.StringProperty()
  wins = db.IntegerProperty()
  losses = db.IntegerProperty()

class Comment(db.Expando):
  text = db.TextProperty()
  item_id = db.StringProperty()
  owner = db.UserProperty()
