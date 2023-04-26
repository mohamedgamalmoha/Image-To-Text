import os
import io
from flask import url_for
from flask_testing import TestCase

from web import app, db
from web.models import User


TEST_IMAGE = 'test_image.png'


class TestAuth(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SECRET_KEY'] = 'secret'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.remove('web/test.db')

    def test_signup(self):
        """Test signing up for new user"""
        # Init user data
        data = {'email': 'test1@example.com', 'password': 'password', 'username': 'username1'}
        data['confirm_password'] = data['password']
        # Send a POST request to the REST API to create new account
        response = self.client.post(url_for('signup'), data=data)
        # Check that the response has a 201 CREATED status code
        self.assertEqual(response.status_code, 201)
        # Check that the user is successfully created
        self.assertIn(b'User has successfully created', response.data)
        user = User.query.filter_by(email=data['email']).first()
        # Check that the user is located in database
        self.assertIsNotNone(user)

    def test_login(self):
        """Test logging in an existing user"""
        # Create new user & commit to the database
        data = {'email': 'test2@example.com', 'password': 'password', 'username': 'username2'}
        user = User.create_user(**data)
        db.session.add(user)
        db.session.commit()
        # Send a POST request to the REST API to login & get access token
        response = self.client.post(url_for('login'),
                                    data={k: v for k, v in data.items() if k in ('email', 'password')})
        # Check that the response has a 200 OK status code
        self.assert200(response)
        # Check that the access token is returned
        self.assertIn(b'access_token', response.data)

    def test_invalid_login(self):
        """Test logging in with invalid credentials"""
        # Create new user & commit to the database
        user = User.create_user(email='test3@example.com', password='password', username='username3')
        db.session.add(user)
        db.session.commit()
        data = user.as_dict()
        # Update password to a different value
        data['password'] = 'wrong_password'
        # Send a POST request to the REST API to login
        response = self.client.post(url_for('login'), data={k: v for k, v in data.items() if k in ('email', 'password')})
        # Check that the response has a 401 UNAUTHORIZED status code
        self.assert401(response)
        # Check that invalid message is returned
        self.assertIn(b'Invalid email or password', response.data)


class TestText(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SECRET_KEY'] = 'secret'
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()
        # Create a test user
        data = {'email': 'test@example.com', 'password': 'password', 'username': 'username'}
        user = User.create_user(**data)
        # Commit to the database
        db.session.add(user)
        db.session.commit()
        # Send a POST request to the REST API to get the access token
        self.auth_response = self.client.post(url_for('login'),
                                              data={k: v for k, v in data.items() if k in ('email', 'password')})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        os.remove('web/test.db')
        os.remove(f'web/images/{TEST_IMAGE}')

    def get_auth_headers(self):
        # Get access token form the auth response
        access_token = self.auth_response.json['access_token']
        return {'Authorization': 'Bearer ' + access_token}

    def test_extract_text_from_image(self):
        """Test image to text with valid image & token"""
        # Read image anc convert it into byte stram
        with open(TEST_IMAGE, 'rb') as f:
            image = io.BytesIO(f.read())
        # Send a POST request to the REST API with the test image
        response = self.client.post(url_for('image_to_text'), data={'image': (image, TEST_IMAGE)},
                                    headers=self.get_auth_headers())
        # Extract the response data as a dictionary
        data = response.get_json()
        # Check that the response has a 200 OK status code
        self.assert200(response)
        # Assert that the 'text' field of the response data matches the expected value
        self.assertEqual(data['text'],
                         "This is the first line of\nthis text example.\n\nThis is the second line\nof the same text.\n")
        # Assert that the 'num_words' field of the response data matches the expected value
        self.assertEqual(data['num_words'], 18)
        # Assert that the 'image_size' field of the response data matches the expected value
        self.assertEqual(data['image_size'], '336x150')
        # Assert that the 'language' field of the response data matches the expected value
        self.assertEqual(data['language'], 'eng')
        # Assert that the 'avg_confidence' field of the response data is greater than or equal to 60
        self.assertGreaterEqual(data['avg_confidence'], 80)
        # Assert that the 'num_chars' field of the response data matches the expected value
        self.assertEqual(data['num_chars'], 88)
        # Assert that the 'image_format' field of the response data matches the expected value
        self.assertEqual(data['image_format'], 'PNG')
        # Assert that the 'dpi' field of the response data is None
        self.assertIsNone(data['dpi'])
        # Assert that the 'extraction_time' field of the response data is not None
        self.assertIsNotNone(data['extraction_time'])
        # Assert that the 'hocr' field of the response data is not None
        self.assertIsNotNone(data['hocr'])

    def test_missed_image(self):
        """Test image to text without image"""
        # Send a POST request to the REST API without the test image
        response = self.client.post(url_for('image_to_text'), headers=self.get_auth_headers())
        # Check that the response has a 400 BAD_REQUEST status code
        self.assert400(response)

    def test_unauthorized_access(self):
        """Test image to text without image"""
        # Read image anc convert it into byte stram
        with open(TEST_IMAGE, 'rb') as f:
            image = io.BytesIO(f.read())
        # Send a POST request to the REST API without headers - authentication Bearer -
        response = self.client.post(url_for('image_to_text'),  data={'image': (image, TEST_IMAGE)},)
        # Check that the response has a 401 UNAUTHORIZED status code
        self.assert401(response)
