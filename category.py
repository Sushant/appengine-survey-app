import cgi
import logging
import random
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from datetime import datetime, timedelta
from webapp2_extras.appengine.users import login_required
from lib import templates
from lib.models import Category
from lib.models import Comment
from lib.models import Item
from xml.dom import minidom

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
      cat_name = cgi.escape(self.request.POST['catName'])
      expiry = int(self.request.POST['expiry'])
      expiry = datetime.now() + timedelta(days=expiry)
      category_exists = self._check_if_category_exists(cat_name)
      if category_exists:
        self._show_home_page({'error': 'Error saving category, a category by that name already exists'})
        return

      item_list = []
      for param in self.request.POST.items():
        if param[0] != 'catName' and param[0] != 'expiry':
          if param[1] != '':
            item_list.append(cgi.escape(param[1]))
      if len(item_list) < 2:
        self._show_home_page({'error': 'Error saving category, please retry by creating at least 2 items for the category'})
        return

      category = Category(name=cat_name, owner=user, expiry=expiry)
      category.put()
      for item_name in item_list:
        item = Item(name=item_name, category=category, wins=0, losses=0)
        item.put()
        self._show_home_page({'success': 'Saved category "%s" successfully' % cat_name})
    else:
      self.redirect(users.create_login_url("/"))


  def _check_if_category_exists(self, cat_name):
    user = users.get_current_user()
    categories = list(db.GqlQuery('SELECT * from Category where owner=:1 AND name=:2', user, cat_name))
    if len(categories):
      return True
    return False


  @login_required
  def mine(self):
    user = users.get_current_user()
    categories = db.GqlQuery('SELECT * from Category where owner=:1', user)
    template = templates.get('user_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      if category.expiry < datetime.now():
        expires_in = 'expired'
      else:
        expires_in = (category.expiry - datetime.now()).days
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id(),
          'expires_in': expires_in}
      category_list.append(cat)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'categories': category_list
    }
    self.response.write(template.render(template_values))

  @login_required
  def all(self):
    categories = db.GqlQuery('SELECT * from Category')
    template = templates.get('all_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      if category.expiry < datetime.now():
        expires_in = 'expired'
      else:
        expires_in = (datetime.now() - category.expiry).days
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id(),
          'owner': category.owner.nickname(), 'expires_in': expires_in}
      category_list.append(cat)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'categories': category_list
    }
    self.response.out.write(template.render(template_values))


  @login_required
  def vote(self, cat_id):
    user = users.get_current_user()
    template = templates.get('vote.html')
    category = Category.get_by_id(int(cat_id))
    items = category.items
    selected_items = list(random.sample(set(items), 2))
    item1 = self.get_item_dict(selected_items[0])
    item2 = self.get_item_dict(selected_items[1])
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'category': category.name,
        'item1': item1,
        'item2': item2
    }
    self.response.out.write(template.render(template_values))


  def get_item_dict(self, item):
    user = users.get_current_user()
    item_dict = {'name': item.name, 'id': item.key().id()}
    item_comment = list(item.comments.filter('owner =', user))
    if item_comment:
      item_dict['comment'] = item_comment[0].text
    return item_dict

  def submit_vote(self):
    user = users.get_current_user()
    if user:
      item1_id = int(self.request.POST['item1'])
      item2_id = int(self.request.POST['item2'])
      comment1 = self.request.POST['comment' + str(item1_id)]
      comment2 = self.request.POST['comment' + str(item2_id)]
      selected_id = int(self.request.POST['optionsRadios'])
      item1 = Item.get_by_id(item1_id)
      item2 = Item.get_by_id(item2_id)
      if selected_id == item1_id:
        item1.wins += 1
        item1.put()
        item2.losses += 1
        item2.put()
      else:
        item2.wins += 1
        item2.put()
        item1.losses += 1
        item1.put()
      if comment1:
        comment = Comment(text=comment1, owner=user, item=item1)
        comment.put()
      if comment2:
        comment = Comment(text=comment2, owner=user, item=item2)
        comment.put()
      self._show_home_page({'success': 'Successfully saved the vote'})
    else:
      self.redirect(users.create_login_url("/"))

  def _show_home_page(self, msg_dict):
    template = templates.get('index.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'message': msg_dict
    }
    self.response.write(template.render(template_values))

  @login_required
  def results(self):
    categories = db.GqlQuery('SELECT * from Category')
    template = templates.get('results_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id(),
          'owner': category.owner.nickname()}
      category_list.append(cat)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'categories': category_list
    }
    self.response.out.write(template.render(template_values))

  @login_required
  def result(self, cat_id):
    template = templates.get('results_items.html')
    user = users.get_current_user()
    category = Category.get_by_id(int(cat_id))
    items = category.items
    item_list = []
    for item in items:
      try:
        percentage = item.wins * 100.0 / (item.wins + item.losses)
        percentage_str = '%.2f' % percentage
      except ZeroDivisionError:
        percentage = -1
        percentage_str = '-'
      item_dict = {'id': item.key().id(), 'name': item.name,
          'wins': item.wins, 'losses': item.losses,
          'comments': item.comments, 'percentage': percentage,
          'comment_count': item.comments.count(),
          'percentage_str': percentage_str}
      item_list.append(item_dict)
    item_list = sorted(item_list, key=lambda k: k['percentage'], reverse=True)
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'items': item_list,
        'category': category.name
    }
    self.response.out.write(template.render(template_values))


  @login_required
  def show_export(self):
    categories = db.GqlQuery('SELECT * from Category')
    template = templates.get('all_category.html')
    user = users.get_current_user()
    category_list = []
    for category in categories:
      cat = {'name': category.name, 'date': str(category.date),
          'items': category.items.count(), 'id': category.key().id(),
          'owner': category.owner.nickname()}
      category_list.append(cat)
    template_values = {
        'page'       : 'export',
        'user'       : user.nickname(),
        'logout_url' : users.create_logout_url("/"),
        'categories' : category_list
    }
    self.response.out.write(template.render(template_values))


  @login_required
  def export(self, cat_id):
    category = Category.get_by_id(int(cat_id))
    self.response.headers['Content-Type'] = 'text/xml'
    xml_str = '<CATEGORY><NAME>' + category.name + '</NAME>'
    for item in category.items:
      xml_str += '<ITEM><NAME>' + item.name + '</NAME></ITEM>'
    xml_str += '</CATEGORY>'
    self.response.out.write('<?xml version="1.0" encoding="ISO-8859-1"?>' + xml_str)


  @login_required
  def delete(self, cat_id):
    category = Category.get_by_id(int(cat_id))
    cat_name = category.name
    for item in category.items:
      item.delete()
    category.delete()
    self._show_home_page({'success': 'Successfully deleted category "%s"' % cat_name})


  def import_xml(self):
    user = users.get_current_user()
    if user:
      xml_file = self.request.POST.multi['file'].file
      xml = ''
      for line in xml_file.readlines():
        xml += line.strip()
      dom = minidom.parseString(xml)
      cat_name = dom.getElementsByTagName('CATEGORY')[0].firstChild.childNodes[0].data
      items = dom.getElementsByTagName('ITEM')
      item_list = []
      for item in items:
        item_name = item.firstChild.childNodes[0].data
        item_list.append(item_name)
      category_exists = self._check_if_category_exists(cat_name)

      if category_exists:
        self._edit_category(cat_name, item_list)
      else:
        category = Category(name=cat_name, owner=user)
        category.put()
        for item_name in item_list:
          item = Item(name=item_name, category=category, wins=0, losses=0)
          item.put()
      self._show_home_page({'success': 'Successfully imported category "%s"' % cat_name})
    else:
      self.redirect(users.create_login_url("/"))


  def _edit_category(self, cat_name, new_item_list):
    user = users.get_current_user()
    categories = list(db.GqlQuery('SELECT * from Category where owner=:1 AND name=:2', user, cat_name))
    category = categories[0]
    old_item_list = []
    for item in category.items:
      old_item_list.append(item.name)
    items_to_add = list(set(new_item_list) - set(old_item_list))
    items_to_delete = list(set(old_item_list) - set(new_item_list))

    for item_name in items_to_add:
      item = Item(name=item_name, category=category, wins=0, losses=0)
      item.put()

    deleted_items = category.items.filter('name IN', items_to_delete)
    for item in deleted_items:
      item.delete()



  def import_page(self):
    template = templates.get('import.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/")
    }
    self.response.write(template.render(template_values))


  def show_edit(self, cat_id):
    category = Category.get_by_id(int(cat_id))
    expires_in = (category.expiry - datetime.now()).days
    if expires_in < 0:
      expires_in = 0
    template = templates.get('edit_page.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/"),
        'items': category.items,
        'category': category,
        'expires_in': expires_in,
        'item_count': category.items.count()
    }
    self.response.write(template.render(template_values))

  def edit(self):
    user = users.get_current_user()
    if user:
      cat_name = cgi.escape(self.request.POST['catName'])

      item_list = []
      for param in self.request.POST.items():
        if param[0] != 'catName':
          if param[1] != '':
            item_list.append(cgi.escape(param[1]))
      if len(item_list) < 2:
        self._show_home_page({'error': 'Error saving category, please retry by creating at least 2 items for the category'})
        return

      self._edit_category(cat_name, item_list)
      self._show_home_page({'success': 'Saved category "%s" successfully' % cat_name})
    else:
      self.redirect(users.create_login_url("/"))
