from google.appengine.api import users

def user_auth(handler_method):
  def check_login(self, *args, **kwargs):
    user = users.get_current_user()
    if not user:
      return self.redirect(users.create_login_url(self.request.url))
    else:
      handler_method(self, *args, **kwargs)

    return check_login
