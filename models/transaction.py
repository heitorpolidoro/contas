from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship

from models import Account
from polidoro_model import Base
from polidoro_terminal import Format


class Transaction(Base):
    __tablename__ = 'transaction'
    __custom_str__ = f'$date $reason {Format.BOLD}R$$ $value{Format.NORMAL} ' \
                     'Origem: $(origin.name) Destino: $(destination.name)'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", foreign_keys=[category_id])
    origin_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    origin = relationship("Account", foreign_keys=[origin_id])
    destination_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    destination = relationship("Account", foreign_keys=[destination_id])
    value = Column(Float, nullable=False)
    reason = Column(String, nullable=True)

    def __init__(self, *args, **kwargs):
        super(Transaction, self).__init__(*args, **kwargs)
        if isinstance(self.origin, str):
            self.origin = Account.filter(alias=self.origin)[0]
        if isinstance(self.destination, str):
            self.destination = Account.filter(alias=self.destination)[0]
            
    def ask_attribute(self, attr):
        if self.category:
            if attr == 'origin' and self.category.fixed_origin:
                self.set_attribute(attr, self.category.fixed_origin)
                return
            elif attr == 'destination' and self.category.fixed_destination:
                self.set_attribute(attr, self.category.fixed_destination)
                return
        Base.ask_attribute(self, attr)

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
