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
  
  
  CORS(app, origins='*')

  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

  
  @app.route('/categories')
  def list_categories():
    selection =  Category.query.order_by(Category.id).all()
    categories = [category.type for category in selection]

    return jsonify({
      'success': True,
      'categories': categories,
    })


  
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


  
  @app.route('/questions/<id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter_by(id=id).one_or_none()

    if question is None:
      abort(404)

    question.delete()
    
    return jsonify({
      'success': True,
    })

  
  @app.route('/questions', methods=['POST'])
  def create_or_search_question():
    body = request.get_json()

    try:
      # If it's a request to create new question
      if 'searchTerm' not in body:
        # Retreive the user inputs for the new question
        question_text = body.get('question').strip()
        answer_text = body.get('answer').strip()
        category = body.get('category').strip()
        difficulty = body.get('difficulty')
        
        # Valid question must have no empty fields and have valid values
        valid_question  = question_text and answer_text and category and int(category) <= 6 and difficulty and difficulty <= 5

        if valid_question:
          question = Question(question_text, answer_text,category, difficulty)
          # Add the new question
          question.insert()
        else:
          abort(422)

        categories = Category.query.order_by('id').all()

        return jsonify({
          'success': True,
          # 'created': question.id,
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

    