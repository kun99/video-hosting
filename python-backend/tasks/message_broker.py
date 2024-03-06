from tasks.thumbnail import extract_thumbnail
from tasks.converter import convert
from tasks.chunker import chunker
import boto3
import botocore
from redis import Redis
from rq import Queue
import os
from dotenv import load_dotenv

redis_conn = Redis(host='redis-service', port=6379, db=0)
firstQueue = Queue('q', connection=redis_conn)

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

def enqueue_video_tasks(key, user, title, desc, id, time):
    input = {'key': key, 'user': user, 'title': title, 'desc': desc, 'id': id, 'time': time}
    firstQueue.enqueue(extract_thumbnail, input)
    firstQueue.enqueue(convert, input)
    firstQueue.enqueue(chunker, input)