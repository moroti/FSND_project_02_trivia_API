import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page =  request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, origins='*')

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def list_categories():
    selection =  Category.query.order_by(Category.id).all()
    categories = [category.type for category in selection]

    return jsonify({
      'success': True,
      'categories': categories,
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def list_questions():
    questions_list = Question.query.order_by('id').all()

    categories =  Category.query.order_by(Category.id).all()

    return jsonify({
      'success': True,
      'questions': paginate_questions(request, questions_list),
      'total_questions': len(questions_list),
      'categories': [category.type for category in categories],
      'current_category': None,
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<q_id>', methods=['DELETE'])
  def delete_question(q_id):
    question = Question.query.filter_by(id=q_id).one_or_none()

    if question is None:
      abort(404)

    question.delete()
    
    return jsonify({
      'success': True,
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_or_search_question():
    body = request.get_json()

    try:
      # If it's a request to create new question
      if 'searchTerm' not in body:
        # Retreive the user inputs for the new question
        question_text = body.get('question').strip()
        answer_text = body.get('answer').strip()
        category = body.get('category')
        difficulty = body.get('difficulty')
        print("category",category)
        # Valid question must have no empty fields and have valid values
        valid_question  = question_text and answer_text and category and category <= 6 and difficulty and difficulty <= 5

        if valid_question:
          question = Question(question_text, answer_text,category, difficulty)
          # Add the new question
          question.insert()
        else:
          abort(422)

        categories = Category.query.order_by('id').all()

        return jsonify({
          'success': True,
          'created': question.id,
        })
      else:
        # If instead it's a search request, retreive the input search term
        search_term = body.get('searchTerm', '').strip()
        # Search the questions containing the search term
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
        # Paginate the questions list
        current_questions = paginate_questions(request, questions)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': None,
        })
    except:
      # print(sys.exc_info())
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # check the POST /questions endpoint

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions')
  def get_questions_by_category(cat_id):
    selected_category = Category.query.filter_by(id=cat_id).one_or_none()
    categories = Category.query.order_by('id').all()

    # If the given category does not exist, abort and raise 404 error
    if selected_category is None:
      abort(404)
    
    questions_list = Question.query.filter_by(category=cat_id).order_by('id').all()

    return jsonify({
      'success': True,
      'questions': paginate_questions(request, questions_list),
      'total_questions': len(questions_list),
      'categories': [category.type for category in categories],
      'current_category': selected_category.format(),
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    quiz_category = body.get('quiz_category')
    previous_questions = body.get('previous_questions')

    # Exclude all the previous questions from the list of eligible questions
    questions = Question.query.filter(~Question.id.in_(previous_questions))

    # When a category is selected
    if quiz_category['id'] > 0:
      # Get the list of the questions of the given category
      questions = questions.filter(Question.category==quiz_category['id'])

    current_question = None

    # Randomly select the current question
    if len(questions.all()) > 0:
      current_question = random.choice(questions.all()).format()

    return jsonify({
      'success': True,
      'question': current_question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "unprocessable"
    }), 422
  
  return app

    