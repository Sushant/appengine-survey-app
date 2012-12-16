import cgi
import webapp2
from lib import templates
from google.appengine.api import users
from google.appengine.ext import db
from lib.models import Category
from lib.models import Item

class SearchHandler(webapp2.RequestHandler):
  def search(self):
    user = users.get_current_user()
    if user:
      template = templates.get('search.html')
      search_term = cgi.escape(self.request.POST['searchTerm'])
      categories = Category.all().search(search_term, properties=['name'])
      entity_list = []
      for category in categories:
        entity_list.append({'type': 'Category', 'name': category.name})

      items = Item.all().search(search_term, properties=['name'])
      for item in items:
        entity_list.append({'type': 'Item', 'name': item.name})

      template_values = {
          'user' : user.nickname(),
          'logout_url': users.create_logout_url("/"),
          'entities': entity_list
      }
      self.response.write(template.render(template_values))
    else:
      self.redirect(users.create_login_url("/"))
