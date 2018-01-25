from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Story, Base, Word, User

engine = create_engine('sqlite:///storyandword.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Add example user
user1 = User(name="Wizard", email="databasewizard@protonmail.ch", )
session.add(user1)
session.commit()


# Add first example story
story1 = Story(title="Ejemplo 1",
               description="Esta es una historia muy interesante",
               text="Una vez fui al {} para buscarme un buen de {}",
               user_id=user1.id)

session.add(story1)
session.commit()


word1 = Word(word="mago",
             lexical_category="msn",
             story=story1,
             user_id=user1.id,
             order=1)

session.add(word1)
session.commit()

word2 = Word(word="amigos",
             lexical_category="msn",
             story=story1,
             user_id=user1.id,
             order=2)

session.add(word2)
session.commit()


# Add second example story
story2 = Story(title="Example 2",
               description="Esta es una historia muy aburrida",
               text="Cuantos {} puedes comer. Yo solo puedo comer {}",
               user_id=user1.id)

session.add(story2)
session.commit()


word3 = Word(word="mago",
             lexical_category="msn",
             story=story2,
             user_id=user1.id,
             order=1)

session.add(word3)
session.commit()


word4 = Word(word="dos",
             lexical_category="número",
             story=story2,
             user_id=user1.id,
             order=2)

session.add(word4)
session.commit()


# Add a third story

# Add second example story
story3 = Story(title="Example 3",
               description="This is a sample story in English",
               text="I like to eat {} because it is very delicous",
               user_id=user1.id)

session.add(story3)
session.commit()


word5 = Word(word="pizza",
             lexical_category="msn",
             story=story3,
             user_id=user1.id,
             order=1)

session.add(word5)
session.commit()


word6 = Word(word="delicious",
             lexical_category="number",
             story=story3,
             user_id=user1.id,
             order=2)

session.add(word6)
session.commit()

print("Added 3 example stories!")
