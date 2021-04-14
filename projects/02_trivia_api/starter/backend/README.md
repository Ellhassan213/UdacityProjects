# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

#### Base URL

The app is currently run locally and is not hosted as a base URL.
The backend app is hosted at default http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration.

#### API Keys/Authentication

This version of the app does not require authentication or API keys.

## Error Handling

Errors are returned as JSON objects in the following format:
```bash
{
    "success": False,
    "error": 400,
    "message": "bad request"
}
```

The app will return the following error types when request fail:

- 400: Bad request
- 404: Resource not found
- 422: Unprocessable
- 405: Method not allowed
- 500: Internal server error

## Resource Endpoints

### GET /categories

#### General
- Returns a dictionary of all category topics, success value and total number of categories

#### Sample Request

```bash
curl http://127.0.0.1:5000/categories
```

#### Sample Response

```bash
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true, 
  "total_categories": 6
}
```

### GET /questions

#### General
- Returns a dictionary of list of questions, success value, total number of questions and categories
- Results are paginated in groups of 10
- It is possible to include a request argument to choose page number. Start from 1!

#### Sample Request

```bash
curl http://127.0.0.1:5000/questions?page=1
```

#### Sample Response

```bash
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_categories": null, 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 3, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```
### DELETE /questions/{question_id}

#### General
- Deletes the record of a question
- Returns ID of deleted question, success value, current paginated questions and total number of questions left

#### Sample Request

```bash
curl -X DELETE http://127.0.0.1:5000/questions/4
```

#### Sample Response

```bash
{
  "deleted": 4, 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    },  
    {
      "answer": "Agra", 
      "category": 3, 
      "difficulty": 2, 
      "id": 15, 
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
```

### POST /questions

#### General
- Creates a new question record
- Returns ID of created question, success value, current paginated questions and total number of questions

#### Sample Request

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question": "Sample Question", "answer": "Sample Answer", "category": 3, "difficulty": 3}' http://127.0.0.1:5000/questions 
```

#### Sample Response

```bash
{
  "created": 30, 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Agra", 
      "category": 3, 
      "difficulty": 2, 
      "id": 15, 
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ], 
  "success": true, 
  "total_questions": 20
}
```

### POST /search

#### General
- Search questions based on a search term (case insensitive)
- Returns list of questions that contain the search term, success value and total questions of resulting questions

#### Sample Request

```bash
curl -X POST -H "Content-Type: application/json" -d '{"searchTerm": "title"}' http://127.0.0.1:5000/questions/search 
```
#### Sample Response

```bash
{
  "questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```

### GET /categories/{category_id}/questions

#### General
- Gets questions based on chosen category
- Returns current category, paginated and total number of questions based on that category, and finally success value

#### Sample Request

```bash
curl http://127.0.0.1:5000/categories/1/questions
```

#### Sample Response

```bash
{
  "current_category": {
    "id": 1, 
    "type": "Science"
  }, 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }, 
    {
      "answer": "There is no such thing", 
      "category": 1, 
      "difficulty": 5, 
      "id": 29, 
      "question": "What is the most popular scientific word"
    }
  ], 
  "success": true, 
  "total_questions": 4
}
```

### POST /quizzes

#### General
- Gets a question to be asnwered for the quiz, as long as it does not belong to the previous questions
- Takes in previous questions and quiz category the player chose
- Returns a new question for the quiz and success value

#### Sample Request

```bash
curl -X POST -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category": {"type": "science", "id": 1}}' http://127.0.0.1:5000/quizzes
```

#### Sample Response

```bash
{
  "question": {
    "answer": "Blood", 
    "category": 1, 
    "difficulty": 4, 
    "id": 22, 
    "question": "Hematology is a branch of medicine involving the study of what?"
  }, 
  "success": true
}
```

## Testing

#### General
Each endpoint is tested for successful and unsuccessful execution. Expected outputs are used for validation
See tests below:
- test_retrieve_all_categories: Test successful retrieval of all categories
- test_retrieve_paginated_questions: Test successful retrieval of paginated questions
- test_404_retrieve_paginated_questions_page_not_found: Test unsuccessful retrieval of non-existing question page
- test_delete_question: Test successful deletion of a question
- test_404_delete_question: Test unsuccessful deletion of a question that does not exist
- test_create_question: Test successful creation of a question
- test_405_create_question_method_not_allowed: Test unsuccessful creation of question where method is not allowed
- test_search_questions: Test successful search of questions - search term found
- test_search_questions_search_term_not_found: Test unsuccessful search of questions - Search term not found
- test_retrieve_questions_by_category: Test successful retrieval of questions by category
- test_404_retrieve_questions_by_category_not_found: Test unsuccessful retrieval of questions where category does not exist
- test_quizzes: Test successful quiz - Question retrieved
- test_500_test_quizzes_no_data: Test unsuccessful quiz - no data - Server Fails

#### Test Execution
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## Deployment - N/A

## Tasks (Completed)

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 
10. Create Unit tests for successful and unsuccessful execution of all endpoints functionality