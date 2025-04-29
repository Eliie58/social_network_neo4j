# social_network.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from neo4j import GraphDatabase
from dataclasses import dataclass
from typing import List, Optional

# ======================
# Database Access Layer
# ======================
class Database:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
     
    # User operations
    def create_user(self, id, username, name):
        query = (
            "CREATE (u:User {id: $id, username: $username, name: $name}) RETURN u"
        )
        with self.driver.session() as session:
            result = session.run(query, id=id, username=username, name=name)
            return result.single()["u"]

    def get_user(self, username):
        query = "MATCH (u:User {username: $username}) RETURN u"
        with self.driver.session() as session:
            record = session.run(query, username=username).single()
            return record["u"] if record else None

    def get_all_users(self):
        query = "MATCH (u:User) RETURN u"
        with self.driver.session() as session:
            return [record["u"] for record in session.run(query)]
    
    # Post operations
    def create_post(self, post_id, user_id, content):
        query = (
            "MATCH (u:User {id: $user_id}) "
            "CREATE (p:Post {id: $post_id, content: $content, timestamp: datetime()}) "
            "CREATE (u)-[:AUTHORED]->(p) RETURN p"
        )
        with self.driver.session() as session:
            return session.run(query, post_id=post_id, user_id=user_id, content=content).single()["p"]

    def get_posts_by_user(self, user_id):
        query = (
            "MATCH (u:User {id: $user_id})-[:AUTHORED]->(p:Post) "
            "RETURN p ORDER BY p.timestamp DESC"
        )
        with self.driver.session() as session:
            return [r["p"] for r in session.run(query, user_id=user_id)]
    
    def get_feed(self, user_id):
        query = (
            "MATCH (u:User {id: $user_id})-[:FOLLOWS]->(f:User)-[:AUTHORED]->(p:Post) "
            "RETURN p, f ORDER BY p.timestamp DESC"
        )
        with self.driver.session() as session:
            return [ {"post": r["p"], "author": r["f"]} for r in session.run(query, user_id=user_id) ]
    
    # Follow operations
    def follow_user(self, follower_id, followee_id):
        query = (
            "MATCH (a:User {id: $follower}), (b:User {id: $followee}) "
            "MERGE (a)-[:FOLLOWS]->(b)"
        )
        with self.driver.session() as session:
            session.run(query, follower=follower_id, followee=followee_id)

    def unfollow_user(self, follower_id, followee_id):
        query = (
            "MATCH (a:User {id: $follower})-[r:FOLLOWS]->(b:User {id: $followee}) "
            "DELETE r"
        )
        with self.driver.session() as session:
            session.run(query, follower=follower_id, followee=followee_id)

    def get_followers(self, user_id):
        query = (
            "MATCH (f:User)-[:FOLLOWS]->(u:User {id: $user_id}) RETURN f"
        )
        with self.driver.session() as session:
            return [r["f"] for r in session.run(query, user_id=user_id)]

    def get_following(self, user_id):
        query = (
            "MATCH (u:User {id: $user_id})-[:FOLLOWS]->(f:User) RETURN f"
        )
        with self.driver.session() as session:
            return [r["f"] for r in session.run(query, user_id=user_id)]

# ======================
# Web Application
# ======================
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
db = Database("bolt://localhost:7687", "neo4j", "QUANGdang14032005")

# Sample data initialization
with app.app_context():
    # Create some sample users if they don't exist
    if not db.get_all_users():
        db.create_user('alice', 'Alice Smith')
        db.create_user('bob', 'Bob Johnson')
        db.create_user('charlie', 'Charlie Brown')

# ======================
# API Endpoints
# ======================
@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(db.get_all_users())

@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = db.get_user(user_id)
    return jsonify(user) if user else ('User not found', 404)

@app.route('/api/users/<int:user_id>/posts', methods=['GET'])
def api_get_user_posts(user_id):
    return jsonify(db.get_posts_by_user(user_id))

@app.route('/api/users/<int:user_id>/feed', methods=['GET'])
def api_get_user_feed(user_id):
    return jsonify(db.get_feed(user_id))

@app.route('/api/users/<int:user_id>/followers', methods=['GET'])
def api_get_user_followers(user_id):
    return jsonify(db.get_followers(user_id))

@app.route('/api/users/<int:user_id>/following', methods=['GET'])
def api_get_user_following(user_id):
    return jsonify(db.get_following(user_id))

