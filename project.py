from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Story, Word
from flask import session as login_session
import random
import string
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

#Connect to Database and create database session
engine = create_engine('sqlite:///storyandword.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/')
def showHomePage():
    return "This will be the homepage of my MadLibs App"

@app.route('/createstory', methods=['GET', 'POST'])
def createStory():
    if request.method == 'POST':
      newStory = Story(title = request.form['title'], description = request.form['description'], text = request.form['text'])
      session.add(newStory)
      session.commit()
      numberOfBlanks = newStory.text.count('{')
      return render_template('addWords.html', newStory = newStory, number_of_blanks = numberOfBlanks)
    # If it is a get request render the template with the form
    else:
        return render_template('createStory.html')


@app.route('/addwords/<int:story_id>/<int:number_of_blanks>)')
def addWords(story_id, number_of_blanks):
    print(story_id)
    print(number_of_blanks)

@app.route('/stories')
def showStories():
    stories = session.query(Story).all()
    return render_template('stories.html', stories = stories)


@app.route('/viewstory/<int:story_id>')
def viewStory(story_id):
    # Get the specific story that the user clicked on from the database
    story = session.query(Story).filter_by(id=story_id).one()
    
    # Get the specific words related to this story that the user clicked on
    words = session.query(Word).filter_by(story_id=story_id).all()

    stringStory = story.text
    listOfWords = []

    # Loop through the words all of the database rows returned and add each word to a list
    for word in words:
    	listOfWords.append(word.word)
    
    # Change the listOfWords into a tuple so that I can pass it into .format()
    tupleList = tuple(listOfWords)
    
    # Create the complete story using .format() the * unpacks the tuple to prevent index out of range error
    exampleStory = stringStory.format(*tupleList)
    
    print(exampleStory)
    
    return render_template('story.html', story = story, exampleStory = exampleStory)


@app.route('/editstory')
def editStory():
    return "This is where you will edit a story: I can render similar templates to the create story"


@app.route('/deletestory')
def deleteStory():
    return "This will be a confirmation page to make sure that users want to delete their stories"


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)