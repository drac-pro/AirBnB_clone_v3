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


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def search_place():
    """retrieves all Place objects depending of the JSON in the
    body of the request
    keys that can be in the body:
    states: list of State ids
    cities: list of City ids
    amenities: list of Amenity ids
    """
    prompts = request.get_json(silent=True)
    if not prompts:
        abort(400, description='Not a JSON')
    if prompts == {} or all(not value for value in prompts.values()):
        places_dict = storage.all(Place)
        places = [place.to_dict() for place in places_dict.values()]
        return jsonify(places)

    result = []

    if 'states' in prompts.keys() and prompts['states'] != []:
        for state_id in prompts['states']:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    result = [place for place in city.places]

    if 'cities' in prompts.keys() and prompts['cities'] != []:
        for city_id in prompts['cities']:
            city = storage.get(City, city_id)
            if city:
                result.extend([place for place in city.places])

    if 'amenities' in prompts.keys() and prompts['amenities'] != []:
        amenity_ids = prompts['amenities']
        amenities = {storage.get(Amenity, amenity_id) for amenity_id in
                     amenity_ids if storage.get(Amenity, amenity_id)
                     is not None}
        for place in result:
            if not set({amenities}).issubset({amenity in place.amenities}):
                result.remove(place)

    return jsonify(list(map(lambda amenity: amenity.to_dict(), result)))
