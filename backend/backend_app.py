import json
import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS_FILE = 'posts.json'

POSTS = [
    {"id": 1,
     "title": "First post",
     "content": "This is the first post.",
     "author": "Viktoria Sarkisian",
     "date": "2023-07-14"},
    {"id": 2,
     "title": "Second post",
     "content": "This is the second post.",
     "author": "Viktoria Sarkisian",
     "date": "2023-07-15"}
]


def setup():
    if not os.path.exists(POSTS_FILE):
        # Save the initial POSTS list to the JSON file
        with open(POSTS_FILE, 'w') as file:
            json.dump(POSTS, file, indent=2)


def read_posts():
    try:
        with open(POSTS_FILE, 'r') as file:
            posts = json.load(file)
        return posts
    except FileNotFoundError:
        return []


def write_posts(posts):
    with open(POSTS_FILE, 'w') as file:
        json.dump(posts, file, indent=2)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction')

    if sort_field and sort_direction:
        if sort_field not in ['title', 'content', 'author', 'date']:
            return jsonify({'error': 'Invalid sort filed'}), 400

        if sort_direction not in ['asc', 'desc']:
            return jsonify({'error': 'Invalid sort direction.'}), 400

        # Perform sorting based on the provided sort filed and direction
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_field], reverse=sort_direction == 'desc')
        return jsonify(sorted_posts)

    else:
        return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    if 'title' not in data or not data['title']:
        return jsonify({'error': 'Title is required.'}), 400

    if 'content' not in data or not data['content']:
        return jsonify({'error': 'Content is required.'}), 400

    if 'author' not in data or not data['author']:
        return jsonify({'error': 'Author is required.'}), 400

    if 'date' not in data or not data['date']:
        return jsonify({'error': 'Date is required.'}), 400

    new_post = {
        'id': len(POSTS) + 1,
        'title': data['title'],
        'content': data['content'],
        'author': data['author'],
        'date': data['date']
    }

    POSTS.append(new_post), 201

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for post in POSTS:
        if post['id'] == post_id:
            POSTS.remove(post)
            return jsonify({'message': f'Post with id {post_id} has been deleted successfully.'}), 200

    return jsonify({'error': f"Post with id {post_id} does not exist."}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    for post in POSTS:
        if post['id'] == post_id:
            if 'title' in data:
                post['title'] = data['title']
            if 'content' in data:
                post['content'] = data['content']
            if 'author' in data:
                post['author'] = data['author']
            if 'date' in data:
                post['date'] = data['date']

            return jsonify(post), 200

    return jsonify({'error': f'Post with id {post_id} does not exist'}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title_query = request.args.get('title')
    content_query = request.args.get('content')
    author_query = request.args.get('author')
    date_query = request.args.get('date')
    id_query = request.args.get('id')

    posts = read_posts()

    matching_posts = []

    for post in posts:
        if (id_query and post['id'] == int(id_query)) or \
                (title_query and title_query.lower() in post['title'].lower()) or \
                (content_query and content_query.lower() in post['content'].lower()) or \
                (author_query and author_query.lower() in post['author'].lower()) or \
                (date_query and date_query == post['date']):
            matching_posts.append(post)

    return jsonify(matching_posts)


def get_sort_value(value):
    if value == 'date':
        return lambda x: datetime.strptime(x[value], '%Y-%m-%d')
    return lambda x: x[value]


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
