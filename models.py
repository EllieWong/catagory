from sqlalchemy import Column, ForeignKey, Integer, String,TIMESTAMP,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'name': self.name
        }


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    create_time = Column(TIMESTAMP,nullable=False,server_default=text("current_timestamp"))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description':self.description,
            'category_id': self.category_id,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///cagegory.db')

Base.metadata.create_all(engine)
