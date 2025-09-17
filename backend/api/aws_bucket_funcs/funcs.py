import boto3,botocore
from backend.database.config.config import settings

def get_client():
    boto3.setup_default_session() 
    print(settings.AWS_ACCESS_KEY,settings.AWS_SECRET_KEY)
    s3_client = boto3.client('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY,
                             aws_secret_access_key=settings.AWS_SECRET_KEY,
                             region_name=settings.REGION,
                             config=botocore.config.Config(signature_version="s3v4"),)
    return s3_client

def create_s3_bucket(s3_client):
    params = {"Bucket": settings.BUCKET_NAME}
    response = s3_client.create_bucket(**params)

### Server-side
def upload(file_path:str,key:str,s3_client):
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    with open(file_path, "rb") as f:
        f.seek(0)  # make sure
        s3_client.upload_fileobj(
            f, settings.BUCKET_NAME, key,
            ExtraArgs={
                "ContentType": DOCX_MIME,
                "ContentDisposition": f'attachment; filename="{file_path}"'
            }
        )

def download(key:str,s3_client,expires:int=3600):
    response = s3_client.generate_presigned_url(
        'get_object',
        Params = {
            'Bucket': settings.BUCKET_NAME,
            'Key': key
        },
        ExpiresIn = expires
    )
    return response