@app.route('/api/posts', methods=['POST'])
def api_create_post():
    data = request.get_json()
    post_id = db.create_post(data['user_id'], data['content'])
    return jsonify({'post_id': post_id}), 201

@app.route('/api/follow', methods=['POST'])
def api_follow_user():
    data = request.get_json()
    success = db.follow_user(data['follower_id'], data['followee_id'])
    return jsonify({'success': success}), 201 if success else 200

# ======================
# Frontend Routes
# ======================
@app.route('/')
def home():
    users = db.get_all_users()
    current_user = None
    if 'user_id' in session:
        current_user = db.get_user(session['user_id'])
    return render_template('index.html', users=users, current_user=current_user)

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = db.get_user(user_id)
    if not user:
        return "User not found", 404
        
    current_user = None
    is_following = False
    
    if 'user_id' in session:
        current_user = db.get_user(session['user_id'])
        if current_user and current_user['id'] != user_id:
            # Check if current user is following this profile user
            following = db.get_following(current_user['id'])
            is_following = any(f['id'] == user_id for f in following)
    
    posts = db.get_posts_by_user(user_id)
    followers = db.get_followers(user_id)
    following = db.get_following(user_id)
    
    return render_template('profile.html', 
                         user=user, 
                         posts=posts,
                         followers=followers,
                         following=following,
                         current_user=current_user,
                         is_following=is_following)

@app.route('/user/<int:user_id>/feed')
def user_feed(user_id):
    user = db.get_user(user_id)
    feed = db.get_feed(user_id)
    return render_template('feed.html', user=user, feed=feed)

@app.route('/create_post', methods=['POST'])
def create_post():
    user_id = int(request.form['user_id'])
    content = request.form['content']
    db.create_post(user_id, content)
    return redirect(url_for('user_profile', user_id=user_id))

@app.route('/login/<int:user_id>')
def login(user_id):
    session['user_id'] = user_id
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/follow', methods=['POST'])
def follow():
    follower_id = int(request.form['follower_id'])
    followee_id = int(request.form['followee_id'])
    
    # Check if the user is already following
    following = db.get_following(follower_id)
    is_following = any(f['id'] == followee_id for f in following)
    
    if is_following:
        # Implement unfollow functionality (you'll need to add this to your Database class)
        db.unfollow_user(follower_id, followee_id)
    else:
        db.follow_user(follower_id, followee_id)
    
    return redirect(url_for('user_profile', user_id=followee_id))

# ======================
# HTML Templates
# ======================
@app.route('/templates/<template_name>')
def serve_template(template_name):
    return render_template(template_name)

# Template rendering functions
app.jinja_env.globals.update(
    render_index=lambda: render_template('index.html', users=db.get_all_users()),
    render_profile=lambda user_id: render_template(
        'profile.html',
        user=db.get_user(user_id),
        posts=db.get_posts_by_user(user_id),
        followers=db.get_followers(user_id),
        following=db.get_following(user_id)
    )
)

# Migration Script
def migrate(sqlite_path, neo4j_uri, neo4j_user, neo4j_pass):
    # Connect SQLite
    sq = sqlite3.connect(sqlite_path)
    cur = sq.cursor()

    # Connect Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    with driver.session() as session:
        # Create constraints
        session.run("CREATE CONSTRAINT unique_user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;")
        session.run("CREATE CONSTRAINT unique_post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE;")

        # Migrate users
        for user in cur.execute("SELECT id, username, name FROM users"):
            session.run(
                "CREATE (u:User {id: $id, username: $username, name: $name})",
                id=user[0], username=user[1], name=user[2]
            )

        # Migrate posts
        for post in cur.execute("SELECT id, user_id, content, timestamp FROM posts"):
            session.run(
                "MATCH (u:User {id: $user_id}) CREATE (p:Post {id: $id, content: $content, timestamp: datetime($timestamp)}) CREATE (u)-[:AUTHORED]->(p)",
                id=post[0], user_id=post[1], content=post[2], timestamp=post[3]
            )

        # Migrate follows
        for f in cur.execute("SELECT follower_id, followee_id FROM follows"):
            session.run(
                "MATCH (a:User {id: $follower}), (b:User {id: $followee}) MERGE (a)-[:FOLLOWS]->(b)",
                follower=f[0], followee=f[1]
            )
    driver.close()

if __name__ == '__main__':
    app.run(debug=True, port=5050)