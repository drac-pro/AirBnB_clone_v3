#!/usr/bin/python3
"""view for Place objects that handles all default RESTFul API actions"""
from flask import jsonify, abort, make_response, request
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity
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
    if 'user_id' not in kwargs.keys():
        abort(400, description='Missing user_id')

    user = storage.get(User, kwargs['user_id'])
    if not user:
        abort(404)

    if 'name' not in kwargs.keys():
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


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_place():
    """retrieves all Place objects depending of the JSON in the
    body of the request
    keys that can be in the body:
    states: list of State ids
    cities: list of City ids
    amenities: list of Amenity ids.
    """
    prompts = request.get_json(silent=True)
    if prompts is None:
        abort(400, description='Not a JSON')

    if not prompts or all(not prompts.get(key) for key in
                          ('states', 'cities', 'amenities')):
        places_list = storage.all(Place).values()
        places = [place.to_dict() for place in places_list]
        return jsonify(places)

    result = []

    if prompts.get('states'):
        for state_id in prompts.get('states'):
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    result.extend(city.places)

    if prompts.get('cities'):
        for city_id in prompts.get('cities'):
            city = storage.get(City, city_id)
            if city:
                for place in city.places:
                    if place not in result:
                        result.append(place)

    if amenities:
        if not result:
            result = storage.all(Place).values()
        amenity_ids = prompts.get('amenities')
        result = [place for place in result if
                  all(amenity.id in amenity_ids
                      for amenity in place.amenities)]

    return jsonify([place.to_dict() for place in result])
