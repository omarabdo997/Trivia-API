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
        self.database_path = "postgres://{}:{}@{}/{}".format('omar','917356oo','localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res=self.client().get("/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])


    def test_get_questions_404(self):
        res=self.client().get("/questions?page=1000")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"resource not found")
        self.assertEqual(data["error"],404)


    def test_get_categories(self):
        res=self.client().get("/categories")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["categories"])



    def test_get_categories_405(self):
        res=self.client().post("/categories",json={"title":"asd"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,405)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"method not allowed")
        self.assertEqual(data["error"],405)

    def test_delete_question(self):
        res=self.client().delete("/questions/20")
        data=json.loads(res.data)
        question=Question.query.get(20)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["questions"])
        self.assertEqual(question,None)

    def test_delete_question_404(self):
        res=self.client().delete("/questions/1000")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"resource not found")
        self.assertEqual(data["error"],404)

    def test_add_question(self):
        res=self.client().post("/questions",json={"question":"How are you?","category":1,"difficulty":1,"answer":"fine"})
        data=json.loads(res.data)
        question=Question.query.filter(Question.question=="How are you?").all()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(question)

    def test_add_question_400(self):
        res=self.client().post("/questions",json={"question":"How are you?","category":1})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"bad request")
        self.assertEqual(data["error"],400)

    def test_search_questions(self):
        res=self.client().post("/questions/search",json={"searchTerm":"what"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_search_questions_404(self):
        res=self.client().post("/questions/search",json={"searchTerm":"whsadsadaat"})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"resource not found")
        self.assertEqual(data["error"],404)

    def test_get_questions_by_category(self):
        res=self.client().get("/categories/2/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category_404(self):
        res=self.client().get("/categories/10/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"resource not found")
        self.assertEqual(data["error"],404)

    def test_get_quiz(self):
        res=self.client().post("/quizzes",json={"previous_questions":[],"quiz_category":{"type":"Science","id":1}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data["success"],True)
        self.assertTrue(data["question"])

    def test_get_quiz_404(self):
        res=self.client().post("/quizzes",json={"previous_questions":[],"quiz_category":{"type":"Physics","id":8}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"resource not found")
        self.assertEqual(data["error"],404)

    def test_get_quiz_400(self):
        '''Here i called typo instead of type in quiz category dictionary'''
        res=self.client().post("/quizzes",json={"previous_questions":[],"quiz_category":{"typo":"Physics","id":8}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data["success"],False)
        self.assertEqual(data["message"],"bad request")
        self.assertEqual(data["error"],400)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
