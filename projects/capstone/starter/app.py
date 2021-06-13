import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth import (AuthError, requires_auth, AUTH0_DOMAIN,
                  ALGORITHMS, API_AUDIENCE, CLIENT_ID, CALLBACK_URL)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

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
    @requires_auth('get:movies')
    def get_movies(token):
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

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movie')
    def post_movie(token):
        try:
            # Get new movie data, create and insert new movie in database
            # Format and return as json object
            data = request.get_json()
            if not ('title' in data and 'release_date' in data):
                abort(400)
            title = data["title"]
            release_date = data["release_date"]
            movie = Movie(
                title=title,
                release_date=release_date
            )
            movie.insert()
            movies = Movie.query.all()
            formatted_movies = [movie.format() for movie in movies]

            return jsonify({
                "success": True,
                "created": movie.id,
                "movies": formatted_movies
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/movies/<id>', methods=['PATCH'])
    @requires_auth('patch:movie')
    def patch_movie(token, id):
        try:
            # Get updated movie data, create and update changes in database
            # Format and return as json object
            movie = Movie.query.get_or_404(id)
            data = request.get_json()

            movie.title = data["title"]
            movie.release_date = data["release_date"]

            movie.update()

            movies = Movie.query.all()
            formatted_movies = [movie.format() for movie in movies]

            return jsonify({
                "success": True,
                "patched_movie": id,
                "movies": formatted_movies
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/movies/<id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(token, id):
        try:
            # Get movie using incoming id, delete item from database
            movie = Movie.query.get_or_404(id)
            movie.delete()

            return jsonify({
                "success": True,
                "deleted_movie": id
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

#----------------------------------------------------------------------------#
# Actor
#----------------------------------------------------------------------------#

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(token):
        try:
            # Get all actors, format into short form and return as json object
            actors = Actor.query.all()
            formatted_actors = [actor.format() for actor in actors]
            if len(formatted_actors) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "actors": formatted_actors
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actor')
    def post_actor(token):
        try:
            # Get new actor data, create and insert new actor in database
            # Format and return as json object
            data = request.get_json()
            if not ('name' in data and 'age' in data and 'gender' in data):
                abort(400)
            name = data["name"]
            age = data["age"]
            gender = data["gender"]
            actor = Actor(
                name=name,
                age=age,
                gender=gender
            )
            actor.insert()
            actors = Actor.query.all()
            formatted_actors = [actor.format() for actor in actors]

            return jsonify({
                "success": True,
                "created": actor.id,
                "actors": formatted_actors
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/actors/<id>', methods=['PATCH'])
    @requires_auth('patch:actor')
    def patch_actor(token, id):
        try:
            # Get updated actor data, create and update changes in database
            # Format and return as json object
            actor = Actor.query.get_or_404(id)
            data = request.get_json()

            actor.name = data["name"]
            actor.age = data["age"]
            actor.gender = data["gender"]

            actor.update()

            actors = Actor.query.all()
            formatted_actors = [actor.format() for actor in actors]

            return jsonify({
                "success": True,
                "patched_actor": id,
                "actors": formatted_actors
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/actors/<id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(token, id):
        try:
            # Get actor using incoming id, delete item from database
            actor = Actor.query.get_or_404(id)
            actor.delete()

            return jsonify({
                "success": True,
                "deleted_actor": id
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)


#----------------------------------------------------------------------------#
# Helper functions
#----------------------------------------------------------------------------#

    @app.route("/auth/URL", methods=["GET"])
    def generate_auth_URL():
        URL = f'https://{AUTH0_DOMAIN}/authorize' \
            f'?audience={API_AUDIENCE}' \
            f'&response_type=token&client_id=' \
            f'{CLIENT_ID}&redirect_uri=' \
            f'{CALLBACK_URL}'
        return jsonify({
            'URL': URL
        })


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
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

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
    app.run(host='127.0.0.1', port=5000, debug=True)
