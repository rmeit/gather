import os
import uuid
# from flask import (Flask, redirect, render_template, request,
#                    send_from_directory, url_for)

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

groups = {}

class user:
    """A unique user of the app."""
    def __init__(self, name, creator=False):
        self.name = name
        self.user_id = uuid.uuid4()
        self.creator = creator

    def set_preferences(self, preferences):
        self.preferences = preferences

    def __str__(self) -> str:
        return self.name + " : " + self.preferences
    
class group:
    """A group of users. Has a creator."""
    def __init__(self, creator_name):
        self.creator = user(creator_name, creator=True)
        self.group_id = uuid.uuid4()
        self.users = [self.creator]
        groups[self.group_id] = self
        return self.group_id
    
    def add_user(self, user_name):
        self.users.append(user(user_name, creator=False))
        return True
    
    def set_preferences(self, user_name, preferences):
        for user in self.users:
            if user.name == user_name:
                user.set_preferences(preferences)
                return True
        return False
    
    def get_recommendations(self):
        ### TODO ###
        return True
    
    def delete(self):
        ### TODO ###
        return True
  

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run()