import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))


class Story(Base):
	__tablename__ = 'story'
	
	title = Column(
		String(80), nullable = False)

	description = Column(
		String(80), nullable = False)

	text = Column(
		String(80), nullable = False)

	id = Column(
		Integer, primary_key = True)

	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		# Returns object data in easily serializeable format

		return {
			'title' : self.title,
			'description' : self.description,
			'text' : self.text,
			'id' : self.id
		}

class Word(Base):
	__tablename__ = 'word'

	word = Column(String(80), nullable = False)
	lexical_category = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	story_id = Column(
		Integer, ForeignKey('story.id'))
	story = relationship(Story)

	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		# Returns object data in easily serializeable format

		return {
			'word' : self.word,
			'lexical_category' : self.lexical_category,
			'id' : self.id,
			'story_id' : self.story_id,
			'user_id' : self.user_id
		}

engine = create_engine(
'sqlite:///storyandword.db')

Base.metadata.create_all(engine)