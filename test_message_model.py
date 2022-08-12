"""Message model tests."""



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

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        """Set up two messages."""
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)


        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        m1 = Message(text="test_message", user_id=self.u1_id)
        m2 = Message(text="test_message2", user_id=self.u2_id)

        db.session.commit()
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_create_message(self):
        """Test that messages are successfully created."""

        messages = Message.query.all()

        self.assertEqual(len(messages), 2)

    def test_user_message_relationship(self):
        """Test that user messages can be accessed through relationship."""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.messages),1)
        self.assertEqual(len(u2.messages),1)

