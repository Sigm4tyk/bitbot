from flask import Flask, request, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your secret key'
CORS(app) # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') 
db = SQLAlchemy(app)

class User(db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        nickname (str): The nickname of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def json(self):
        """
        Returns a dictionary representation of the user.

        Returns:
            dict: A dictionary containing the user's id, nickname, and email.
        """
        return {'id': self.id, 'nickname': self.nickname, 'email': self.email}


db.create_all()

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'The server is running!'})

@app.route('/api/flask/users', methods=['POST'])   
def create_user():
    try:
        data = request.get_json()
        new_user = User(nickname=data['nickname'], email=data['email'], password_hash=generate_password_hash(data['password']))
        db.session.add(new_user)
        db.session.commit()
    
        return jsonify({
            'id': new_user.id,
            'nickname': new_user.nickname,
            'email': new_user.email
        }), 201
    
    except Exception as e:
        return make_response(jsonify({'message': 'error creating user', 'error': str(e)}), 500)
    

    
@app.route('/api/flask/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([user.json() for user in users]), 200
    except Exception as e:
        return make_response(jsonify({'message': 'error getting users', 'error': str(e)}), 500)
    
@app.route('/api/flask/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify(user.json()), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting user', 'error': str(e)}), 500)
    
@app.route('/api/flask/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.nickname = data['nickname']
            user.email = data['email']
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error updating user', 'error': str(e)}), 500)
    
@app.route('/api/flask/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error deleting user', 'error': str(e)}), 500)
    
@app.route('/api/flask/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # store user id in session
            return make_response(jsonify({'message': 'login successful'}), 200)
        return make_response(jsonify({'message': 'invalid credentials'}), 401)
    except Exception as e:
        return make_response(jsonify({'message': 'error during login', 'error': str(e)}), 500)
    
@app.route('/api/flask/logout', methods=['POST'])
def logout():
    try:
        session.pop('user_id', None)  # remove user id from session
        return make_response(jsonify({'message': 'logout successful'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': 'error during logout', 'error': str(e)}), 500)
    
@app.route('/api/flask/logged_in', methods=['GET'])
def logged_in():
    if 'user_id' in session:
        return jsonify({'message': 'user is logged in'}), 200
    else:
        return jsonify({'message': 'user is not logged in'}), 401