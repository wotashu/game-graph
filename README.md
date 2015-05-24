# Gamer-Flask
Neo4j Flask App for Gamer Group

On ubuntu
```
sudo su
apt-get install python python-dev libffi-dev python-pip python-virtualenv
git clone git@github.com:wotashu/game-graph.git
cd game-graph
virtualenv env
source venv/bin/activate
pip install -r requirements.txt
python run.py
```
Using gunicorn:
```
pip install gunicorn
gunicorn gamer4j:app
```

Opens on port 5000
