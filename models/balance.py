# import calendar
# import datetime
# import locale
#
# from polidoro_table import Table
#
# from models import Account, Transaction
# from polidoro_sqlite_utils import SQLiteTable
# from polidoro_sqlite_utils.types import ForeignKey, FloatField, IntegerField, TextField
#
#
# def thousand_format(number):
#     return format(float(number), ',.2f').replace(",", "X").replace(".", ",").replace("X", ".")
#
#
# class Balance(SQLiteTable):
#     account = TextField(default=None, null=True)
#     total_in = FloatField()
#     total_out = FloatField()
#     balance = FloatField()
#     total = FloatField()
#     month = IntegerField()
#     year = IntegerField()
#
#     def __init__(self, *args, **kwargs):
#         for attr in ['balance', 'total', 'total_in', 'total_out']:
#             kwargs.setdefault(attr, 0)
#         super(Balance, self).__init__(*args, **kwargs)
#         value = kwargs.get('account', None)
#         if not isinstance(value, Account) and value and value.isnumeric():
#             value = Account.get(pk=value)
#         if isinstance(value, Account):
#             setattr(self, 'account', value.alias)
#
#     def __add__(self, other):
#         resp = Balance(**self.__dict__)
#         for attr in ['balance', 'total', 'total_in', 'total_out']:
#             setattr(resp, attr, getattr(self, attr) + getattr(other, attr))
#         return resp
#
#     @classmethod
#     def create(cls, account, month, year, force_create=False):
#         som = datetime.date(year, month, 1)
#         eom = datetime.date(year, month, calendar.monthrange(year, month)[1])
#
#         last_month = som - datetime.timedelta(days=1)
#
#         opening_balance = 0
#         ending_balance = 0
#         ending_balance_transaction = Transaction.find(origin=account.id, category='ending_balance', date=(som, eom))
#         if ending_balance_transaction:
#             ending_balance = round(ending_balance_transaction[0].value, 3)
#         opening_balance_transaction = Transaction.find(origin=account.id, category='opening_balance',
#                                                        date=(som, eom))
#         if opening_balance_transaction:
#             opening_balance = round(opening_balance_transaction[0].value, 2)
#
#         if not force_create:
#             last_balance = Balance.find_or_create(account, last_month.month, last_month.year)
#             balance_opening_balance = last_balance.total
#             if opening_balance_transaction:
#                 if opening_balance != balance_opening_balance:
#                     print(f'{account.name} Balance in {last_month.month}/{last_month.year} is wrong.\n'
#                                      f'- Transaction: {opening_balance}\n- Balance: {balance_opening_balance}')
#                     if input(f'Continue with {thousand_format(opening_balance)} as opening balance?[Y/n]: ') not in ['y', '']:
#                         exit(1)
#             else:
#                 opening_balance = balance_opening_balance
#
#         account_transactions = Transaction.all(
#             '(origin = :account or destination = :account) and (date between :som and :eom)',
#             dict(account=account.id, som=som, eom=eom))
#
#         print(f'Creating {month}/{year} {account.name} Balance...')
#         total_in = 0
#         total_out = 0
#         balance = 0
#         for transaction in account_transactions:
#             if transaction.origin == transaction.destination:
#                 continue
#             if transaction.origin == account:
#                 balance -= transaction.value
#                 if transaction.category != 'Transferência':
#                     total_out += transaction.value
#             elif transaction.destination == account:
#                 balance += transaction.value
#                 if transaction.category != 'Transferência':
#                     total_in += transaction.value
#
#         total = round(opening_balance + balance, 2)
#         if ending_balance_transaction and total != ending_balance:
#             raise ValueError(f'{account.name} Balance in {last_month.month}/{last_month.year} is wrong.\n'
#                              f'- Transaction: {ending_balance}\n- Calculated: {total}')
#         return super(Balance, cls).create(account=account, balance=balance, year=year, month=month,
#                                           total=total, total_in=total_in, total_out=total_out)
#
#     def save(self):
#         super(Balance, self).save()
#         if self.account != 'Total':
#             total_balance = Balance.find_or_create(Account(name='Total'), self.month, self.year)
#             total_balance = total_balance + self
#             total_balance.save()
#         return self
#
#     @staticmethod
#     def find_or_create(account, month, year):
#         oldest_transaction = Transaction.all(order_by='date', limit=1)[0]
#         oldest_transaction_date = oldest_transaction.date
#         balance = Balance.find(account=account.alias, month=month, year=year)
#         if balance:
#             return balance[0]
#
#         if oldest_transaction_date >= datetime.date(year, month, 1):
#             balance = Balance.create(account, month, year, force_create=True)
#         else:
#             balance = Balance.create(account, month, year)
#         return balance.save()
#
#     @staticmethod
#     def show(month, year=None):
#         locale.setlocale(locale.LC_ALL, '')
#
#         if year is None:
#             year = month.year
#             month = month.month
#
#         accounts = Account.all()
#
#         t = Table(f'Balance {month}/{year}')
#         t.add_columns(['Account', 'Total in', 'Total out', 'Balance', 'Total'])
#         for account in accounts:
#             balance = Balance.find_or_create(account, month, year)
#             t.add_row([account.name,
#                        thousand_format(balance.total_in),
#                        thousand_format(balance.total_out),
#                        thousand_format(balance.balance),
#                        thousand_format(balance.total),
#                        ])
#         t.add_row(None)
#         total_balance = Balance.find(account='Total', month=month, year=year)[0]
#         t.add_row(['Total',
#                    thousand_format(total_balance.total_in),
#                    thousand_format(total_balance.total_out),
#                    thousand_format(total_balance.balance),
#                    thousand_format(total_balance.total),
#                    ])
#
#         Balance.find_or_create(Account(name='Total'), month=month, year=year)
#         query_str, query_kwargs = Balance.create_query(account='Total', year=year-1)
#         t_last_year = Table('Last Year')
#         t_last_year.add_columns(['Month', 'Total in', 'Total out', 'Balance', 'Total'])
#         for balance in Balance.all(query_str.replace('year = :year', "year >= :year"), query_kwargs):
#             t_last_year.add_row([f'{balance.month}/{balance.year}',
#                                  thousand_format(balance.total_in),
#                                  thousand_format(balance.total_out),
#                                  thousand_format(balance.balance),
#                                  thousand_format(balance.total),
#                                  ])
#         t_last_year.print()
#         t.print()
#
#     @staticmethod
#     def delete_balances(account_alias, date):
#         year = date.year
#         month = date.month
#         if isinstance(account_alias, Account):
#             account_alias = account_alias.alias
#         Balance.delete_where('(account = :account or account = "Total") and month >= :month and year >= :year',
#                              dict(account=account_alias, month=month, year=year))
