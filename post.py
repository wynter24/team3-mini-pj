import boto3, os, certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# 환경변수 설정
load_dotenv()
MONGO_USER = os.environ.get('MONGO_USER')
MONGO_PASS = os.environ.get('MONGO_PASS')
SECRET_KEY = os.environ.get('SECRET_KEY')

# 몽고DB 연결
ca = certifi.where()
client = MongoClient(f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.ebm0gtg.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.miniproject


load_dotenv()
def s3_connection():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECERT_ACCESS_KEY"),
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!") 
        return s3
        
s3 = s3_connection()

# s3에 파일 업로드
# try:
#     # (로컬에서 올릴 이미지, 버킷이름, 버킷에 저장될 파일 이름)
#     s3.upload_file("./img/분홍토끼.png","group3artistimage","분홍토끼")
# except Exception as e:
#     print(e)

@app.route('/', methods = ['GET'])
def get_main_page():
    return render_template('createPost.html')

# 이미지파일 S3에 저장 / 노래 제목, 가수, 이미지 url, 작성자는 db에 저장
@app.route("/upload", methods=["POST"])
def api_write():
    # print(request.files['image_give'])
    # html에서 가져온 정보
    file = request.files['image_give']
    title_receive = request.files['song_title_give']
    artist_receive = request.files['artist_give']
    # 현재 로그인 사용자 정보
    # writer =get_user()

    # S3에서 가져온 이미지url
    location = s3.get_bucket_location(Bucket='group3artistimage')['LocationConstraint']
    image_url = f'https://group3artistimage.s3.ap-northeast-2.amazonaws.com/'


    # mongodb에 저장
    doc = {
        'user': '',
        'song_title': title_receive,
        'artist': artist_receive,
        'img_url': ''
    }
    db.posts.insert_one(doc)

    # S3에 저장할 파일 이름 지정
    filename = file.filename.split('.')[0]
    ext = file.filename.split('.'[-1])
    img_name = datetime.now().strftime(f"{filename}-%Y-%m-%d-%H-%S.{ext}")

    # S3 버킷에 업로드
    success = s3_put_object(s3,'group3artistimage',file,img_name)
    
    if success:
        return jsonify({'msg': '저장 완료!'})
    else:
        return jsonify({'msg': '저장 실패!'}), 500

def s3_put_object(s3, bucket, file, filename):
    try:
        s3.put_object(
            Body=file, #업로드할 파일 객체
            Bucket=bucket,
            Key=f'images/{filename}', #S3에 업로드할 파일 경로
            ContentType=file.content_type, #image/jpeg ?
            ACL='public-read'
        )
        return True
    
    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':
    app.run('0.0.0.0', port=5002, debug=True)