from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from polidoro_model import Base


class Category(Base):
    __tablename__ = 'category'
    __table_str__ = '$category'
    __custom_str__ = '$category $(fixed_origin.alias)->$(fixed_destination.alias)'
    __default_filter_attribute__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    regex = Column(String)
    fixed_origin_id = Column(Integer, ForeignKey('account.id'))
    fixed_origin = relationship("Account", foreign_keys=[fixed_origin_id])
    fixed_destination_id = Column(Integer, ForeignKey('account.id'))
    fixed_destination = relationship("Account", foreign_keys=[fixed_destination_id])
    ask_for_confirmation = Column(Boolean, nullable=False, default=True)

