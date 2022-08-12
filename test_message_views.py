"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    """Set up user and message for testing."""
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()


class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message_when_logged_in(self):
        """Test that a user can add a message when logged in and when logged out."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/messages/new", data={"text": "Hello"})
            message = Message.query.filter_by(text="Hello").one()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(message.text), 5)

    def test_add_message_when_logged_out(self):
        """ Test that a user cannot add a message when logged out."""

        resp = self.client.post("/messages/new", data={"text": "Hello"},
                          follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)


class MessageDeleteViewTestCase(MessageBaseViewTestCase):
    def test_delete_message_when_logged_in(self):
        """Test that a user can delete a message when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/messages/new", data={"text": "Hello friend"})
            message = Message.query.filter_by(text="Hello friend").one()

            resp = c.post(f"/messages/{message.id}/delete")
            message = Message.query.all()

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(message), 1)

    def test_delete_message_when_logged_out(self):
        """Test that a user can delete a message when logged out"""

        resp = self.client.post(f"/messages/{self.m1_id}/delete",
                          follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", html)