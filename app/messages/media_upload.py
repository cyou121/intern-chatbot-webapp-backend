import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings
from fastapi import HTTPException, UploadFile
import uuid

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.YOUR_ACCESS_KEY,
    aws_secret_access_key=settings.YOUR_SECRET_KEY,
    region_name='ap-northeast-1'
)

BUCKET_NAME = 'mutimodel-intern'

async def upload_to_s3(file: UploadFile):
    try:
        file_contents = await file.read()
                
        file_key = f"{uuid.uuid4().hex}{file.filename}"

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=file_contents,
            ContentType=file.content_type,
            ACL='private'
        )

        return file_key
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"画像のアップロードに失敗しました: {str(e)}")
    
def generate_presigned_url(file_key, expiration=900):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_key},
            ExpiresIn=expiration 
        )
        return url
    except NoCredentialsError:
        print("No AWS credentials found.")
        return None
    