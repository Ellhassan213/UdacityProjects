import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    Using the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

#----------------------------------------------------------------------------#
# Movie
#----------------------------------------------------------------------------#

    @app.route('/movies', methods=['GET'])
    def get_movies():
        try:
            # Get all movies, format into short form and return as json object
            movies = Movie.query.all()
            formatted_movies = [movie.format() for movie in movies]
            if len(formatted_movies) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "movies": formatted_movies
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

#----------------------------------------------------------------------------#
# Actor
#----------------------------------------------------------------------------#

    @app.route('/actors', methods=['GET'])
    def get_actors():
        try:
            # Get all actors, format into short form and return as json object
            actors = Actor.query.all()
            formatted_actors = [actor.format() for actor in actors]
            if len(formatted_actors) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "movies": formatted_actors
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

#----------------------------------------------------------------------------#
# Error Handling
#----------------------------------------------------------------------------#

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        return jsonify({
            "success": False,
            "error": AuthError.status_code,
            "message": AuthError.error
        }), 401

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
