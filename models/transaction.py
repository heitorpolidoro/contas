# from models import Account
# from polidoro_sqlite_utils import SQLiteTable
# from polidoro_sqlite_utils.types import ForeignKey, FloatField, TextField, DateField
#
#
# class Transaction(SQLiteTable):
#     date = DateField()
#     category = TextField(null=True)
#     origin = ForeignKey(Account, default=None, null=True)
#     destination = ForeignKey(Account, default=None, null=True)
#     value = FloatField()
#     reason = TextField()
#
#     def __init__(self, *args, **kwargs):
#         super(Transaction, self).__init__(*args, **kwargs)
#         self.original_reason = kwargs.get('original_reason', self.reason)
#         if self.category not in ['opening_balance', 'ending_balance']:
#             self.value = abs(self.value)
#
#     def save(self):
#         transaction = super(Transaction, self).save()
#         Transaction.delete_balances(transaction)
#         return transaction
#
#     @classmethod
#     def find(cls, transaction=None, **kwargs):
#         if transaction:
#             find_dict = dict(
#                 date=transaction.date,
#                 value=transaction.value,
#                 reason=transaction.reason,
#                 origin=transaction.origin.id if transaction.origin else None,
#                 destination=transaction.destination.id if transaction.destination else None
#             )
#             for attr in kwargs.get('ignores', []):
#                 del find_dict[attr]
#             return Transaction.find(**find_dict)
#         return super(Transaction, cls).find(**kwargs)
#
#     @staticmethod
#     def delete_balances(transaction):
#         from models import Balance
#         if transaction.origin:
#             Balance.delete_balances(transaction.origin, transaction.date)
#         if transaction.destination:
#             Balance.delete_balances(transaction.destination, transaction.date)
#
#     @classmethod
#     def delete(cls, *args, **kwargs):
#         if len(args) == 1:
#             transactions_to_delete = [Transaction.get(args[0])]
#         else:
#             transactions_to_delete = Transaction.find(*args, **kwargs)
#         for transaction in transactions_to_delete:
#             Transaction.delete_balances(transaction)
#         super(Transaction, cls).delete(*args, **kwargs)
#
#     def __str__(self):
#         origin = self.origin
#         if isinstance(origin, Account):
#             origin = origin.alias
#         destination = self.destination
#         if isinstance(destination, Account):
#             destination = destination.alias
#         from polidoro_terminal import Format
#
#         category = ''
#         if self.category:
#             category = Format.BOLD + "(" + self.category + ")" + Format.NORMAL
#         return f'Data: {self.date} ' \
#                f'Reason: {self.original_reason} {category} ' \
#                f'Value: {self.value} ' \
#                f'Origin: {origin} Destination: {destination}'
