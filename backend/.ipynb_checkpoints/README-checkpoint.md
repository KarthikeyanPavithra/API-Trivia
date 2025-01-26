## Project Title
API Trivia:
This project is a trivia game application with a Flask-based backend API and a frontend to manage and play trivia quizzes.

# Installing Project Dependencies:
pip install flask flask-sqlalchemy flask-cors

# Starting the Project Server:

For Backend code:
cd backend
pip3 install -r requirements.txt
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run

For Front end UI:
cd frontend 
npm install
npm start

# API Documentation:

## GET /categories

Request Parameters: None
Response Body:
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    ...
  },
  "success": true
}


## GET /questions

Request Parameters:
page (optional): Integer, default is 1
Response Body:
{
  "categories": {
    "1": "Science",
    "2": "Art",
    ...
  },
  "current_category": null,
  "questions": [
    {
      "answer": "Sample Answer",
      "category": 1,
      "difficulty": 3,
      "id": 1,
      "question": "Sample Question"
    },
    ...
  ],
  "success": true,
  "total_questions": 20
}


## DELETE /questions/int:question_id

Request Parameters: None
Response Body:
{
  "success": true,
  "deleted": 1,
  "questions": [...],
  "total_questions": 19
}


## POST /questions

Request Parameters:
{
  "question": "New question",
  "answer": "New answer",
  "difficulty": 3,
  "category": 1
}
Response Body:
{
  "success": true,
  "created": 21,
  "questions": [...],
  "total_questions": 21
}


## POST /questions/search

Request Parameters:
{
  "searchTerm": "sample"
}

Response Body:
{
  "success": true,
  "questions": [...],
  "total_questions": 1
}


## GET /categories/int:id/questions

Request Parameters: None
Response Body:
{
  "success": true,
  "questions": [...],
  "total_questions": 3,
  "current_category": 1
}


## POST /quizzes

Request Parameters:
{
  "previous_questions": [1, 2, 3],
  "quiz_category": {"id": 1, "type": "Science"}
}

Response Body:
{
  "question": {
    "answer": "Sample Answer",
    "category": 1,
    "difficulty": 3,
    "id": 4,
    "question": "Sample Question"
  },
  "force_end": false
}
