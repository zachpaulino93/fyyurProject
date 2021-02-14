import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_quest(request, selection):

    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [q.format() for q in selection]
    formatted_questions = questions[start:end]

    return formatted_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  # using aftr req decorator to trigger this check before any request will be proccessed
  @app.after_request
  #after req function
  def after_request(response):
        # sets what type of headers will be allowed
        response.headers.add("Access-Control-Allow-Headers", 'Content-Type, Authorization')
        # sets what type of methods will be allowed
        response.headers.add("Access-Control-Allow-Methods", 'GET, PATCH, POST, DELETE, OPTIONS')
        # sends the response back out into the app. but where does the response return to? the program its self?
        # Is this almost like a firewall the return doesnt really go to any funtion it just release the data back into the program?
        return response

  @app.route('/categories')
  def handle_categories():
      query_cat = Category.query.all()
      category_items = {category.id: category.type.lower() for category in query_cat}

      if len(category_items) == 0:
        abort(404)

      return jsonify({
            'success': True,
            'categories': category_items
      }), 200

  @app.route('/categories/<int:id>/questions')
  def get_category_questions(id):
          try:
                  if (id > 7):
                      abort(422)
                  category = Category.query.get(id).format()
                  questions = Question.query.filter(Question.category == id).all()
                  question = [ question.format() for question in questions]

                  return jsonify({
                    'success': True,
                    'questions': question,
                    'totalQuestions': len(questions),
                    'currentCategory': category['type']
                    }), 200
          except Exception as e:
                  abort(422)



  @app.route('/questions')
  def handle_questions():
      query_questions = Question.query.all()
      query_cat = Category.query.all()
      fqs = [item for item in paginate_quest(request, query_questions)]

      fcs = query_cat
      category_items = {category.id: category.type.lower() for category in query_cat}

      if len(query_questions) == 0:
          abort(404)

      return jsonify({
            'success': True,
            'status_code': 200,
            'total_questions': len(query_questions),
            'questions': fqs,
            'categories': category_items,
            'total_categories': len(query_cat)
      }), 200

  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_questions(question_id):
        # remove question from db
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            # Abort if question is Null
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            }), 200
        # abort to server error if it fails due to db being what failed
        except Exception as e:
            db.session.rollback()

            abort(500)

  @app.route('/questions', methods=['POST'])
  def add_new_question():
            # set json body
            body = request.get_json()

            # using strip to remove spaces so no one can submit a question or answer with only spaces
            new_question = body.get('question').strip()
            new_answer = body.get('answer').strip()
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            # i need to handle questions and answers with no data
            if len(new_question) == 0:
                abort(422)
            elif len(new_answer) == 0:
                abort(422)

            else:
                try:
                    question = Question(new_question, new_answer, new_category, new_difficulty)
                    question.insert()
                    return jsonify({
                        'success': True,
                        'message': 'question added'
                        }), 200

                except Exception as e:
                        db.session.rollback()
                        abort(422)

  @app.route('/question/search', methods=['POST'])
  def question_search():
      body = request.get_json()
      search_term = body.get('searchTerm')
      questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()
      question = [question.format() for question in questions]

      if len(questions) == 0:
          abort(422)
      try:
          return jsonify({
            'success': True,
            'questions': question,
            'total_questions': len(question)
            }), 200

      except Exception as e:
            abort(422)



  @app.route('/quizzes', methods=['POST'])
  def create_quiz():
        try:
          body = request.get_json()
          category = body.get('quiz_category')
          pq = body.get('previous_questions')

          if category['id'] == 0:
              question = Question.query.filter(Question.id.notin_(pq)).all()

          else:
              question = Question.query.filter(Question.id.notin_(pq), Question.category == category['id']).all()

          def get_rando():
                nq = random.choice(question).format()
                return nq

          questions = None
          if(question):
              questions = random.choice(question).format()

          return jsonify({
                "success": True,
                'question': questions
          }), 200


        except Exception as e:
                abort(400)

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def no_no_found(error):
      return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page is not found'
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
            'success': False,
            'error': 422,
            'message': "Unprocessable Entity"
      }), 422

  @app.errorhandler(400)
  def bad_req(error):
      return jsonify({
            'success': False,
            'error': 400,
            'message': "it was a bad request"
      }), 400

  @app.errorhandler(500)
  def serv_error(error):
      return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal server error"
      }), 500

  return app
