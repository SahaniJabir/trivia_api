import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

MESSAGE_NOT_FOUND = 'resource not found.'
MESSAGE_UNPROCESSABLE = 'unprocessable.'
MESSAGE_SERVER_ERROR = 'internal server error'

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the scientific name for humans?',
            'answer': 'Homo sapiens',
            'difficulty': 31,
            'category': '3'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions_pagination(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions_all'])
        self.assertTrue(len(data['questions']))

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['categories_all'])

    def test_create_question(self):

        questions_saved = Question.query.all()
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        questions_after = Question.query.all()
        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(questions_after) - len(questions_saved) == 1)
        self.assertIsNotNone(question)

    def test_delete_question(self):

        question = Question.query.order_by(Question.id.desc()).first()
        question_id = question.id
        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)
        question = Question.query.get(question_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertIsNone(question)

    def test_get_guesses_error_no_category(self):
        response = self.client().post('/quizzes')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], MESSAGE_UNPROCESSABLE)

    def test_search_questions(self):

        response = self.client().post('/questions',json={'searchTerm': 'Homo sapiens'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 33)

    def test_search_questions_fails(self):
        response = self.client().post('/questions',json={'searchTerm': 'abcd'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], MESSAGE_NOT_FOUND)




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
