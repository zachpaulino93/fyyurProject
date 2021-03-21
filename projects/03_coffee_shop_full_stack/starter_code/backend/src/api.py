import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    #query all drinks
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        # one liner loop to loop each drink in drinks and give short description BOOM
        'drinks': [drink.short() for drink in drinks]
    })


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''




@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks(payload):
    drinks = Drink.query.all()
    all_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': all_drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(404)
    title = data['title']
    recipe = json.dumps(data['recipe'])
    drink = Drink(title=title, recipe=recipe)
    drink.insert()
    return jsonify({
        'success': True,
        'drinks':[drink.long()]
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drink(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'delete': drink.id
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return ({
        'success': False,
        'error': 404,
        'message': 'Resouce not found'
    }), 404



'''
@TODO implement error handler for 404
    error handler should conform to general task above


'''

@app.errorhandler(AuthError)
def auth_error_hndl(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code

@app.errorhandler(401)
def unauthorized_attempt(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized attempt'
    }), 401

@app.errorhandler(400)
def bad_req(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request was made'
    }), 400

@app.errorhandler(405)
def method_not_allowed_today_zurg(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method is not vaild'
    }), 405

@app.errorhandler(500)
def internal_server_failure_of_doom(error):
    return jsonify ({
        'success': False,
        'error': 500,
        'message': 'The internal server has failed! THE SHIP SINKING'
    }), 500




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
