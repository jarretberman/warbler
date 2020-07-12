"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_signup_user(self):
        """Does signup class method work?"""

        u = User.signup(
            username='testuser',
            email='test@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )

        db.session.add(u)
        db.session.commit()

        #User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        #User password should be encrypted and not stored as entered password
        self.assertNotEqual('testtest', u.password)

        u2 = User.signup(
            username='testuser',
            email='test2@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )
        db.session.add(u2)

        #Raises error when a non-unique username is committed to the db
        self.assertRaises(IntegrityError,db.session.commit())

    def test_authenicate_user(self):
        """Does authenticate class method work"""

        u = User.signup(
            username='testuser',
            email='test@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )

        db.session.add(u)
        db.session.commit()

        #Properly authenticates when password is correct
        self.assertEqual(u, User.authenticate(username='testuser',password='testtest'))
        #Returns false if it can't authenticate
        self.assertFalse(User.authenticate(username='testuser',password='wrongpassword'))

    def test_is_following(self):
        """Does is_following method work"""

        u = User.signup(
            username='testuser',
            email='test@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )
        u2 = User.signup(
            username='testuser2',
            email='test2@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )
        db.session.add_all([u,u2])
        db.session.commit()

        #Should return false when the users are not following eachother
        self.assertFalse(u.is_following(u2))

        u.following.append(u2)
        db.session.commit()

        #Should return true when a user is following another
        self.assertTrue(u.is_following(u2))

    def test_is_followed_by(self):

        u = User.signup(
            username='testuser',
            email='test@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )
        u2 = User.signup(
            username='testuser2',
            email='test@test.com',
            password= 'testtest',
            image_url= '/test/url',
        )
        
        db.session.add_all([u,u2])
        db.session.commit()

        #Should return false when the users are not following eachother
        self.assertFalse(u.is_followed_by(u2))

        u.following.append(u2)
        db.session.commit()

        #Should return true when a user is following another
        self.assertTrue(u2.is_followed_by(u))
