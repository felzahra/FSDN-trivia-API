import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
	'''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

    CORS(app, resources={'/': {'origins': '*'}})

	'''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  
    @app.after_request
    def after_request(response):
       
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
		
def paginate_questions(request, selection):
 '''Paginates and formats questions 

    Parameters:
      * <HTTP object> request, that may contain a "page" value
      * <database selection> selection of questions, queried from database
    
    Returns:
      * <list> list of dictionaries of questions, max. 10 questions

    '''
    # Get page from request. If not given, default to 1
    page = request.args.get('page', 1, type=int)
	# Calculate start and end slicing
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

	    # Format selection into list of dicts and slice

    questions = [question.format() for question in selection]
    questions_paginated = questions[start:end]

    return questions_paginated
		

  def getErrorMessage(error, default_text):
    '''Returns default error text or custom error message (if not applicable)

    Parameters:
      * <error> system generated error message which contains a description message
      * <string> default text to be used as error message if Error has no specific message
    
    Returns:
      * <string> specific error message or default text(if no specific message is given)
    
    '''
    try:
      # Return message contained in error, if possible
      return error.description["message"]
    except TypeError:
      # otherwise, return given default text
      return default_text
  
#  API Endpoints
#  ----------------------------------------------------------------
#  NOTE:  For explanation of each endpoint, please have look at the backend/README.md file. 
#         DOC Strings only contain short description and list of test classes 

#----------------------------------------------------------------------------#
# Endpoint /questions GET/POST/DELETE
#----------------------------------------------------------------------------#
  '''
  # TODO:

  DONE Create an endpoint to handle GET requests for questions
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST DONE: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions')
    def retrieve_questions():

  
        selection = Question.query.all()
        total_questions = len(selection)
        questions_paginated = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_returned = {}
        for category in categories:
            categories_returned[category.id] = category.type

        if (len(questions_paginated) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': questions_paginated,
            'total_questions': total_questions,
            'categories': categories_returned
        })
'''
  TEST DONE: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        question = Question.query.filter_by(id=id).one_or_none()

			if not question:
      # If no question with given id was found, raise 404 and explain what went wrong.
      abort(400, {'message': 'Question with id {} does not exist.'.format(id)})
    
    try:
      # Try to delete a new question. If anything went wrong, raise 422 "unprocessable"
      question.delete()

      # Return succesfull response with deleted question id
	  

            return jsonify({
                'success': True,
                'deleted': id
            })

        except:
            abort(422)
'''
  # TODO DONE:  Create an endpoint to POST a new question,  
  which will require the question and answer text,  
  category, and difficulty score.
  
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  ADDITIONALLY:

  # TODO DONE: Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 

  '''
    @app.route('/questions', methods=['POST'])
    def create_or_search_questions():
         """Creates a question or searches for it with search term
      
      Tested by:
        Success:
          - test_create_question
          - test_search_question
        Error:
          - test_error_create_question
          - test_error_404_search_question

    """
           
        body = request.get_json()

        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            selection = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            if (len(selection) == 0):
                abort(404)

            paginated = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
        else:
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                questions_paginated = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': questions_paginated,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_from_categories(id):
        """Returns paginated questions from a specific category

        Tested by:
          Success:
            - test_get_questions_from_category
          Error:
            - test_400_get_questions_from_category

    """
        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(400)

        selection = Question.query
		.filter_by(category=category.id)
		.all()

        questions_paginated = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': questions_paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })
#----------------------------------------------------------------------------#
# Endpoint /quizzes POST
#----------------------------------------------------------------------------#
  '''
  TODO DONE: Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
      

        body = request.get_json()

        previous = body.get('previous_questions')

        category = body.get('quiz_category')

        if ((category is None) or (previous is None)):
            abort(400)

        if (category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=category['id']).all()

        total = len(questions)

        def get_random_question():
            return questions[random.randrange(0, len(questions), 1)]

        def check_if_used(question):
            used = False
            for q in previous:
                if (q == question.id):
                    used = True

            return used

        question = get_random_question()

        while (check_if_used(question)):
            question = get_random_question()

            
            if (len(previous) == total):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

		'''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
      """Returns all categories as list

      Tested by:
        Success:
          - test_get_all_categories
        Error:
          - test_error_405_get_all_categories

    """
    # Get all categories
        categories = Category.query.all()
        categories_returned = {}
        for category in categories:
            categories_returned[category.id] = category.type

        if (len(categories_returned) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_returned
        })
	

	@app.route('/categories/<string:id>/questions', methods=['GET'])
  def retrieve_categories(id):
  
    selection = (Question.query
    .filter(Question.category == str(id))
    .order_by(Question.id)
    .all())

    if not selection:
      abort(400, {'message': 'No questions with category {} found.'.format(id) })

    questions_paginated = paginate_questions(request, selection)

    if not questions_paginated:
      abort(404, {'message': 'No questions in selected page.'})

    return jsonify({
      'success': True,
      'questions': questions_paginated,
      'total_questions': len(selection),
      'current_category' : id
      })
	
	
	@app.route('/categories', methods=['POST'])
  def create_categories():
 
    body = request.get_json()
 
    if not body:
      abort(400, {'message': 'request does not contain a valid JSON body.'})
    
    new_type = body.get('type', None)
 if not new_type:
      abort(400, {'message': 'no type for new category provided.'})

    try:
      category = Category(type = new_type)
      category.insert()

      selections = Category.query.order_by(Category.id).all()
      categories_all = [category.format() for category in selections]

      return jsonify({
        'success': True,
        'created': category.id,
        'categories': categories_all,
        'total_categories': len(selections)
      })

    except:
      abort(422)

  @app.route('/categories/<int:id>', methods=['DELETE'])
  def delete_categories(id):
 

    category = Category.query.filter(Category.id == id).one_or_none()
    if not category:
      abort(400, {'message': 'Category with id {} does not exist.'.format(id)})
    
    try:
      category.delete()

      return jsonify({
        'success': True,
        'deleted': id
      })

    except:
      abort(422)
#
#----------------------------------------------------------------------------#
# API error handler & formatter.
#----------------------------------------------------------------------------#
 
  # TODO DONE: Create error handlers for all expected errors 

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
		
		'''
	  @TODO: 
	  Create error handlers for all expected errors 
	  including 404 and 422. 
	  '''
  
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
