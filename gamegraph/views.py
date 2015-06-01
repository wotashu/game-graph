from models import User, get_todays_recent_games, get_users_recent_games, get_all_games, get_game, MyForm
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def index():
    games = get_todays_recent_games()
    return render_template('index.html', games=games)

app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            error = 'Your username must be at least one character.'
        elif len(password) < 5:
            error = 'Your password must be at least 5 characters.'
        elif not User(username).set_password(password).register():
            error = 'A user with that username already exists.'
        else:
            flash('Successfully registered. Please login.')
            return redirect(url_for('login'))

    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username)

        if not user.verify_password(password):
            error = 'Invalid login.'
        else:
            session['username'] = user.username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/add_game', methods=['POST'])
def add_game():
    user = User(session['username'])
    title = request.form['title']
    tags = request.form['tags']
    genre = request.form['genre']
    platform = request.form['platform']

    if not title:
        abort(400, 'You must give your game a title.')
    if not tags:
        abort(400, 'You must give your game at least one tag.')
    if not genre:
        abort(400, 'You must give at least one genre')

    user.add_game(title, tags, genre, platform)
    flash("Game Added")
    return redirect(url_for('index'))


@app.route('/add_node', methods=['GET', 'POST'])
def add_node():
    user = User(session['username'])
    node_type = request.form['node_type']
    node_title = request.form['node_title']
    node_notes = request.form['node_notes']

    if not node_type:
        abort(400, 'You must give a node type')

    elif not node_title:
        abort(400, 'You must the node a title')

    elif not node_notes:
        abort(400, 'You must explain this node with notes')

    user.add_node(node_type, node_title, node_notes)
    flash("Node Added")
    return redirect(url_for('new_node'))


@app.route('/add')
def new_node():
    return render_template('new_node.html')


@app.route('/all_games')
def index2():
    games = get_all_games()
    return render_template('all_games.html', games=games)


@app.route('/like_game/<game_id>', methods=['GET'])
def like_game(game_id):
    username = session.get('username')
    if not username:
        abort(400, 'You must be logged in to like a game.')

    user = User(username)
    user.like_game(game_id)
    flash('Liked game.')
    return redirect(request.referrer)


@app.route('/game/<game_title>', methods=['GET'])
def game_profile(game_title):
    games = get_game(game_title)
    return render_template('game.html', games=games)


@app.route('/profile/<profile_username>', methods=['GET'])
def profile(profile_username):
    games = get_users_recent_games(profile_username)

    similar = []
    common = []

    viewer_username = session.get('username')
    if viewer_username:
        viewer = User(viewer_username)
        # If they're visiting their own profile, show similar users.
        if viewer.username == profile_username:
            similar = viewer.get_similar_users()
        # If they're visiting another user's profile, show what they
        # have in common with that user.
        else:
            common = viewer.get_commonality_of_user(profile_username)

    return render_template(
        'profile.html',
        username=profile_username,
        games=games,
        similar=similar,
        common=common
    )


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))


@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('submit.html', form=form)

