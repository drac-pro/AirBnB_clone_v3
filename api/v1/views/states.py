#!/usr/bin/python3
"""view for State objects that handles all default RESTFul API actions"""
from flask import jsonify, abort, make_response, request
from models.state import State
from models import storage
from api.v1.views import app_views


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    """Retrieves the list of all State objects"""
    states_dict = storage.all(State)
    state_list = []
    for state in states_dict.values():
        state_list.append(state.to_dict())
    return jsonify(state_list)


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state(state_id):
    """Retrieves a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route('/states/<state_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    storage.delete(state)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """Creates a State"""
    kwargs = request.get_json(silent=True)
    if not kwargs:
        abort(400, description='Not a JSON')
    elif 'name' not in kwargs.keys():
        abort(400, description='Missing name')
    state = State(**kwargs)
    state.save()
    return make_response(jsonify(state.to_dict()), 201)


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """Updates a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404)
    kwargs = request.get_json(silent=True)
    if not kwargs:
        abort(400, description='Not a JSON')
    for key, value in kwargs.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(state, key, value)
    state.save()
    return jsonify(state.to_dict())
