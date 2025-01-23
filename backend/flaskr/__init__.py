from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        """
        Endpoint to handle GET requests for all available categories.
        Returns:
            - A JSON object containing all categories in the database.
            - The success status of the operation.
        """
        # Query all categories from the database
        categories = Category.query.all()

        # Format categories into a dictionary with {id: type}
        formatted_categories = {category.id: category.type for category in categories}

        # Return the response
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        total_questions = len(selection)

        if len(current_questions) == 0:
            abort(404)
        
        # Get all categories for the response
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': formatted_categories,
            'current_category': None,  # Add logic to filter questions by category if needed
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            # Fetch the question using the ID, or return 404 if not found
            question = Question.query.filter(Question.id == question_id).one_or_none()

            # If no question found, return 404 error
            if question is None:
                abort(404)

            # Delete the question
            db.session.delete(question)
            db.session.commit()

            # Retrieve all questions after deletion and paginate them
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            # Return success response
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            # If any exception occurs, return 422 error
            db.session.rollback()
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("search", None)

        try:
            if search:
                # If search is provided, filter questions by title
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                    }
                )

            else:
                # Create a new question and insert it into the database
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty,
                )
                db.session.add(question)
                db.session.commit()

                # Get all questions and paginate them
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()

        search_term = body.get("searchTerm", None)

        if not search_term:
            abort(400)

        try:
            # Search for questions where the search term is a substring of the question text (case-insensitive)
            selection = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()

            # Paginate the results if needed (optional)
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):
        try:
            # Fetch all questions for the given category
            selection = Question.query.filter(Question.category == id).all()

            # Paginate the results
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "current_category": id,
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def get_question():
        body = request.get_json()
        print(body)
        previous_questions = body.get("previous_questions", [])
        category = body.get("quiz_category", None)  # This will be an object containing 'id' and 'type'
        print(category)

        category_id = category.get("id") if category else None  # Extract 'id' from the category object
        print(category_id)
        try: 
            # Filter questions based on category if provided
            if category_id:
                questions = Question.query.filter(Question.category == category_id).all()
                print(questions)
            else:
                questions = Question.query.all()
                print(questions)

            # Remove previously asked questions
            questions = [q for q in questions if q.id not in previous_questions]
            
            # If no questions left, return an error with appropriate status code
            if not questions:
                return jsonify({
                        "success": False,
                        "message": "Quiz completed",
                        "force_end": True,
                        "score": len(previous_questions)  # You can also pass this score from frontend
                    })
                        
            # Get a random question from the remaining questions
            question = random.choice(questions)

            return jsonify({
                "question": question.format(),
                "force_end": False
            })
        
        except Exception as e:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
                "success": False,
                "error": 500,
                "message": "Error occurred while fetching the question"
            }), 500

    return app

