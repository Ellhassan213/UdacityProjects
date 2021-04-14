import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


# Paginate questions and organise into desired format
def paginate_questions(request, selection):
    items_limit = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1

    questions = Question.query.order_by(Question.id
                                        ).limit(items_limit).offset(
                                          current_index * items_limit).all()

    current_questions = [question.format() for question in questions]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def retrieve_all_categories():
        # Get all categories, if none found, abort 404,
        # else format and return json object
        categories = Category.query.order_by(Category.id).all()

        if not categories:
            abort(404)

        formatted_categories = {category.id: category.type
                                for category in categories}
        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(formatted_categories)
        })

    @app.route('/questions', methods=['GET'])
    def retrieve_paginated_questions():
        # Get and paginate questions, get categories
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()

        # Abort 404 if no questions or no categories
        if len(current_questions) == 0 or not categories:
            abort(404)

        #  return intented json object
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type
                           for category in categories},
            'current_categories': None
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            # Get question by id, if it does not exist 404 abort.
            # If it exist, delete
            question = Question.query.get_or_404(question_id)
            question.delete()

            # Repaginate and display questions
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
              'success': True,
              'deleted': question_id,
              'questions': current_questions,
              'total_questions': len(selection)
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        # Get inputs from the form
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            # Create a new question and insert to database
            question = Question(
              question=new_question,
              answer=new_answer,
              category=new_category,
              difficulty=new_difficulty
            )

            question.insert()

            # repaginate and display questions
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get search term from form
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        # search using the ilike to ensure case insensitivity
        search_results = Question.query.filter(Question.question.ilike(
                                                  f'%{search_term}%')).all()

        if search_results is None:
            abort(404)

        formatted_search_results = [result.format()
                                    for result in search_results]

        return jsonify({
            'success': True,
            'questions': formatted_search_results,
            'total_questions': len(formatted_search_results)
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            # Get category based on id, filter questions
            selected_category = Category.query.get_or_404(category_id)
            category_questions = Question.query.filter(
              Question.category == category_id).order_by(Question.id).all()
            current_questions = paginate_questions(request, category_questions)

            # Return intended json object
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(category_questions),
                'current_category': selected_category.format()
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            # Get incoming input, previous questions & quiz category chosen
            body = request.get_json()

            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            # Category id 0 - Select all questions not in previous questions!
            if quiz_category['id'] == 0:
                selected_questions = Question.query.filter(
                  Question.id.notin_(previous_questions)).all()
            # Select questions by category, make sure not in previous questions
            else:
                selected_questions = Question.query.filter(
                  Question.category == quiz_category['id'],
                  Question.id.notin_(previous_questions)).all()

            # Format questions
            questions = [question.format() for question in selected_questions]

            # Choose a random question out of the ones selected
            if selected_questions:
                random_selector = random.randint(0, len(selected_questions)-1)
                new_question = questions[random_selector]
            else:
                new_question = None

            # Return question
            return jsonify({
                'success': True,
                'question': new_question
            })
        except ValueError as e:
            print(f'Error: {str(e)}')
            abort(422)

    # Create all error handlers, pass in the error codes
    # return appropriate errors and messages
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
