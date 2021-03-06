import json

from flask import abort, jsonify, request, Response
from flask.views import MethodView

import config

from finance import utils, db
from finance.forms.account import AccountForm
from finance.models.account import Account
from finance.stats import STATS


class AccountAPI(MethodView):
    """Account Views"""

    decorators = [
        utils.requires_auth,
        utils.crossdomain(
            origin='*',
            headers=config.HEADERS_ALLOWED
        ),
    ]

    def get(self, account_id):
        if account_id is None:
            with STATS.all_accounts.time():
                # return a list of accounts
                res = [acct.jsonify() for acct in Account.query.all()]
                STATS.success += 1
                return Response(json.dumps(res), mimetype='application/json')
        else:
            with STATS.get_account.time():
                # expose a single account
                acct = Account.query.get(account_id)
                if acct is None:
                    STATS.notfound += 1
                    return abort(404)
                STATS.success += 1
                return jsonify(acct.jsonify())

    def post(self):
        with STATS.add_account.time():
            # create a new account
            form = AccountForm(request.data)
            if form.validate():
                acct = Account(
                    form.name.data,
                    form.acct_type,
                    form.description.data
                )
                db.session.add(acct)
                db.session.commit()
                STATS.success += 1
                return jsonify({
                    'message': 'Successfully added Account',
                    'account_id': acct.account_id
                })
            STATS.validation += 1
            resp = jsonify({"errors": form.errors})
            resp.status_code = 400
            return resp

    def delete(self, account_id):
        with STATS.delete_account.time():
            # delete a single account
            acct = Account.query.get(account_id)
            if acct is None:
                STATS.notfound += 1
                return abort(404)
            db.session.delete(acct)
            db.session.commit()
            STATS.success += 1
            return jsonify({"message": "Successfully deleted Account"})

    def put(self, account_id):
        with STATS.update_account.time():
            # update a single account
            acct = Account.query.get(account_id)
            if acct is None:
                STATS.notfound += 1
                return abort(404)
            form = AccountForm(request.data)
            if form.validate():
                acct = Account.query.get(account_id)
                acct.name = form.name.data
                acct.account_type_id = form.account_type_id.data
                acct.description = form.description.data
                db.session.add(acct)
                db.session.commit()
                STATS.success += 1
                return jsonify({
                    'message': 'Successfully updated Account'
                })
            STATS.validation += 1
            resp = jsonify({'errors': form.errors})
            resp.status_code = 400
            return resp


@utils.requires_auth
@utils.crossdomain(origin='*', headers=config.HEADERS_ALLOWED)
def transactions(account_id):
    """Get transactions for account"""
    with STATS.get_account_transactions.time():
        acct = Account.query.get(account_id)
        if acct is None:
            STATS.notfound += 1
            return abort(404)
        res = [trx.jsonify() for trx in acct.transactions()]
        STATS.success += 1
        return Response(json.dumps(res), mimetype='application/json')
