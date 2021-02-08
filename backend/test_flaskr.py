import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


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
            'question': 'Which club won the 2020 football champions league?',
            'answer': 'Bayern Munich',
            'category': 6,
            'difficulty': 3
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


    def test_get_categories(self):
        """Test the listing of all categories"""

        res = self.client().get('/categories')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)


    def test_list_questions(self):
        """ Test the listing of all questions """

        res = self.client().get('/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)


    def test_get_questions_by_category(self):
        """ Test the listing of all questions """

        res = self.client().get('/categories/1/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])


    def test_create_new_question(self):
        """ Test the success creation of a question"""

        res = self.client().post('/questions', json=self.new_question)
        # print("Response: ", res.data)

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_failure_create_new_quetion(self):
        """ Test new question creation failure due to no user data """
        res = self.client().post('/questions')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], "unprocessable")

    def test_delete_question(self):
        """Test the success of question delettion """

        res = self.client().delete('/questions/28')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_delete_question(self):
        """Test 404 error when trying to delete not existing question"""

        res =  self.client().get('/qustions/100')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "resource not found")

    def test_search_question(self):
        """ Test the search operation """
        res = self.client().post('/questions', json={'searchTerm': 'soccer'})
        
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)


    def test_play_quizzes_with_no_previous_questions(self):
        """ Test the start of playing the quiz """
        res = self.client().post('/quizzes', json={"quiz_category":{"id":1}, "previous_questions":[]})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] in [20, 21, 22])

    
    def test_play_quizzes_with_previous_questions(self):
        """ Test playing the quiz """
        res = self.client().post('/quizzes', json={"quiz_category":{"id":1}, "previous_questions":[21]})

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 21)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()