"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for Users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
    
    def test_anon_access(self):
        """When non authenticated anonymous users try to vist routes, they are rejected and sent to sign up"""

        with self.client as c:

            # /  
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)

            # /users/1/following 
            resp = c.get("/users/1/following")
            self.assertEqual(resp.status_code, 302)

            # /users/1/followers
            resp = c.get("/users/1/followers")
            self.assertEqual(resp.status_code, 302)

            # /users/follow/1
            resp = c.post("/users/follow/1")
            self.assertEqual(resp.status_code, 302)

            # /users/stop-following/1
            resp = c.post("/users/stop-following/1")
            self.assertEqual(resp.status_code, 302)

            # /users/profile
            resp = c.get("/users/profile")
            self.assertEqual(resp.status_code, 302)

            # /users/delete
            resp = c.post("/users/delete")
            self.assertEqual(resp.status_code, 302)

    def test_authenticated_user_routes(self):

        u2 = User.signup(username="test2user",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = u2.id
            # /  
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)

            # /users/1/following 
            resp = c.get("/users/1/following")
            self.assertEqual(resp.status_code, 200)

            # /users/1/followers
            resp = c.get("/users/1/followers")
            self.assertEqual(resp.status_code, 200)

            # /users/follow/1
            resp = c.post("/users/follow/1")
            self.assertEqual(resp.status_code, 302)

            # /users/stop-following/1
            resp = c.post("/users/stop-following/1")
            self.assertEqual(resp.status_code, 302)

            # /users/profile
            resp = c.get("/users/profile")
            self.assertEqual(resp.status_code, 200)

            # /users/delete
            resp = c.post("/users/delete")
            self.assertEqual(resp.status_code, 302)