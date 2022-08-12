"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from urllib.request import url2pathname

from flask import g, session
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """Set up two users."""
        User.query.delete()

        u1 = User.signup("username1", "u1@email.com", "password", None)
        u2 = User.signup("username2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_following(self):
        """CONDITION 1: Test user1 is following user2.
        check user1.following includes user2

        CONDITION 2: Test user1 is not following user2.
        check user1.following does not include user2
        """
        # CONDITION 1

        with self.client.session_transaction() as sess:
            sess['curr_user'] = self.u1_id

        resp = self.client.post(f'/users/follow/{self.u2_id}',
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(u1.following), 1)
        self.assertIn(u2.username, html)

        # CONDITION 2

        resp = self.client.post(f'/users/stop-following/{self.u2_id}',
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(u1.following), 0)
        self.assertNotIn(u2.username, html)




    def test_followers(self):
        """CONDITION 1: Test user1 is followed by user2.
        check user1.followers includes user2

        CONDITION 2: Test user1 is not followed by user2.
        check user1.followers does not include user2
        """

        #CONDITION 1

        with self.client.session_transaction() as sess:
            sess['curr_user'] = self.u2_id

        resp = self.client.post(f'/users/follow/{self.u1_id}',
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(u1.followers), 1)
        self.assertIn(u1.username, html)

        # CONDITION 2

        resp = self.client.post(f'/users/stop-following/{self.u1_id}',
                                follow_redirects=True)
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(u1.followers), 0)
        self.assertNotIn(u1.username, html)

    def test_see_follower_pages_logged_in(self):
        """CONDITION 1: Test if you can see follower/following pages for any
        user when logged in."""

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u1_id

        resp = self.client.get(f"/users/{self.u2_id}/following")
        html = resp.get_data(as_text=True)

        u2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(u2.username, html)

    def test_sewe_follower_pages_logged_out(self):
        """  Test if you can see follower/following pages for any
        user when logged out. """

        resp = self.client.get(f"/users/{self.u2_id}/following",
                               follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)




