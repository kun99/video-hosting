import boto3
import botocore
import tempfile
import os
import subprocess
from dotenv import load_dotenv

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

def convert(data):
    temp_video = None
    temp = None
    try:
        metadata = {
            'title': data['title'],
            'desc': data['desc'],
            'id': data['id'],
            'user': data['user'],
            'time': data['time']
        }
        with tempfile.NamedTemporaryFile(mode='w+b', suffix=".mp4",delete=False) as temp_video:
            try:
                s3.download_file(bucket, data['key'], temp_video.name)
                with tempfile.NamedTemporaryFile(mode='w+b', suffix=".mp4", delete=False) as temp:
                    try:
                        command = [
                            'ffmpeg',
                            '-y',
                            '-i', temp_video.name,
                            '-vf', 'scale=854:480',
                            '-c:a', 'copy',
                            temp.name
                        ]
                        subprocess.run(command, check=True)
                    except Exception as e:
                        print('error processing: ', e)
                    s3.upload_file(temp.name, bucket, "videos/"+data['user']+"/"+data['title'], ExtraArgs={'ACL': 'public-read', 'ContentType':'video/mp4', 'Metadata': metadata})
                    print("success")
            except Exception as e:
                print("error: ", e)
                return e
    except Exception as e:
        return e
    finally:
        if temp_video:
            os.remove(temp_video.name)
        if temp:
            os.remove(temp.name)