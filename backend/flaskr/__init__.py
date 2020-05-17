import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate(request, questions):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions_formated = [question.format() for question in questions]
  current_questions = questions_formated[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)


  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route("/categories",methods=["GET"])
  def get_categories():
      error=0
      try:
          categories=Category.query.all()
          categories_formated=[category.type for category in categories]
          if(len(categories_formated)==0):
              error=404
          return jsonify({
          "success":True,
          "categories":categories_formated
          })
      except:
          error=422
      finally:
          if(error):
              abort(error)



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
  @app.route("/questions",methods=["GET"])
  def get_questions():
      error=0
      try:
          questions=Question.query.all()
          categories=Category.query.all()
          current_questions=paginate(request,questions)
          categories_formated=[category.type for category in categories]
          if(len(current_questions)==0):
              error=404
          return jsonify({
          "success":True,
          "questions":current_questions,
          "total_questions":len(questions),
          "categories":categories_formated,
          "current_category":None
          })
      except:
          error=422
      finally:
          if(error):
              abort(error)




  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route("/questions/<int:question_id>",methods=["DELETE"])
  def delete_question(question_id):
      error=0
      try:
        question=Question.query.get(question_id)
        if(question):
            question.delete()
            return get_questions()
        else:
            error=404
      except:
        error=422
      finally:
          if(error):
            abort(error)

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route("/questions",methods=["POST"])
  def add_question():
      error=0
      try:
          body=request.get_json()
          question=body.get("question","")
          answer=body.get("answer","")
          difficulty=body.get("difficulty","")
          category=body.get("category","")
          if not(question == "" or answer == "" or difficulty == "" or category == ""):
             new_question=Question(question,answer,category,difficulty)
             new_question.insert()
             return jsonify({
             "success":True
             })
          else:
             error=400
      except:
          error=422
      finally:
          if(error):
              abort(error)


  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route("/questions/search",methods=["POST"])
  def search_questions():
      error=0
      try:
          body=request.get_json()
          search=body.get("searchTerm")

          questions=Question.query.filter(Question.question.ilike("%"+search+"%")).all()
          if(questions):

              current_questions=paginate(request,questions)
              return jsonify({
              "success":True,
              "questions":current_questions,
              "total_questions":len(questions)
              })
          else:
              error=404
      except:
          error=422
      finally:
          if(error):
              abort(error)


  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route("/categories/<int:category_id>/questions",methods=["GET"])
  def get_questions_by_category(category_id):
      error=0
      try:
          questions=Question.query.filter(Question.category==category_id).all()
          if(questions):

              current_questions=paginate(request,questions)
              return jsonify({
              "success":True,
              "questions":current_questions,
              "total_questions":len(questions),
              "current_category":None
              })
          else:
              error=404
      except:
          error=422
      finally:
          if(error):
              abort(error)


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
  @app.route("/quizzes",methods=["POST"])
  def get_quiz():
      error=0
      try:
        body=request.get_json()
        previous_questions=body.get("previous_questions",None)
        quiz_category=body.get("quiz_category",None)

        if(("type" in quiz_category.keys()) and ("id" in quiz_category.keys()) and quiz_category["id"]==0 and not(previous_questions==None)):

          questions=Question.query.filter(Question.id.notin_(previous_questions)).all()
          
          if(questions):
              question=questions[random.randint(0,len(questions)-1)]
              return jsonify({
              "success":True,
              "question":question.format()
              })
          else:
              error=404
        elif(("type" in quiz_category.keys()) and ("id" in quiz_category.keys()) and quiz_category and not(previous_questions==None)):
          questions=Question.query.filter(Question.id.notin_(previous_questions),Question.category==quiz_category["id"]).all()
          if(questions):
              question=questions[random.randint(0,len(questions)-1)]
              return jsonify({
              "success":True,
              "question":question.format()
              })
          else:
              error=404
        else:
            error=400
      except:
          error=422
      finally:
          if(error):
              abort(error)


  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
      "success":False,
      "error":405,
      "message":"method not allowed"
      }),405

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
      "success":False,
      "error":500,
      "message":"internal server error"
      }),500
  return app
