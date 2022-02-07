# import re
#
# from models import Account
# from models.category import Category
# from polidoro_sqlite_utils import SQLiteTable
# from polidoro_sqlite_utils.types import TextField, ForeignKey
#
#
# class ReasonRule(SQLiteTable):
#     regex = TextField()
#     category = ForeignKey(Category)
#     origin = ForeignKey(Account, default=None, null=True)
#     destination = ForeignKey(Account, default=None, null=True)
#
#     _rules = []
#
#     @classmethod
#     def find_rule(cls, reason):
#         for rule in cls.get_rules():
#             if re.match(rule.regex, reason):
#                 return rule
#
#     @classmethod
#     def get_rules(cls):
#         if not ReasonRule._rules:
#             ReasonRule._rules = cls.all()
#         return ReasonRule._rules
#
