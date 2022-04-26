import calendar
import datetime
import locale
from collections import defaultdict

from sqlalchemy import Column, Integer, ForeignKey, Float, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship

from models import Account, Transaction, Category
from polidoro_model import Base
from polidoro_table import Table


def thousand_format(value):
    return f'{value:n}'


class Balance(Base):
    __tablename__ = 'balance'
    __table_attributes__ = ['month', 'year', 'account', 'total_in', 'total_out', 'balance', 'total']
    # __option_str__ = '$category'
    # __table_str__ = '$category'
    __custom_str__ = '$(account.alias) $balance'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", foreign_keys=[account_id])
    total_in = Column(Float, nullable=False)
    total_out = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Balance, self).__init__(*args, **kwargs)
        self.total_in = self.total_in or 0
        self.total_out = self.total_out or 0
        self.balance = self.balance or 0
        self.total = self.total or 0

    def __add__(self, other):
        self.total_in += other.total_in
        self.total_out += other.total_out
        self.balance += other.balance
        self.total += other.total
        return self

    @classmethod
    def create(cls, account, month, year, force_create=False):
        som = datetime.date(year, month, 1)
        eom = datetime.date(year, month, calendar.monthrange(year, month)[1])
        outer_account = Account.filter(name='Externa').one()
        last_month = som - datetime.timedelta(days=1)

        opening_balance, opening_balance_transaction = cls.get_balance_value(account, 'opening_balance', eom, som)
        ending_balance, ending_balance_transaction = cls.get_balance_value(account, 'ending_balance', eom, som)

        if not force_create:
            last_balance = Balance.find_or_create(account, last_month.month, last_month.year)
            balance_opening_balance = last_balance.total
            if opening_balance_transaction:
                if opening_balance != balance_opening_balance:
                    print(f'{account.name} Balance in {last_month.month}/{last_month.year} is wrong.\n'
                          f'- Transaction: {opening_balance}\n- Balance: {balance_opening_balance}')
                    exit(1)
            else:
                opening_balance = balance_opening_balance

        account_transactions = Transaction.filter(
            or_(Transaction.origin == account, Transaction.destination == account), date=(som, eom))

        print(f'Creating {month}/{year} {f"{account.bank}-{account.name}" if account else "Total"} Balance...')
        total_in = 0
        total_out = 0
        balance = 0
        for transaction in account_transactions:
            if transaction.origin == transaction.destination:
                continue
            if transaction.origin == account:
                balance -= transaction.value
                if transaction.destination == outer_account:
                    total_out += transaction.value
            elif transaction.destination == account:
                balance += transaction.value
                if transaction.origin == outer_account:
                    total_in += transaction.value

        total = round(opening_balance + balance, 2)
        if ending_balance_transaction and total != ending_balance:
            raise ValueError(f'{account.bank}-{account.name} Balance in {month}/{year} is wrong.\n'
                             f'- Transaction: {ending_balance}\n- Calculated: {total}')
        return Balance(account=account, balance=balance, year=year, month=month,
                       total=total, total_in=total_in, total_out=total_out)

    @staticmethod
    def get_balance_value(account, category, eom, som):
        category_balance = Category.filter(fixed_origin=account, category=category).first()
        if category_balance:
            balance_transaction = Transaction.filter(origin=account, category=category_balance,
                                                     date=(som, eom)).first()
            if balance_transaction:
                balance_value = round(balance_transaction.value, 2)
                return balance_value, balance_transaction
        return 0, None

    @staticmethod
    def find_or_create(account, month, year):
        balance = Balance.filter(account=account, month=month, year=year).first()
        if balance:
            return balance

        oldest_transaction = Transaction.all().order_by('date').first()
        oldest_transaction_date = oldest_transaction.date
        force_create = oldest_transaction_date >= datetime.date(year, month, 1)
        balance = Balance.create(account=account, month=month, year=year, force_create=force_create)
        balance.save()
        return balance

    @staticmethod
    def get_total_balance(month):
        year = month.year
        month = month.month

        # accounts = defaultdict(Balance)
        total_balance = Balance.find_or_create(account=None, month=month, year=year)
        total_balance.total_in = 0
        total_balance.total_out = 0
        total_balance.balance = 0
        total_balance.total = 0
        for account in Account.all():
            if account.id == 1:
                continue
            balance = Balance.find_or_create(account, month, year)
            total_balance += balance
        return total_balance
        t.print()
