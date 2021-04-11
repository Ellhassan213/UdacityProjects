import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
  # create and configure the app
  ''' @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs '''
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"/api/*": {"origins": '*'}})


  ''' @TODO: Use the after_request decorator to set Access-Control-Allow '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  

  ''' @TODO: Create an endpoint to handle GET requests for all available categories. '''
  @app.route('/categories', methods=['GET'])
  def retrieve_all_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id: category.type for category in categories}

    # print(formatted_categories) {1: 'Science', 2: 'Art', 3: 'Geography', 4: 'History', 5: 'Entertainment', 6: 'Sports'}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories' : len(formatted_categories)
    })


  ''' @TODO: Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). 
      This endpoint should return a list of questions, number of total questions, current category, categories. 

      TEST: At this point, when you start the application you should see questions and categories generated,
      ten questions per page and pagination at the bottom of the screen for three pages.
      Clicking on the page numbers should update the questions. '''

  @app.route('/questions', methods=['GET'])
  def retrieve_paginated_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.order_by(Category.id).all()
    formatted_categories = {category.id: category.type for category in categories}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': formatted_categories,
      'current_categories': None
    })


  ''' @TODO: Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get_or_404(question_id)
      question.delete()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    except:
      abort(422)

  ''' @TODO: Create an endpoint to POST a new question, which will require the question and 
  answer text, category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(
        question=new_question,
        answer=new_answer,
        category=new_category,
        difficulty=new_difficulty
      )

      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    except:
      abort(422)


  ''' @TODO: Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include only question that include that string within their question. 
  Try using the word "title" to start. '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    
    if search_results is None:
      abort(404)
    
    formatted_search_results = [result.format() for result in search_results]

    return jsonify({
      'success': True,
      'questions': formatted_search_results,
      'total_questions': len(formatted_search_results)
    })

  ''' @TODO: Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the categories in the left column will cause only questions of that 
  category to be shown. '''

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_questions_by_category(category_id):
    try:
      selected_category = Category.query.get_or_404(category_id)
      category_questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
      current_questions = paginate_questions(request, category_questions)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(category_questions),
        'current_category': selected_category.format()
      })
    except:
      abort(404)


  ''' @TODO: Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters 
  and return a random questions within the given category, if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category, one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()

      previous_questions = body.get('previous_questions', None)
      quiz_category = body.get('quiz_category', None)

      if quiz_category['id'] == 0:
        selected_questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        selected_questions = Question.query.filter(Question.category == quiz_category['id'], \
                                                    Question.id.notin_(previous_questions)).all()

      questions = [question.format() for question in selected_questions]

      if selected_questions:
        random_selector = random.randint(0, len(selected_questions)-1)
        new_question = questions[random_selector]
      else:
        new_question = None

      return jsonify({
        'success': True,
        'question': new_question
      })
    except:
      abort(422)


  ''' @TODO: Create error handlers for all expected errors, including 404 and 422. '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422

  @app.errorhandler(405)
  def unprocessable(error):
      return jsonify({
          'success': False,
          'error': 405,
          'message': 'method not allowed'
      }), 405

  @app.errorhandler(400)
  def unprocessable(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': 'bad request'
      }), 400

  # curl http://127.0.0.1:5000/categories
  # curl http://127.0.0.1:5000/questions
  # curl http://127.0.0.1:5000/questions?page=999
  # curl -X "DELETE" http://127.0.0.1:5000/questions?page=999
  
  return app

    