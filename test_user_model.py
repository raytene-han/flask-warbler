"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from flask import g, session
from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError

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

    def test_email_requirement(self):
        """Test that signup fails without a required field"""

        with self.assertRaises(IntegrityError):
            u3 = User.signup("u3", None ,"password", None)
            db.session.commit()

        #CONDITZION 3: Check duplicate usernames cannot be created

    def test_duplicate_username_prompts_error(self):
        """Test that an account cannot be created with a dupelicate username"""

        with self.assertRaises(IntegrityError):
            u3 = User.signup("u2", "u3@email.com", "password", None)
            db.session.commit()


    def test_user_authenticate(self):
        """Test User.authenticate returns the use when given a valid username
        and password, or fails when username/password is invalid."""

        # CONDITION 1: valid credentials

        user = User.authenticate("u1", "password")
        self.assertIsInstance(user, User)

        # CONDITION 2: invalid username

        user = User.authenticate("cat", "password")
        self.assertEqual(user, False)

        # CONDITION 3: invalid password
        user = User.authenticate("u1", "password1")
        self.assertEqual(user, False)


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
        """ Test user1 is following user2.
        check user1.following includes user2
        """


        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        self.assertEqual(u1.is_following(u2),True)


    def test_is_not_following(self):
        """Test user1 is not following user2.
        check user1.following does not include user2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_following(u2), False)


    def test_is_followed_by(self):
        """Test user1 is not followed by user2.
        check user1.followers does not include user2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        self.assertEqual(u1.is_followed_by(u2), True)

    def test_is_not_followed_by(self):
        """Test user1 is followed by user2.
        check user1.followers includes user2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_followed_by(u2), False)

