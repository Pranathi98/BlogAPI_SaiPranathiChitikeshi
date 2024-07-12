import os

from decouple import config
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY', default='enter_secret_key')
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# MongoDB connection
mongo_uri = config('MONGO_URI_DEV')
client = MongoClient(mongo_uri)
db = client.get_database()
users_collection = db.users
posts_collection = db.posts
counters_collection = db.counters

#counter to get ids in order
if counters_collection.count_documents({'_id': 'postid'}) == 0:
    counters_collection.insert_one({'_id': 'postid', 'seq': 0})

#to find out what is the next sequence based on previous id
def get_next_sequence_value(sequence_name):
    sequence_document = counters_collection.find_one_and_update(
        {'_id': sequence_name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return sequence_document['seq']

#signup with id and password for authentication
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        abort(400, description="Missing 'username' or 'password'")

    if users_collection.find_one({'username': data['username']}):
        abort(400, description="Username already exists")

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = {
        'username': data['username'],
        'password': hashed_password
    }
    users_collection.insert_one(user)
    return jsonify({"message": "User created successfully"}), 201

#login with id and password for authentication
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        abort(400, description="Missing 'username' or 'password'")

    user = users_collection.find_one({'username': data['username']})
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity=data['username'])
        return jsonify(access_token=access_token), 200

    abort(401, description="Invalid username or password")

#post method to create blog with title and content
@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    if 'title' not in data or 'content' not in data:
        abort(400, description="Missing 'title' or 'content'")

    post_id = get_next_sequence_value('postid')

    post = {
        '_id': post_id,
        'title': data['title'],
        'content': data['content']
    }
    #to insert collection
    posts_collection.insert_one(post)
    return jsonify(post), 201

#get method to get all the blogs
@app.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    posts = list(posts_collection.find())
    return jsonify(posts), 200

#get method to get blog by id
@app.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    post = posts_collection.find_one({'_id': post_id})
    if post is None:
        abort(404, description=f"Post with ID {post_id} not found")
    return jsonify(post), 200

#update method to update blogs based on id
@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    data = request.get_json()
    post = posts_collection.find_one({'_id': post_id})
    if post is None:
        abort(404, description=f"Post with ID {post_id} not found")

    update_data = {}
    if 'title' in data:
        update_data['title'] = data['title']
    if 'content' in data:
        update_data['content'] = data['content']

    posts_collection.update_one({'_id': post_id}, {'$set': update_data})
    post = posts_collection.find_one({'_id': post_id})
    return jsonify(post), 200

#delete method to delete a blog based on id
@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    result = posts_collection.delete_one({'_id': post_id})
    if result.deleted_count == 0:
        abort(404, description=f"Post with ID {post_id} not found")
    return jsonify({"message": f"Post with ID {post_id} has been deleted successfully"}), 200

#error handler for bad request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

#error handler for not found
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

#error handler for unautherized
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': str(error)}), 401

#error handler for forbiddden
@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': str(error)}), 403

if __name__ == '__main__':
    app.run(debug=True)
