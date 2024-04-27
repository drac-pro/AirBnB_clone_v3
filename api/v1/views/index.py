#!/usr/bin/python3
"""index file"""
from flask import jsonify
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from models import storage
from api.v1.views import app_views


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """Restful API status"""
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def objs_count():
    """retrieves the number of each objects by type"""
    classes = {'amenities': Amenity, 'cities': City, 'places': Place,
               'reviews': Review, 'states': State, 'users': User}
    objs_num = {}
    for key, value in classes.items():
        objs_num[key] = storage.count(value)
    return jsonify(objs_num)
