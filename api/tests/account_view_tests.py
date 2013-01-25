import json

from finance.models import Account, db_session
from view_tests import BaseViewTestCase

class AccountViewTestCase(BaseViewTestCase):

    def setUp(self):
        super(AccountViewTestCase, self).setUp()
        self.account = Account('Insurance', 'Expense', "Safety Net")
        db_session.add(self.account)
        db_session.commit()

    def tearDown(self):
        db_session.delete(self.account)
        super(AccountViewTestCase, self).tearDown()

    def test_view_auth_required(self):
        """Test that authentication is required"""
        rv = self.app.get("/accounts/")
        self.assertEqual(401, rv.status_code)

    def test_view_all(self):
        """Test viewing all accounts"""
        rv = self.open_with_auth(
            "/accounts/",
            'GET',
            self.username,
            self.password
        )
        self.assertEqual(200, rv.status_code)
        data = json.loads(rv.data)
        acct = self.account.jsonify()
        self.assertIn(acct, data['accounts'])

    def test_view_account(self):
        """Test viewing a single account"""
        rv = self.open_with_auth(
            "/accounts/%s" % self.account.account_id,
            "GET",
            self.username,
            self.password
        )
        self.assertEqual(200, rv.status_code)
        self.assertEqual(self.account.jsonify(), json.loads(rv.data))

    def test_view_account_404(self):
        """Test viewing a non-existant account"""
        rv = self.open_with_auth(
            "/accounts/999",
            "GET",
            self.username,
            self.password
        )
        self.assertEqual(404, rv.status_code)
        self.assertIn("404 Not Found", rv.data)

    def test_view_add(self):
        """Test adding an account"""
        name = 'Supplies'
        account_type = 'Expense'
        description = 'Getting things done'
        rv = self.open_with_auth(
            "/accounts/",
            "POST",
            self.username,
            self.password,
            data=dict(
                name=name,
                account_type=account_type,
                description=description
            )
        )
        self.assertEqual(200, rv.status_code)
        self.assertIn('Success', rv.data)

        acct = json.loads(rv.data)
        rv = self.open_with_auth(
            "/accounts/%s" % acct.get('account_id'),
            "GET",
            self.username,
            self.password,
        )

        self.assertEqual(200, rv.status_code)
        acct_get = json.loads(rv.data)
        self.assertEqual(name, acct_get.get('name'))
        self.assertEqual(account_type, acct_get.get('account_type'))
        self.assertEqual(description, acct_get.get('description'))
        self.assertEqual(acct.get('account_id'), acct_get.get('account_id'))

    def test_view_add_fail(self):
        """Test adding an invalid account"""
        name = 'Supplies'
        account_type = 'Exp'
        description = 'Getting things done'
        rv = self.open_with_auth(
            "/accounts/",
            "POST",
            self.username,
            self.password,
            data=dict(
                name=name,
                account_type=account_type,
                description=description
            )
        )
        self.assertEqual(400, rv.status_code)
        self.assertIn('errors', rv.data)

    def test_view_delete(self):
        """Test deleting account"""
        account1 = Account('Entertainment', 'Expense', "Party like it's 1999'")
        db_session.add(account1)
        db_session.commit()
        rv = self.open_with_auth(
            "/accounts/%s" % account1.account_id,
            "DELETE",
            self.username,
            self.password
        )
        self.assertEqual(200, rv.status_code)

        # attempt to get the account
        rv = self.open_with_auth(
            "/accounts/%s" % account1.account_id,
            "GET",
            self.username,
            self.password
        )
        self.assertEqual(404, rv.status_code)

    def test_view_delete_fail(self):
        """Test deleting a non existant account"""
        rv = self.open_with_auth(
            "/accounts/999",
            "DELETE",
            self.username,
            self.password
        )
        self.assertEqual(404, rv.status_code)

    def test_view_update(self):
        """Test updating an account"""
        name = 'Entertainment'
        account_id = self.account.account_id
        rv = self.open_with_auth(
            "/accounts/%s" % account_id,
            "PUT",
            self.username,
            self.password,
            data=dict(
                name=name,
                account_type=self.account.account_type,
                description=self.account.description
            )
        )
        self.assertEqual(200, rv.status_code)
        self.assertIn('Success', rv.data)

        rv = self.open_with_auth(
            "/accounts/%s" % account_id,
            "GET",
            self.username,
            self.password,
        )

        self.assertEqual(200, rv.status_code)
        acct_get = json.loads(rv.data)
        self.assertEqual(name, acct_get.get('name'))


test_cases = [
    AccountViewTestCase
]