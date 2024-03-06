from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_bcrypt import Bcrypt
import boto3
import botocore
from datetime import datetime
import hashlib
import message_broker
import re
import tempfile
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173")

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqldb://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}/{os.environ['MYSQL_DB']}?unix_socket=/run/mysqld/mysqld.sock"

db = SQLAlchemy(app)
bcrypt = Bcrypt()
uname = ""
video_title = ""
video_i = ""
video_id = 0

load_dotenv()
access_key = os.getenv("ACCESS_KEY")
secret = os.getenv("SECRET")
endpoint = os.getenv("ENDPOINT")
bucket = os.getenv("BUCKET")
session = boto3.session.Session()

s3 = session.client('s3',
                        config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
                        region_name='sgp1',
                        endpoint_url=endpoint,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret)

#generating presigned url to save video to
@app.route('/api/get_presigned_url', methods=['POST'])  
def get_presigned_url():
    try:
        #metadata values for identification and additional info
        uname = request.form['user']
        gen_id = hashlib.sha256((uname+request.form['title']).encode()).hexdigest()
        upload_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        key = "videos/"+uname+"/"+request.form['title']
        #presigned url where frontend can use to upload video to
        presigned_url = s3.generate_presigned_url(ClientMethod='put_object', Params={'Bucket': bucket,'Key': key}, ExpiresIn=900)
        user = User.query.filter_by(username=uname).first()
        video = Video(id=gen_id, user_id=user.id, title=request.form['title'])
        db.session.add(video)
        db.session.commit()
        return jsonify({'url': presigned_url, 'id': gen_id, 'datetime': upload_datetime})
    except Exception as e:
        return jsonify({'error': e}), 500

#redis queue
@app.route('/api/tasks', methods=['POST'])
def enqueue_tasks():
    data = request.get_json()
    key = data.get('key')
    user = data.get('user')
    message_broker.enqueue_video_tasks(key, user, data.get("title"), data.get("desc"), data.get("id"), data.get("time"))
    return 'Enqueued tasks.'

#delete video+thumbnail
@app.route('/api/delete', methods=['DELETE'])
def delete():
    try:
        data = request.get_json()
        username = data['username']
        title = data['title']
        id = data['id']
        #deleting video
        response = s3.list_objects_v2(Bucket=bucket, Prefix="videos/"+username+'/')
        #list all videos for a user and delete video with matching title and id from request
        for obj in response.get('Contents', []):
            obj_metadata = s3.head_object(Bucket=bucket, Key=obj['Key'])['Metadata']
            if obj_metadata['title'] == title and obj_metadata['id'] == id:
                s3.delete_object(Bucket=bucket, Key=obj['Key'])
        #deleting thumbnail
        response_thumbnails = s3.list_objects_v2(Bucket=bucket, Prefix="thumbnail/"+username+'/')
        #list all thumbnails for a user and delete thumbnail with matching title and id from request
        for obj in response_thumbnails.get('Contents', []):
            obj_metadata = s3.head_object(Bucket=bucket, Key=obj['Key'])['Metadata']
            if obj_metadata['title'] == title and obj_metadata['id'] == id:
                s3.delete_object(Bucket=bucket, Key=obj['Key'])
                break
        try:
            #deleting cached video
            response_thumbnails = s3.list_objects_v2(Bucket=bucket, Prefix="cached/"+username+'/')
            #list all cached video for a user and delete cached video with matching title and id from request
            for obj in response_thumbnails.get('Contents', []):
                obj_metadata = s3.head_object(Bucket=bucket, Key=obj['Key'])['Metadata']
                if obj_metadata['title'] == title and obj_metadata['id'] == id:
                    s3.delete_object(Bucket=bucket, Key=obj['Key'])
                    break
        except Exception as e:
            print("wasnt cached")
        return jsonify({'message': "Succesfully deleted " + title})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error deleting'}), 500

