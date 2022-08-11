"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from flask import g, session
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """Set up two users."""
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_signup(self):
        """Test that signing up creates a new user."""

        users = User.query.all()
        u1 = User.query.get(self.u1_id)

        self.assertEqual(u1.email, "u1@email.com")
        self.assertEqual(len(users), 2)

        # CONDITION 2: Check user signup fails

        u3 = User.signup("u3", "u3", "password", None)
        self.assertEqual(len(users), 2)

    def test_user_model(self):
        """Check new user model has no messages and no followers."""
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_repr(self):
        """Test repr method works as expected.
        use assertEqual for repr output
        """

        u1 = User.query.get(self.u1_id)
        self.assertIn( "u1, u1@email.com", str(u1))


    def test_is_following(self):
        """CONDITION 1: Test user1 is following user2.
        check user1.following includes user2

        CONDITION 2: Test user1 is not following user2.
        check user1.following does not include user2
        """
        # CONDITION 1

        with self.client.session_transaction() as sess:
            sess['curr_user'] = self.u1_id

        resp = self.client.post(f'/users/follow/{self.u2_id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.following), 1)
        self.assertIn(u2.username, html)

        # CONDITION 2

        resp = self.client.post(f'/users/stop-following/{self.u2_id}')
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.following), 0)
        self.assertNotIn(u2.username, html)




    def test_is_followed_by(self):
        """CONDITION 1: Test user1 is followed by user2.
        check user1.followers includes user2

        CONDITION 2: Test user1 is not followed by user2.
        check user1.followers does not include user2
        """

        #CONDITION 1

        with self.client.session_transaction() as sess:
            sess['curr_user'] = self.u2_id

        resp = self.client.post(f'/users/follow/{self.u1_id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.followers), 1)
        self.assertIn(u1.username, html)

        # CONDITION 2

        resp = self.client.post(f'/users/stop-following/{self.u1_id}')
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.followers), 0)
        self.assertNotIn(u1.username, html)


