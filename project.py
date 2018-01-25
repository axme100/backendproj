from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash,
    make_response,
    g,
    abort
)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Story, Word, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///storyandword.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


# This route checks the passowrd
@auth.verify_password
def verify_password(username, password):
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


# This method creates a new user, who can make API calls.
@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    name = request.json.get('name')
    email = request.json.get('email')
    if username is None or password is None or name is None or email is None:
        abort(400)  # missing arguments
    if session.query(User).filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username, name=name, email=email)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': user.username}), 201,
    {'Location': url_for('get_user', id=user.id, _external=True)}


# This method will return JSON information of a user if they exist.
@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


# This is an API endpoint that will return all stories
@app.route('/stories/JSON')
@auth.login_required
def storiesJSON():
    stories = session.query(Story).all()
    return jsonify(story=[i.serialize for i in stories])


# This is an API endpoint that willr return all words
@app.route('/words/JSON')
@auth.login_required
def wordsJSON():
    words = session.query(Word).all()
    return jsonify(Word=[i.serialize for i in words])


# The next three functions are helpers to implement user system
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# This is to get userinformation from Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    req = h.request(url, 'GET')[1]
    req_json = req.decode('utf8').replace("'", '"')
    result = json.loads(req_json)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# This disconnects from Google
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com'
    '/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/')
def showHomePage():
    return render_template('homePage.html')


@app.route('/createstory', methods=['GET', 'POST'])
def createStory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        # It seems that when I was testing this app
        # I was able to create stories and add them to the database
        # without being logged in, then I was getting an error
        # When I tried to view the story because there was no username
        # associaed with that story.
        # That is why I added this additional if session
        if 'username' not in login_session:
            return redirect('/login')
        else:
            newStory = Story(
                title=request.form['title'],
                description=request.form['description'],
                text=request.form['text'],
                user_id=login_session['user_id'])
            session.add(newStory)
            session.commit()
            # This counts number of blanks intended for Mad Lib
            # This can and should be made more robust (see readme)
            numberOfBlanks = newStory.text.count('{')
            return render_template(
                'addWords.html',
                newStory=newStory,
                number_of_blanks=numberOfBlanks)
        # If it is a get request render the template with the form
    else:
        return render_template('createStory.html')


@app.route(
    '/addwords/<int:story_id>/<int:number_of_blanks>',
    methods=['GET', 'POST'])
def addWords(story_id, number_of_blanks):
    if request.method == 'POST':
        data = request.form
        dataDict = data.to_dict()
        # At this point I have all the data in a nice dictionary form
        # I just need to loop through it pull out the corresponding word
        # and lexical_category values, and add them to the database.

        for item in range(number_of_blanks):
            newWord = Word(
                word=dataDict["word" + str(item)],
                lexical_category=dataDict["lexical_category" + str(item)],
                story_id=story_id,
                user_id=login_session['user_id'],
                order=item + 1)
            session.add(newWord)
            session.commit()

    return redirect(url_for('showStories'))


@app.route('/stories')
def showStories():
    stories = session.query(Story).all()
    return render_template('stories.html', stories=stories)


@app.route('/viewstory/<int:story_id>')
def viewStory(story_id):
    # Get the specific story that the user clicked on from the database
    story = session.query(Story).filter_by(id=story_id).one()
    user = session.query(User).filter_by(id=story.user_id).one()

    # Get the specific words related to this story that the user clicked on
    words = session.query(Word).filter_by(
        story_id=story_id).order_by('order').all()

    stringStory = story.text
    listOfWords = []

    # Loop through the words and add each word to a list
    for word in words:
        listOfWords.append(word.word)

    # Change the listOfWords into a tuple so that I can pass it into .format()
    tupleList = tuple(listOfWords)

    # Create the complete story using .format()
    # The * unpacks the tuple to prevent index out of range error
    exampleStory = stringStory.format(*tupleList)

    creator = getUserInfo(story.user_id)

    # Sometimes getting key errors here-look into login_session_object
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        # Conditional satisfied
        return render_template('publicStory.html',
                               story=story,
                               exampleStory=exampleStory,
                               user_email=user.email)
    else:
        return render_template('story.html',
                               story=story,
                               exampleStory=exampleStory,
                               user_email=user.email)


@app.route('/editstory/<int:story_id>', methods=['GET', 'POST'])
def editStory(story_id):
    storyToEdit = session.query(Story).filter_by(id=story_id).one()
    if request.method == 'POST':
        storyToEdit.text = request.form['text']
        storyToEdit.title = request.form['title']
        storyToEdit.description = request.form['description']
        session.add(storyToEdit)
        session.commit()
        numberOfBlanks = storyToEdit.text.count('{')
        return redirect(url_for('editWords',
                                number_of_blanks=numberOfBlanks,
                                story_id=story_id))

    return render_template('editStory.html', storyToEdit=storyToEdit)


@app.route('/editwords/<int:story_id>/<int:number_of_blanks>',
           methods=['GET', 'POST'])
def editWords(story_id, number_of_blanks):

    editedStory = session.query(Story).filter_by(id=story_id).one()
    wordsToEdit = session.query(Word).filter_by(story_id=story_id).all()

    if 'username' not in login_session:
        return redirect('/login')
    if editedStory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        "to edit the words of this story.');}"
        "</script><body onload='myFunction()''>"

    if request.method == 'POST':

        # This is the same code from the delete words function
        for word in wordsToEdit:
            session.delete(word)
            session.commit()

        # This is the same code from the add words function
        data = request.form
        dataDict = data.to_dict()

        for item in range(number_of_blanks):
            newWord = Word(word=dataDict["word" + str(item)],
                           lexical_category=dataDict["lexical"
                           "_category" + str(item)],
                           story_id=story_id,
                           order=item + 1)
            session.add(newWord)
            session.commit()
        return redirect(url_for('showStories'))

    return render_template('editWords.html',
                           editedStory=editedStory,
                           old_words=wordsToEdit,
                           number_of_blanks=number_of_blanks)


@app.route('/deletestory/<int:story_id>', methods=['GET', 'POST'])
def deleteStory(story_id):
    deletedWords = session.query(Word).filter_by(id=story_id).all()
    deletedStory = session.query(Story).filter_by(id=story_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deletedStory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized"
        " to delete this restaurant. Please create your own restaurant"
        " in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deletedStory)
        for word in deletedWords:
            session.delete(word)
        session.commit()
        return redirect(url_for('showStories'))
    return render_template('deleteStory.html', story_id=story_id)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
