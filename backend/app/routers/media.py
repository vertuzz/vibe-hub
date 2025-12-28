from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.routers.auth import get_current_user
from app.models import User
from app.schemas.schemas import MediaResponse
import uuid

router = APIRouter()

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

@router.post("/upload", response_model=MediaResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    s3_client = Depends(get_s3_client)
):
    if not settings.S3_BUCKET or not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        raise HTTPException(
            status_code=500,
            detail="S3 is not configured"
        )
    
    try:
        # Generate a unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_key = f"users/{current_user.id}/{uuid.uuid4()}.{file_extension}"
        
        # Upload the file to S3
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            file_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        
        # Construct the URL
        url = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        
        return {
            "url": url,
            "public_id": file_key
        }
    except ClientError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not upload file to S3: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not upload file: {str(e)}"
        )
