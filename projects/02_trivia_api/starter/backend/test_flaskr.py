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

        self.DB_HOST = os.getenv('DB_HOST', '192.168.1.70:5432')
        self.DB_USER = os.getenv('DB_USER', 'pi')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '20202020')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia_test')
        self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass
# this is a dual test i am testing retreiveal of questions and the pagination
    def test_quesions_and_pagi_questies(self):
        req = self.client().get('/questions')
        data = json.loads(req.data)
        # lets test questions and pagination at the same time
        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        # testing pagination here
        self.assertEqual(len(data['questions']), 10)
        # lets also check to make sure we only have 6 categories
        self.assertEqual(data['total_categories'], 6)

# lets test adding the most important question of all time in all the galaxy!
    def test_add_me_a_question_baby_yoda(self):

        baby_yoda = {
            'question': 'are you the one for me?',
            'answer': 'yes yoda one for meeee',
            'difficulty': 1,
            'category': 1
        }
        #starwars joke get it?
        # the difficulty and category are 1 as in the yoda one for me
        req = self.client().post('/questions', json=baby_yoda)
        data = json.loads(req.data)

        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'question added')
# testing all category retreiveal
    def test_get_categories(self):

        req = self.client().get('/categories')
        data = json.loads(req.data)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
# testing invalid catigoriy id's
    def test_invalid_category_id(self):

          req = self.client().get('/categories/1234/questions')
          data = json.loads(req.data)

          self.assertEqual(req.status_code, 422)
          self.assertEqual(data['success'], False)
          self.assertEqual(data['message'], 'Unprocessable Entity')
# testing valid categroy id
    def test_valid_category_id(self):


          req = self.client().get('/categories/6/questions')
          data = json.loads(req.data)

          self.assertEqual(req.status_code, 200)
          self.assertEqual(data['success'], True)
          self.assertTrue(data['questions'])
          self.assertTrue(data['totalQuestions'])
          self.assertTrue(data['currentCategory'])

# testing question searching
    def test_search_questions(self):

        q = {'searchTerm': 'largest lake in Africa'}

        req = self.client().post('/question/search', json=q)
        data = json.loads(req.data)

        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

# testing question deletion
    def test_question_deletion(self):

        # creating a question to then delete it
        question = Question(question='Test question', answer='yoda one to delete',
                                difficulty=3, category=2)
        question.insert()
        question_id = question.id

        req = self.client().delete(f'/questions/{question_id}')
        data = json.loads(req.data)
        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)
# testing the quiz to make sure it runs
    def test_play_quiz(self):

        data = {'previous_questions': [],
        'quiz_category': {'type': 'History', 'id': 4}
        }
        req = self.client().post('/quizzes', json=data)
        data = json.loads(req.data)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

# testing the quiz to fail without data
    def test_play_without_data(self):

        req = self.client().post('/quizzes', json={})
        data = json.loads(req.data)

        self.assertEqual(req.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "it was a bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
