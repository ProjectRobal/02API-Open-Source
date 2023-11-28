from datetime import datetime, timedelta
import time
from django.contrib import auth
import logging





'''
A middleware to check if user session has expired
'''

class SessionChecker:
  def __init__(self, get_response):
        self.get_response = get_response

  def __call__(self, request):

    if not request.user.is_authenticated:
      return self.get_response(request)

    try:
      if time.time() - request.session['last_touch'] > request.session["session_time"]:
        auth.logout(request)
        logging.debug("Session expired")
        del request.session['last_touch']
        del request.session["session_time"]
        return self.get_response(request)
    except KeyError:
      pass
    logging.debug("Session regenerated")
    request.session['last_touch'] = int(time.time())

    response = self.get_response(request)

    return response
    