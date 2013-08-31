from sqlalchemy.orm import mapper, relationship

from finance.models.user import User, users
from finance.models.account_type import AccountType, account_types
from finance.models.account import Account, accounts
from finance.models.transaction import Transaction, transactions


def set_model_mapping():
    mapper(User, users, order_by='username')

    mapper(
        AccountType,
        account_types,
        properties={
            'accounts': relationship(Account, backref='account_type'),
        },
        order_by='name'
    )

    mapper(
        Account,
        accounts,
        properties={
            'debits': relationship(Transaction, backref='debit',
                                   foreign_keys=[
                                       transactions.c.account_debit_id
                                   ]),
            'credits': relationship(Transaction, backref='credit',
                                    foreign_keys=[
                                        transactions.c.account_credit_id
                                    ]),
        },
        order_by='name'
    )

    mapper(Transaction, transactions, order_by='date')