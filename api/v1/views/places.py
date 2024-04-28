#!/usr/bin/python3
"""view for Place objects that handles all default RESTFul API actions"""
from flask import jsonify, abort, make_response, request
from models.place import Place
from models.city import City
from models import storage
from api.v1.views import app_views


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all places in a City objects"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    place_list = []
    for place in city.places:
        place_list.append(place.to_dict())
    return jsonify(place_list)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a Place"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    kwargs = request.get_json(silent=True)
    if not kwargs:
        abort(400, description='Not a JSON')
    elif 'user_id' not in kwargs.keys():
        abort(400, description='Missing user_id')
    elif 'name' not in kwargs.keys():
        abort(400, description='Missing name')
    kwargs['city_id'] = city_id
    place = Place(**kwargs)
    place.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    kwargs = request.get_json(silent=True)
    if not kwargs:
        abort(400, description='Not a JSON')
    for key, value in kwargs.items():
        if key not in \
                ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict())
