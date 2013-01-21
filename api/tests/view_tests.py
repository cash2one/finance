import base64
import json
import unittest

import finance

from finance.models import User, db_session

class BaseViewTestCase(unittest.TestCase):

    def setUp(self):
        self.username = 'admin'
        self.password = 'secret'
        self.user = User(self.username, self.password)
        db_session.add(self.user)
        db_session.commit()
        self.app = finance.app.test_client()

    def tearDown(self):
        db_session.delete(self.user)
        db_session.commit()
        db_session.remove()

    def open_with_auth(self, url, method, username, password, data=None):
        return self.app.open(
            url,
            method=method,
            headers={
                'Authorization': 'Basic ' + base64.b64encode(
                    username + ":" + password
                )
            },
            data=data,
            follow_redirects=True
        )

    def login(self, username, password):
        return self.app.post("/login", data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get("/logout", follow_redirects=True)

class GeneralViewTestCase(BaseViewTestCase):

    def test_login(self):
        """Test logging in """
        rv = self.login(self.username, self.password)
        self.assertEqual(200, rv.status_code)
        self.assertIn("Success", json.loads(rv.data).get('message'))

        rv = self.app.get("/accounts/")
        self.assertEqual(200, rv.status_code)

    def test_logout(self):
        """Test logging out"""
        rv = self.logout()
        self.assertEqual(200, rv.status_code)
        self.assertIn('Success', json.loads(rv.data).get('message'))

        rv = self.app.get("/accounts/")
        self.assertEqual(401, rv.status_code)

test_cases = [
    GeneralViewTestCase
]