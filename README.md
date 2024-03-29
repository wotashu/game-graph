# Gamer-Flask
Neo4j Flask App for the Seattle Interactive Media Museum and Gamer Group

Borrows heavily from the neo4j-flask application https://github.com/nicolewhite/neo4j-flask


# Getting Started
Make sure Neo4j is installed and running 
On ubuntu:
```
sudo su
apt-get install python python-dev libffi-dev python-pip python-virtualenv
git clone git@github.com:wotashu/game-graph.git
cd game-graph
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
Edit the gamegraph/models.py file and look for the line
```
authenticate(url.strip('http://'), "neo4j", "u3Sm8kEVFzE81N6n")
```
and replace the username and password with your own.

To start the server type
```
python run.py
```
This creates a development server running on port 5000

# Using gunicorn:
```
pip install gunicorn
gunicorn gamer4j:app
```

This installation of gunicorn seems to work best with Apache2 and mod_wsgi. Should theoretically work with Nginx with correct configuration.
