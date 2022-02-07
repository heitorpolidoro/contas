from sqlalchemy import Column, Integer, String

from polidoro_model.base import Base


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    alias = Column(String, nullable=False, unique=True)

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

