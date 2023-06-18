import os
import uuid
# from flask import (Flask, redirect, render_template, request,
#                    send_from_directory, url_for)

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

app = Flask(__name__)

users = {}
class user:
    """A unique user of the app."""
    def __init__(self, name, group, creator=False):
        self.name = name
        self.user_id = uuid.uuid4()
        self.group = group
        self.creator = creator
        users[self.user_id] = self

    def set_preferences(self, preferences):
        self.preferences = preferences

    def __str__(self) -> str:
        return self.name + " : " + self.preferences
    
groups = {}
group_id_tracker = 10000
class group:
    """A group of users. Has a creator."""
    def __init__(self, creator_name):
        self.group_id = group_id_tracker
        group_id_tracker += 1
        if group_id_tracker > 99990:
            group_id_tracker = 10000
        self.creator = user(creator_name, self, creator=True)
        self.users = {self.creator.user_id: self.creator}
        groups[self.group_id] = self
        return self.creator.user_id, self.group_id
    
    def add_user(self, user_name):
        new_user = user(user_name, self)
        self.users[new_user.user_id] = new_user
        return new_user.user_id
    
    def set_preferences(self, user_name, preferences):
        for user in self.users:
            if user.name == user_name:
                user.set_preferences(preferences)
                return True
        return False
    
    def find_recommendations(self):
        """Feed the group's preferences to the model and get recommendations."""
        ### TODO ###
        self.recommendations = None
        return self.recommendations
    
    def get_recommendations(self):
        """Return the recommendations for the whole group."""
        return self.recommendations
    
    def delete(self):
        ### TODO ###
        return True

@app.route('/create_room', methods=['POST'])
def create_room():
   """Creates a new group. Assigns group_id. Adds the creator to the group as the first user."""
   creator_name = request.form.get('creator_name')
   if creator_name:
         print('Request to create received with creator_name=%s' % creator_name)
         creator_id, new_group = group(creator_name)
         return '''
              <h1>Your user id is: {}</h1>
              <h1>Your group id is: {}'''.format(creator_id, new_group.group_id)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
   
@app.route('/join_room', methods=['POST'])
def join_room():
    """Join an existing group. Adds the user to the group."""
    group_id = request.form.get('group_id')
    user_name = request.form.get('user_name')
    if group_id and user_name:
        print('Request to join received with group_id=%s and user_name=%s' % (group_id, user_name))
        if group_id not in groups:
            return "No group with that group_id exists."
        this_group = groups[group_id]
        new_user = this_group.add_user(user_name)
        return '''<h1>Your user id is: {}'''.format(new_user.user_id, group_id)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    
@app.route('/set_preferences', methods=['POST'])
def set_preferences():
    """Set the self-described preferences of a user."""
    user_id = request.form.get('user_id')
    preferences = request.form.get('preferences')
    if user_id and preferences:
        print('Request to set preferences received with user_id=%s and preferences=%s' % (user_id, preferences))
        if user_id not in users:
            return "No user with that user_id exists."
        this_user = users[user_id]
        this_user.set_preferences(preferences)
        return '''<h1>Your preferences have been set.'''
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    
@app.route('/find_recommendations', methods=['POST'])
def find_recommendations():
    """Feed preferences to the model and find recommendations for a group. Only available to the group creator."""
    user_id = request.form.get('user_id')
    if user_id:
        print('Request to find recommendations received with user_id=%s' % (user_id))
        if user_id not in users:
            return "No user with that user_id exists."
        this_user = users[user_id]
        if not this_user.creator:
            return "Only the group creator can find recommendations."
        this_group = this_user.group
        this_group.find_recommendations()
        return '''<h1>Recommendations have been found.'''
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """Return recommendations as a text string."""
    user_id = request.form.get('user_id')
    if user_id:
        print('Request to get recommendations received with user_id=%s' % (user_id))
        if user_id not in users:
            return "No user with that user_id exists."
        this_user = users[user_id]
        this_group = this_user.group
        return this_group.get_recommendations()
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

if __name__ == '__main__':
   app.run()