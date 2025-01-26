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

    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

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
    
    @app.route('/categories', methods=['GET'])
    def get_categories():
        # Query all categories from the database
        categories = Category.query.all()

        # Format categories into a dictionary with {id: type}
        formatted_categories = {category.id: category.type for category in categories}

        # Return the response
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

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
            'current_category': None,  
        })

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
            return jsonify({
                "success": True,
                "deleted": question_id,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                })
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
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
                }),201
        except Exception as e:
#             print(f"Error: {e}")
            db.session.rollback()
            abort(422)

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()

        search_term = body.get("searchTerm", None)

        if not search_term:
            abort(400)

        try:
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
#             print(f"Error: {e}")
            abort(422)

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):
        try:
            # Fetch all questions for the given category
            selection = Question.query.filter(Question.category == id).all()
            
            if len(selection) == 0:
                abort(422)
            # Paginate the results
            current_questions = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "current_category": id,
                })

        except Exception as e:
#             print(f"Error: {e}")
            abort(422)

    @app.route("/quizzes", methods=["POST"])
    def get_question():
        body = request.get_json()
#         print(body)
        if not body:
            abort(400)
        previous_questions = body.get("previous_questions", [])
        category = body.get("quiz_category", None)  
#         print(category)
        if previous_questions is None or category is None:
            abort(400)

        category_id = category.get("id") if category else None  
#         print(category_id)
        try: 
            # Filter questions based on category if provided
            if category_id:
                questions = Question.query.filter(Question.category == category_id).all()
#                 print(questions)
            else:
                questions = Question.query.all()
#                 print(questions)

            # Remove previously asked questions
            questions = [q for q in questions if q.id not in previous_questions]
            # If no questions left, return an error with appropriate status code
            if not questions:
                return jsonify({
                    "success": False,
                    "message": "Quiz completed",
                    "force_end": True,
                    "score": len(previous_questions) 
                })
                        
            # Get a random question from the remaining questions
            question = random.choice(questions)
            return jsonify({
                "question": question.format(),
                "force_end": False
            })
        except Exception as e:
            abort(422)

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
    def not_found(error):
        return jsonify({"success": False,
            "error": 405, 
            "message": "method not allowed"
            }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500
    
    return app
