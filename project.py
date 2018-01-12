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

@app.route('/create')
def createStory():
    return "This is where you will create the Mad Lib (Enter the Story)"


@app.route('/addwords')
def addWords():
    return "This is where you will add the words for a certain story"


@app.route('/stories')
def showStories():
    return "This is where you will see the stories that other users have created"


@app.route('/viewstory')
def viewStory():
    return "This is where you will see a specific story that a user has create"

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