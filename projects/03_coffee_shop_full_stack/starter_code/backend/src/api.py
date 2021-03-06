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
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        # Get all drinks, format into short form and return as json object
        drinks = Drink.query.all()
        drinks_short = [drink.short() for drink in drinks]
        if len(drinks_short) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "drinks": drinks_short
        })
    except ValueError as e:
        print(f'Error: {str(e)}')
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        # Get all drinks, format into long form and return as json object
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_long = [drink.long() for drink in drinks]
        if len(drinks_long) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "drinks": drinks_long
        })
    except ValueError as e:
        print(f'Error: {str(e)}')
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(token):
    try:
        # Get new drink data, create and insert new drink in database
        # Format into long form and return as json object
        data = request.get_json()
        if not ('title' in data and 'recipe' in data):
            abort(400)
        title = data["title"]
        recipe = data["recipe"]
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except ValueError as e:
        print(f'Error: {str(e)}')
        abort(422)


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


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, id):
    try:
        # Get updated drink data, create and update changes in database
        # Format into long form and return as json object
        drink = Drink.query.get_or_404(id)
        data = request.get_json()

        drink.title = data["title"]
        drink.recipe = json.dumps(data["recipe"])

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except ValueError as e:
        print(f'Error: {str(e)}')
        abort(422)


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


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    try:
        # Get drink using incoming id, delete item from database
        drink = Drink.query.get_or_404(id)
        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
    except ValueError as e:
        print(f'Error: {str(e)}')
        abort(422)


# Error Handling
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

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error
    }), 401
