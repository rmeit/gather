import os, sys
import uuid
from flask import (Flask, redirect, render_template, request, json, jsonify, url_for)
import asyncio

app = Flask(__name__)

def message(input):
    """Return an error message as a JSON object."""
    return jsonify({'message': input})

def format_request(request):
    return json.loads(request.data)

class user:
    users = {}
    """A unique user of the app."""
    def __init__(self, name, group, creator=False):
        self.name = name
        self.user_id = uuid.uuid4()
        self.group = group
        self.creator = creator
        user.users[self.user_id] = self

    def set_preferences(self, preferences):
        self.preferences = preferences

    def __str__(self) -> str:
        return self.name + " : " + self.preferences
    
class group:
    groups = {}
    id_tracker = 10000
    """A group of users. Has a creator."""
    def __init__(self, creator_name):
        self.group_id = group.id_tracker
        group.id_tracker += 1
        if group.id_tracker > 99990:
            group.id_tracker = 10000
        self.creator = user(creator_name, self, creator=True)
        self.users = {self.creator.user_id: self.creator}
        group.groups[self.group_id] = self
    
    def get_info(self):
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
    
@app.route('/create_group', methods=['POST'])
def create_group():
   """Creates a new group. Assigns group_id. Adds the creator to the group as the first user."""
   content = format_request(request)
   creator_name = content['name']
   if creator_name:
        print('Request to create received with creator_name=%s' % creator_name)
        created_group = group(creator_name)
        print(created_group.group_id)
        return jsonify({'user_id': created_group.creator.user_id, 'group_id': created_group.group_id})
   else:
       print('Request for page received with no name or blank name -- redirecting')
       return message("No name or blank name provided.")
   
@app.route('/join_group', methods=['POST'])
def join_group():
    """Join an existing group. Adds the user to the group."""
    content = format_request(request)
    group_id = content['group_id']
    user_name = content['user_name']
    if group_id and user_name:
        print('Request to join received with group_id=%s and user_name=%s' % (group_id, user_name))
        if group_id not in group.groups:
            print("No group with that group_id exists.")
            return {}
        this_group = group.groups[group_id]
        new_user = this_group.add_user(user_name)
        return jsonify({'user_id': new_user.user_id})
    else:
        print('Request for page received with no name or blank name -- redirecting')
        return message("No group_id or user_name provided.")
    
@app.route('/set_preferences', methods=['POST'])
def set_preferences():
    """Set the self-described preferences of a user."""
    content = format_request(request)
    user_id = content['user_id']
    preferences = content['preferences']
    if user_id and preferences:
        print('Request to set preferences received with user_id=%s and preferences=%s' % (user_id, preferences))
        if user_id not in user.users:
            return "No user with that user_id exists."
        this_user = user.users[user_id]
        this_user.set_preferences(preferences)
        return jsonify(content)
    else:
        print('Request for page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    
@app.route('/find_recommendations', methods=['POST'])
def find_recommendations():
    """Feed preferences to the model and find recommendations for a group. Only available to the group creator."""
    user_id = format_request(request)['user_id']
    if user_id:
        print('Request to find recommendations received with user_id=%s' % (user_id))
        if user_id not in user.users:
            return "No user with that user_id exists."
        this_user = user.users[user_id]
        if not this_user.creator:
            return "Only the group creator can find recommendations."
        this_group = this_user.group
        async def find_recommendations():
            return this_group.find_recommendations()
        _ = find_recommendations()
        return jsonify({'user_id': user_id})
    else:
        print('Request for page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))
    
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """If recommendations are ready, return recommendations as a text string. Else do nothing."""
    user_id = format_request(request)['user_id']
    if user_id:
        print('Request to get recommendations received with user_id=%s' % (user_id))
        if user_id not in user.users:
            return "No user with that user_id exists."
        this_user = user.users[user_id]
        this_group = this_user.group
        if this_group.recommendations == None:
            return message("No recommendations have been found yet for this group.")
        return jsonify({'recommendations': this_group.recommendations})
    else:
        print('Request for page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))

@app.route('/')
def index():
   print('Request for index page received')
   return True

if __name__ == '__main__':
   isDev = sys.argv[1] == 'dev'
   if isDev:
    app.run(debug=True, host='0.0.0.0', port=80)
   else:
    app.run()