#returns videos that frontend can store in a list to request for videos to view
@app.route('/api/videos', methods=['GET'])
def videos():
    try:
        #listing and retrieving all m3u8 files
        response = s3.list_objects(Bucket=bucket, Prefix="videos/")
        others = []
        for obj in response.get('Contents', []):
            if obj['Key'].endswith(".m3u8"):
                others.append(obj['Key'])
        #generating urls for each m3u8 file and getting their metadata
        videos = []
        for key in others:
            video = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key})
            response = s3.head_object(Bucket=bucket, Key= key)
            metadata = response['Metadata']
            videos.append([{
                'file': video,
                'metadata': {
                    'title': metadata['title'],
                    'desc': metadata['desc'],
                    'user': metadata['user'],
                    'time': metadata['time'],
                    'id': metadata['id']
                }
            }])
        return jsonify({'videos': videos})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error fetching videos'}), 500

#for video playback
@app.route('/api/hls', methods=['POST'])
def video_chunks():
    try:
        data = request.get_json()
        #get id of owner with video id
        #get username of owner with owner id
        owner = Vls.query.get(data['id'])
        user = User.query.filter_by(id=owner.user_id).first()
        m3u8_key = 'videos/'+user.username+'/'+data['title']+'.m3u8'
        cached_key = 'cached/'+user.username+'/'+data['title']+'.m3u8'
        print("username is " + user.username)
        try:
            response = s3.head_object(Bucket=bucket, Key=cached_key)
            url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': cached_key})
            #checking if cached file has expired
            expires_date = datetime.datetime.strptime(response.get('Expires'), "%a, %d %b %Y %H:%M:%S %Z")
            current_date = datetime.datetime.now(datetime.timezone.utc)
            #if cached file has expired delete and cache new
            if expires_date < current_date:
                s3.delete_object(Bucket=bucket, Key=cached_key)
                return cache_new(data, user.username, m3u8_key, cached_key)
            else:
                metadata = response['Metadata']
                return jsonify({'m3u8': url,'metadata': metadata})
        except Exception as e:
            #if file isnt cached, cache it
            return cache_new(data, user.username, m3u8_key, cached_key)       
    except Exception as e:
        print(str(e))  
        return jsonify({'f': e}), 404
    
def cache_new(data, username, m3u8_key, cached_key):
    #create temp file to that acts as a notepad
    temp_m3u8 = tempfile.NamedTemporaryFile(suffix=".m3u8", delete=True)
    try:
        s3.download_file(bucket, m3u8_key, temp_m3u8.name)
        regex = r'[a-zA-Z0-9_-]+\.ts'
        #get all rows in m3u8 file
        with open(temp_m3u8.name, 'r') as f:
            rows = f.readlines()
        #for every .ts file generate a presigned url for it and replace the row
        i=0
        with open(temp_m3u8.name, 'w') as f:
            for row in rows:
                if re.search(regex, row):
                    ts_url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': 'videos/'+username+'/'+data['title']+'_'+str(i)+'.ts'})
                    changed_ts = re.sub(regex, ts_url, row)
                    f.write(changed_ts)
                    i+=1
                else:
                    f.write(row)
        #to store contents of the temp file in s3
        with open(temp_m3u8.name, 'r') as f:
            m3u8_content = f.read()
        response = s3.head_object(Bucket=bucket, Key= m3u8_key)
        metadata = response['Metadata']
        #caching it for 10 minutes
        s3.put_object(Body=m3u8_content, Bucket=bucket, Key=cached_key, Metadata= metadata, Expires=600)
        url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': cached_key})
        return jsonify({'m3u8': url,'metadata': metadata})
    except Exception as e:
        print(str(e))
        return jsonify({'f': str(e)}), 500
    finally:
        temp_m3u8.close()

#for listing all the videos available to watch (home page)
@app.route('/api/thumbnails', methods=['GET'])
def thumbnails():
    try:
        response = s3.list_objects(Bucket="ss-p2", Prefix="thumbnail/")
        thumbnails = []
        #generating urls for the thumbnails and getting their metadata
        for obj in response.get('Contents', []):
            thumbnail = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj['Key']})
            response = s3.head_object(Bucket=bucket, Key= obj['Key'])
            metadata = response['Metadata']
            thumbnails.append([{
                'file': thumbnail,
                'metadata': {
                    'title': metadata['title'],
                    'desc': metadata['desc'],
                    'user': metadata['user'],
                    'time': metadata['time'],
                    'id': metadata['id']
                }
            }])
        return jsonify({'thumbnails': thumbnails})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error fetching thuumbnails'}), 500
    
