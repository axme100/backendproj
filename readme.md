# Spanlib

This project aims to create a pedagogical web application that allows students of Spanish and other foreign languages to create Mad Libs and learn about grammar at the same time. If you don't know what a Mad Lib is then you should read this wikipedia page: `https://en.wikipedia.org/wiki/Mad_Libs`

## Initializing the database and adding sample entries

To get started, first fork and clone this repository. `cd` into the repository and run the following commands in the terminal:
```
python3 database_setup.py
python3 add_samples.py
```
The first command will run a python that script that sets up the database and the second command will add some sample entries to the database.

## Adding your Google API credentials. 
You will need to add your Google API credentials as a file named client_secrets.json to the working directory. As of now, the only way to login to this app (which is needed to create a Mad Lib is through the Google OAuth API)
Follow the instructions in this video: `https://www.youtube.com/watch?time_continue=8&v=8aGoty0VXgw`


## Assessing the API
In order to access the API end points `stories/JSON` and `words/JSON` which will respectively provide all of the words and stories in the database, you must create an account. To do this, you will need to send a POST request to the `/api/users` route.

For example, use curl on the command line as so: 

`curl -i -X POST -H "Content-Type: application/json" -d '{"username":"Max","password":"testpassword","name":"max","email":"max@max.com"}' http://localhost:8000/api/users`


Now, when sending GET requets to the API endpoints: `stories/JSON` and `words/JSON` make sure to provide your username and password that were created witht he previous commands

For example, use using curl as so:

```curl -u Max:testpassword -i -X GET http://localhost:8000/words/JSON``` will return all of the words in the database

Or as so:

```curl -u Max:testpassword -i -X GET http://localhost:8000/stories/JSON``` will return all of the words. 


You will return all of the words and stories (respectively) that are stored in the database.

## Looking to the future
The point of this stage is to satisfy the requirements for the Udacity Full Stack Web Developer Nanodegree Program. Here are some things that can be improved.

### Add CSS and Javascript
At this point, this app is pretty bare bones (lacks CSS). Add CSS and javascript to make it pretty.

### Make the createStory() function more robust.
As of now the create story method relies on `numberOfBlanks = newStory.text.count('{')` that is, it just counts the number of curly braces and then determines how many words the user should input on the next screen. This should be made much more robust in order to prevent errors created by the user 

### Incorporate more linguistic theory
As of now, users are only able to select different nouns. This will be expanded to cover many more lexical categories.

### Add a play Mad Lib function. This is where users will be able to actually "play" the Mad Libs that are in the database. This will probably be the most important component of this app once it is created.
