import os
import types
from functools import wraps

import sqlite_utils

from polidoro_sqlite_utils.types import BaseField, ForeignKey, IntegerField, TextField, TimeField, DatetimeField, \
    DateField

SQLITE_DB = os.environ.get('SQLITE_DB', 'database.db')


class Index(object):  # pragma: no cover
    def __init__(self, columns, index_name=None, unique=False):
        self.columns = columns
        self.index_name = index_name
        self.unique = unique
        self.if_not_exists = True


def iterceptor(func, cls):
    def from_generator(result):
        if isinstance(result, types.GeneratorType):
            return [cls(**r) for r in result]
        return result

    @wraps(func)
    def wrapper(*args, **kwargs):
        return from_generator(func(*args, **kwargs))

    if isinstance(func, types.MethodType):
        return wrapper
    return from_generator(func)


class SQLiteTableType(type):
    def __init__(self, *args, **kwargs):
        super(SQLiteTableType, self).__init__(*args, **kwargs)

        attributes = dict(id=IntegerField())
        for attr, attr_type in vars(self).items():
            if isinstance(attr_type, BaseField):
                attributes[attr] = attr_type
        self.attributes = attributes

    def __getattr__(self, item):
        try:
            def wrapper(*args, **kwargs):
                resp = iterceptor(getattr(self._table(), item), self)(*args, **kwargs)
                if item == 'delete_where':
                    sqlite_utils.Database(SQLITE_DB).conn.commit()
                return resp

            return wrapper
        except AttributeError:
            raise AttributeError(f"type object '{self.__name__}' has no attribute '{item}'")


class BaseModel(metaclass=SQLiteTableType):
    _attributes = {}

    def __init__(self, **attributes):
        self.id = attributes.get('id', None)
        for attr, attr_type in self.attributes.items():
            setattr(self, attr, attr_type.parse(attributes.get(attr, None)))

    def __str__(self):
        attributes = []
        for attr, attr_type in self.attributes.items():
            value = attr_type.parse(getattr(self, attr, ''))
            attributes.append(f'{attr}: {value}')
        return f'<{self.__class__.__name__}: {", ".join(attributes)}>'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.id == getattr(other, 'id', None)

    @classmethod
    def _table(cls):
        return sqlite_utils.Database(SQLITE_DB)[cls.__table_name()]

    @classmethod
    def __table_name(cls):
        return cls.__name__.lower()

    @staticmethod
    def get_model(model):
        for sub_class in BaseModel.__subclasses__():
            if model == sub_class.__name__.lower():
                return sub_class
        raise Exception(f'Model "{model}" not found!')

    @classmethod
    def all(cls, *args, **kwargs):
        return cls.rows_where(*args, **kwargs)

    @classmethod
    def find(cls, **kwargs):
        return cls.all(*cls.create_query(**kwargs))

    @classmethod
    def create_query(cls, **kwargs):
        query = []
        attributes = cls.attributes
        for attr, value in dict(kwargs).items():
            if isinstance(attributes[attr], (DatetimeField, DateField, TimeField)) and \
                    isinstance(value, str) and ',' in value:
                value = tuple(value.split(','))

            if value is None:
                query.append(f'{attr} is null')
            elif isinstance(attributes[attr], TextField):
                query.append(f'{attr} like :{attr}')
            elif isinstance(value, tuple):
                del kwargs[attr]
                kwargs[f'{attr}_from'] = value[0]
                kwargs[f'{attr}_to'] = value[1]
                query.append(f'{attr} between :{attr}_from and :{attr}_to')
            else:
                query.append(f'{attr} = :{attr}')

        if query:
            return ' and '.join(query), kwargs
        return tuple()

    @classmethod
    def create(cls, ask_only_not_null=False, **attrs):
        entity = cls(**attrs)
        for attr, attr_type in cls.attributes.items():
            value = getattr(entity, attr, None)

            if value is None and (not attr_type.null or not ask_only_not_null):
                value = attr_type.ask(attr)

            if value == '':
                value = None
            setattr(entity, attr, attr_type.parse(value))
        return entity

    @classmethod
    def print(cls, entries=None):
        if entries is None:
            entries = cls.all()
        if not isinstance(entries, list):
            entries = [entries]

        for e in entries:
            print(e)

    @classmethod
    def get(cls, pk):
        return cls(**cls._table().get(pk))

    @classmethod
    def delete(cls, *args, **kwargs):
        if len(args) == 1:
            return cls._table().delete(args[0])
        else:
            return cls.delete_where(*cls.create_query(**kwargs))

    # @classmethod
    # def print_as_table(cls, show_id=False, **kwargs):
    #     from polidoro_table import Table
    #     t = Table(cls.__name__)
    #     attributes = {}
    #     if show_id:
    #         attributes['id'] = IntegerField()
    #     attributes.update(cls.attributes)
    #     for attr in attributes.keys():
    #         t.add_column(attr)
    #
    #     for info in cls.find(**kwargs):
    #         row = []
    #         for attr, attr_type in attributes.items():
    #             value = attr_type.parse(getattr(info, attr, ''))
    #             if hasattr(value, '_value_in_table'):
    #                 value = value._value_in_table()
    #             row.append('' if value is None else value)
    #         t.add_row(row)
    #
    #     t.print()

    def save(self):
        print('Not Implemented')
        # cls = self.__class__
        # attrs = dict(id=getattr(self, 'id', None))
        # for attr, field in self.attributes.items():
        #     v = getattr(self, attr, field.default)
        #     if v is None and not field.null:
        #         raise ValueError(f'{attr} can not be None')
        #     if isinstance(v, SQLiteTable):
        #         attrs[attr] = v.id
        #     else:
        #         attrs[attr] = v
        #
        # if attrs['id']:
        #     list(cls.upsert(attrs, pk='id').rows)[0]
        #     new_self = cls.get(attrs['id'])
        # else:
        #     del attrs['id']
        #     cls.insert(attrs, pk='id')
        #     new_self = cls.find(**attrs)[-1]
        # self.id = new_self.id
        # if hasattr(cls, 'Meta'):
        #     for index in getattr(cls.Meta, 'indexes', []):
        #         cls.create_index(**vars(index))
        return self