@app.route('/api/my_thumbnails', methods=['POST'])
def user_thumbnails():
    data = request.get_json()
    try:
        response = s3.list_objects(Bucket="ss-p2", Prefix="thumbnail/"+data['username']+'/')
        thumbnails = []
        for obj in response.get('Contents', []):
            thumbnail = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj['Key']})
            response = s3.head_object(Bucket=bucket, Key= obj['Key'])
            metadata = response['Metadata']
            thumbnails.append([{
                'file': thumbnail,
                'metadata': {
                    'title': metadata['title'],
                    'desc': metadata['desc'],
                    'user': metadata['user'],
                    'time': metadata['time'],
                    'id': metadata['id']
                }
            }])
        return jsonify({'thumbnails': thumbnails})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error fetching thumbnails'}), 500 

@app.route('/api/set_videod', methods=['POST'])
def set_video_data():
    try:
        data = request.get_json()
        global video_title, video_i, video_id
        video_i = data['i']
        video_id = data['id']
        video = Video.query.filter_by(id=video_id).first()
        return jsonify({'user': uname, 'id': video_id, 'title': video.title, 'i': video_i})
    except Exception as e:
        print(e)
        return jsonify({'message': 'Error setting details'}), 500

@app.route('/api/videod', methods=['GET'])
def video_data():
    video = Video.query.filter_by(id=video_id).first()
    return jsonify({'user': uname, 'id': video_id, 'title': video.title, 'i': video_i})

#db/websocket stuff
    
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Tokens(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)

class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.String(255), primary_key=True, nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)

class Vls(db.Model):
    __tablename__ = 'vls'
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    username = data['username']
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Registration successful'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        new_access = Tokens(username=username, token=access_token)
        #remove entry if there is already one associated with user
        user_authenticated = Tokens.query.filter_by(username=username).first()
        if user_authenticated:
            db.session.delete(user_authenticated)
            db.session.commit()
        db.session.add(new_access)
        db.session.commit()
        global uname
        uname = username
        return jsonify({'success': True, 'message': 'Login successful', 'token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    global uname
    uname = ""
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@app.route('/api/get_user_using_token', methods=['POST'])
def get_user_using_token():
    data = request.get_json()
    if 'token' not in data:
        return jsonify({'error': 'Need token'}), 400
    token = data['token']
    access = Tokens.query.filter_by(token=token).first()
    return jsonify({'success': True, 'message': 'Username retrieved', 'username': access.username}), 200

@app.route('/api/get_token', methods=['POST'])
def get_token():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'No access'}), 400
    username = data['username']
    access = Tokens.query.filter_by(username=username).first()
    return jsonify({'success': True, 'message': 'Token retrieved', 'token': access.token}), 200

@app.route('/api/fetch_username', methods=['GET'])
def fetch_username():
    return jsonify({'success': True, 'name': uname}), 200

@app.route('/api/views/<video_id>', methods=['GET'])
def get_vls(video_id):
    video = Vls.query.get(video_id)
    if video:
        return jsonify({'views': video.views, 'likes': video.likes}), 200
    else:
        return jsonify({'error': 'Video not found'}), 404

@app.route('/api/initialize', methods=['POST'])
def create_video():
    data = request.get_json()
    video_id = data.get('video_id')
    if video_id:
        user = User.query.filter_by(username=uname).first()
        new_video = Vls(id=video_id, user_id=user.id)
        db.session.add(new_video)
        db.session.commit()
        print("created "+video_id)
        return jsonify({'message': 'Video created successfully'}), 201
    else:
        return jsonify({'error': 'Invalid video ID'}), 400

@app.route('/api/remove_views/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Vls.query.get(video_id)
    if video:
        db.session.delete(video)
        db.session.commit()
        return jsonify({'message': 'Video deleted successfully'}), 200
    else:
        return jsonify({'error': 'Video not found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)