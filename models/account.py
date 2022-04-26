from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean

from polidoro_model import Base


class Account(Base):
    class Type(Enum):
        checking_account = 'checking_account'
        auto_invest = 'auto_invest'
        credit_card = 'credit_card'
        other = 'other'
    __tablename__ = 'account'
    __custom_str__ = '$class: $bank-$name($alias)-$type'
    __option_str__ = '$bank-$name'
    __table_str__ = '$bank-$name'
    __attributes_options__ = {'type': list(t.value for t in Type)}

    id = Column(Integer, primary_key=True, autoincrement=True)
    bank = Column(String, nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    alias = Column(String, nullable=False, unique=True)
    merged_balance = Column(Boolean, nullable=False, default=False)

    # def ask_attribute(self, attribute):
    #     default = None
    #     if attribute == 'name':
    #         default = f'{self.bank} - {self.type}'
    #     Base.ask_attribute(self, attribute, default=default)

    # def __init__(self, *args, **kwargs):
    #     super(Account, self).__init__(*args, **kwargs)
    #     if self.alias is None:
    #         self.alias = self.name

    # @classmethod
    # def create(cls, name=None, alias=None):
    #     attrs = {}
    #     if name is not None:
    #         attrs['name'] = name
    #     if alias is not None:
    #         attrs['alias'] = alias
    #     return super(Account, cls).create(**attrs)

    # @classmethod
    # def get(cls, pk):
    #     try:
    #         if isinstance(pk, Account):
    #             return pk
    #         return super(Account, cls).get(pk)
    #     except NotFoundError:
    #         resp = cls.find(alias=pk)
    #         if resp:
    #             return resp[0]
    #         raise
    #
    # def _value_in_table(self):
    #     return self.name
