#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import category
import search
from google.appengine.api import users
from webapp2_extras.appengine.users import login_required

from lib import templates


class MainHandler(webapp2.RequestHandler):
  @login_required
  def get(self):
    template = templates.get('index.html')
    user = users.get_current_user()
    template_values = {
        'user' : user.nickname(),
        'logout_url': users.create_logout_url("/")
    }
    self.response.write(template.render(template_values))

  def search(self):
    self.response.write(self.request.POST)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    webapp2.Route('/search', handler='search.SearchHandler', handler_method='search', methods=['POST']),
    webapp2.Route('/category/new', handler='category.CategoryHandler', handler_method='new'),
    webapp2.Route('/category/save', handler='category.CategoryHandler', handler_method='save', methods=['POST']),
    webapp2.Route('/category/mine', handler='category.CategoryHandler', handler_method='mine', methods=['GET']),
    webapp2.Route('/category/all', handler='category.CategoryHandler', handler_method='all', methods=['GET']),
    webapp2.Route('/category/vote/submit', handler='category.CategoryHandler', handler_method='submit_vote', methods=['POST']),
    webapp2.Route('/category/vote/<cat_id>', handler='category.CategoryHandler', handler_method='vote'),
    webapp2.Route('/category/export/<cat_id>', handler='category.CategoryHandler', handler_method='export'),
    webapp2.Route('/category/export', handler='category.CategoryHandler', handler_method='show_export'),
    webapp2.Route('/category/results', handler='category.CategoryHandler', handler_method='results', methods=['GET']),
    webapp2.Route('/category/result/<cat_id>', handler='category.CategoryHandler', handler_method='result', methods=['GET'])
], debug=True)

