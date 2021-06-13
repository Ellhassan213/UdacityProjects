import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Movie, Actor
from auth import ASSISTANT_TOKEN, DIRECTOR_TOKEN, PRODUCER_TOKEN


class CastingAgencyTestCase(unittest.TestCase):
    """This class represents the Casting Agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.environ.get("DB_NAME_TEST")
        self.database_path = "postgresql+psycopg2://{}/{}".format(
            os.environ.get("DB_HOST"), self.database_name)
        setup_db(self.app, self.database_path)

        self.new_movie = {
            "title": "Mission Impossible",
            "release_date": "1996-11-20"
        }
        self.new_actor = {
            "name": 'Tom Cruise',
            "age": 45,
            "gender": 'Male'
        }

        self.new_movie_flawed = {
            "title_flawed": "Mission Impossible",
            "release_date_flawed": "1996-11-20"
        }
        self.new_actor_flawed = {
            "name_flawed": 'Tom Cruise',
            "age_flawed": 45,
            "gender_flawed": 'Male'
        }

        self.assistant_header = {
            'Authorization': 'Bearer {}'.format(ASSISTANT_TOKEN)
        }
        self.director_header = {
            'Authorization': 'Bearer {}'.format(DIRECTOR_TOKEN)
        }
        self.producer_header = {
            'Authorization': 'Bearer {}'.format(PRODUCER_TOKEN)
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

    #----------------------------------------------------------------------------#
    # Movie related tests
    #----------------------------------------------------------------------------#

    def test_get_all_movies_success(self):
        res = self.client().get('/movies', headers=self.assistant_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_all_movies_404_not_found(self):
        res = self.client().get('/fake_movies', headers=self.assistant_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_movies_success(self):
        res = self.client().post('/movies', json=self.new_movie, headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_movies_400_bad_request(self):
        res = self.client().post('/movies', json=self.new_movie_flawed,
                                 headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_post_movies_401_not_authorized(self):
        res = self.client().post('/movies', json=self.new_movie, headers=self.director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_movie_success(self):
        res = self.client().patch('/movies/1', json=self.new_movie,
                                  headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_movie_404_not_found(self):
        res = self.client().patch('/movies/999', json=self.new_movie,
                                  headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_movie_success(self):
        create_res = self.client().post('/movies', json=self.new_movie,
                                        headers=self.producer_header)
        create_data = json.loads(create_res.data)
        create_id = create_data['created']

        res = self.client().delete(
            f'/movies/{create_id}', headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_movie_404_not_found(self):
        res = self.client().delete('/fake_movies/1', headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    #----------------------------------------------------------------------------#
    # Actor related tests
    #----------------------------------------------------------------------------#

    def test_get_all_actors_success(self):
        res = self.client().get('/actors', headers=self.assistant_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_all_actors_404_not_found(self):
        res = self.client().get('/fake_actors', headers=self.assistant_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_actor_success(self):
        res = self.client().post('/actors', json=self.new_actor, headers=self.director_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_actors_400_bad_request(self):
        res = self.client().post('/actors', json=self.new_actor_flawed,
                                 headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_post_actors_401_not_authorized(self):
        res = self.client().post('/actors', json=self.new_actor,
                                 headers=self.assistant_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)

    def test_patch_actor_success(self):
        res = self.client().patch('/actors/1', json=self.new_actor,
                                  headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_patch_actor_404_not_found(self):
        res = self.client().patch('/actors/999', json=self.new_actor,
                                  headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_actor_success(self):
        create_res = self.client().post('/actors', json=self.new_actor,
                                        headers=self.director_header)
        create_data = json.loads(create_res.data)
        create_id = create_data['created']

        res = self.client().delete(
            f'/actors/{create_id}', headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_actor_404_not_found(self):
        res = self.client().delete('/fake_actors/1', headers=self.producer_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
