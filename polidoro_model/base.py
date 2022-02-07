import os
from abc import ABC

from sqlalchemy import Column, Integer, create_engine, inspect
from sqlalchemy.orm import declarative_base, DeclarativeMeta, sessionmaker

# s.add(Account(name='a', alias=1))
# s.commit()
os.environ['DB_URL'] = 'sqlite:///contas.db'


class Base(DeclarativeMeta):
    session = None

    def __init__(self, class_name, *args, **kwargs):
        super(Base, self).__init__(class_name, *args, **kwargs)
        print(self)
        if class_name != 'Base' and Base.session is None:
            engine = create_engine(os.environ.get('DB_URL', ''))
            session = sessionmaker()
            session.configure(bind=engine)
            BaseType.metadata.create_all(engine)
            Base.session = session()

    def create(cls):
        print('create', cls)
        for attr in inspect(cls).attrs:
            print(attr, attr.key)
        return cls()


BaseType = declarative_base(metaclass=Base)


def _save(self):
    print('save', self)


BaseType.save = _save

#--------------------
class Foo(BaseType):
    __tablename__ = 'foo'

    id = Column(Integer, primary_key=True)


class Foo2(BaseType):
    __tablename__ = 'foo2'

    id = Column(Integer, primary_key=True)


f = Foo.create()
f.save()
