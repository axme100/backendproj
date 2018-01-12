import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Story(Base):
	__tablename__ = 'story'
	
	text = Column(
		String(80), nullable = False)

	id = Column(
		Integer, primary_key = True)

	@property
	def serialize(self):
		# Returns object data in easily serializeable format

		return {
			'story' : self.story,
			'id' : self.id,
		}

class Word(Base):
	__tablename__ = 'word'

	word = Column(String(80), nullable = False)
	lexical_category = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	story_id = Column(
		Integer, ForeignKey('story.id'))
	story = relationship(Story)

	@property
	def serialize(self):
		# Returns object data in easily serializeable format

		return {
			'word' : self.word,
			'description' : self.lexical_category,
			'id' : self.id,
			'story_id' : self.story_id,
		}


engine = create_engine(
'sqlite:///storyandword.db')

Base.metadata.create_all(engine)