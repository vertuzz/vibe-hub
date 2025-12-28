import pytest
from io import BytesIO
from app.core.config import settings
from moto import mock_aws
import boto3
import os

@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="vibehub")
        yield s3

@pytest.mark.asyncio
async def test_upload_image_success(client, auth_headers, s3_setup):
    # Mock settings for test
    settings.S3_BUCKET = "vibehub"
    settings.AWS_ACCESS_KEY_ID = "testing"
    settings.AWS_SECRET_ACCESS_KEY = "testing"
    settings.AWS_REGION = "us-east-1"

    file_content = b"fake image content"
    file = BytesIO(file_content)
    
    response = await client.post(
        "/media/upload",
        headers=auth_headers,
        files={"file": ("test.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "public_id" in data
    assert "vibehub.s3.us-east-1.amazonaws.com" in data["url"]
    assert data["public_id"].startswith("users/")

@pytest.mark.asyncio
async def test_upload_image_unauthorized(client):
    # Test upload without auth headers
    file_content = b"fake image content"
    file = BytesIO(file_content)
    
    response = await client.post(
        "/media/upload",
        files={"file": ("test.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_upload_image_s3_not_configured(client, auth_headers):
    # Temporarily unset settings
    old_bucket = settings.S3_BUCKET
    settings.S3_BUCKET = None
    
    try:
        file_content = b"fake image content"
        file = BytesIO(file_content)
        
        response = await client.post(
            "/media/upload",
            headers=auth_headers,
            files={"file": ("test.jpg", file, "image/jpeg")}
        )
        
        assert response.status_code == 500
        assert "S3 is not configured" in response.json()["detail"]
    finally:
        settings.S3_BUCKET = old_bucket

@pytest.mark.asyncio
async def test_upload_image_s3_error(client, auth_headers, s3_setup):
    # Test S3 error (e.g. bucket doesn't exist)
    settings.S3_BUCKET = "non-existent-bucket"
    
    file_content = b"fake image content"
    file = BytesIO(file_content)
    
    response = await client.post(
        "/media/upload",
        headers=auth_headers,
        files={"file": ("test.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == 400
    assert "Could not upload file to S3" in response.json()["detail"]
