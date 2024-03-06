from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from database import create_tables, db_session, User, Token, Video, Vl

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'the most secretive a secret key can get'
CORS(app)

create_tables()
bcrypt = Bcrypt()
    
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    username = data['username']
    password = data['password']
    if db_session.query(User).filter(User.username==username).first():
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(username=username, password=hashed_password)
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'success': True, 'message': 'Registration successful'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    username = data['username']
    password = data['password']
    user = db_session.query(User).filter(User.username==username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        new_access = Token(username=username, token=access_token)
        #remove entry if there is already one associated with user
        user_authenticated = db_session.query(Token).filter(Token.username==username).first()
        if user_authenticated:
            db_session.delete(user_authenticated)
            db_session.commit()
        db_session.add(new_access)
        db_session.commit()
        global uname
        uname = username
        return jsonify({'success': True, 'message': 'Login successful', 'token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/auth/logout', methods=['POST'])
def logout():
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/auth/get_user_using_token', methods=['POST'])
def get_user_using_token():
    data = request.get_json()
    if 'token' not in data:
        return jsonify({'error': 'Need token'}), 400
    token = data['token']
    access = db_session.query(Token).filter(Token.token==token).first()
    return jsonify({'success': True, 'message': 'Username retrieved', 'username': access.username}), 200

@app.route('/auth/get_token', methods=['POST'])
def get_token():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'No access'}), 400
    username = data['username']
    access = db_session.query(Token).filter(Token.username==username).first()
    return jsonify({'success': True, 'message': 'Token retrieved', 'token': access.token}), 200

@app.route('/auth/fetch_username', methods=['GET'])
def fetch_username():
    return jsonify({'success': True, 'name': uname}), 200

if __name__ == '__main__':  
   app.run(host='0.0.0.0', debug=True, port=5001)