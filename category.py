import cgi
import logging
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from webapp2_extras.appengine.users import login_required
from lib import templates
from lib.models import Category
from lib.models import Item

class CategoryHandler(webapp2.RequestHandler):
  @login_required
  def new(self):
    template = templates.get('category.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/")
    }
    self.response.write(template.render(template_values))

  # Cannot use login_required decorator for POST
  def save(self):
    user = users.get_current_user()
    if user:
      category = None
      cat_name = self.request.POST['catName']
      category = Category(name=cat_name, owner=user)
      category.put()

      for param in self.request.POST.items():
        if param[0] != 'catName':
          if category:
            item = Item(name=cgi.escape(param[1]), category=category,
                wins=0, losses=0)
            item.put()
      self.response.out.write('%s has items: ' % category.key())
      for item in category.items:
        self.response.out.write(item.name)
    else:
      self.redirect(users.create_login_url("/"))


  @login_required
  def mine(self):
    user = users.get_current_user()
    categories = db.GqlQuery('SELECT * from Category where owner=:1', user)
    self.response.out.write('Categories: ')
    for cat in categories:
      self.response.out.write(cat.name + ' ' + str(cat.date) + '\n')

  @login_required
  def all(self):
    categories = db.GqlQuery('SELECT * from Category')
    self.response.out.write('Categories: ')
    for cat in categories:
      self.response.out.write(cat.name + ' ' + str(cat.date) + '\n')


