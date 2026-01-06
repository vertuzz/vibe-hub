"""Tests for ShowApp agent tools."""

import json
import pytest
import respx
from httpx import Response

from showapp.config import API_BASE


@pytest.fixture
def mock_api():
    """Mock the ShowApp API."""
    with respx.mock(base_url=API_BASE) as api:
        yield api


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful user fetch."""
        from showapp.tools import get_current_user
        
        mock_api.get("/auth/me").mock(return_value=Response(200, json={
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
        }))
        
        result = await get_current_user.handler({})
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert content["id"] == 1
        assert content["username"] == "testuser"


class TestListMyApps:
    @pytest.mark.asyncio
    async def test_missing_creator_id(self, mock_api):
        """Test error when creator_id is missing."""
        from showapp.tools import list_my_apps
        
        result = await list_my_apps.handler({})
        
        assert result.get("isError") is True
        assert "creator_id is required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful apps list fetch."""
        from showapp.tools import list_my_apps
        
        mock_api.get("/apps/").mock(return_value=Response(200, json=[
            {"id": 1, "title": "Test App", "status": "Live"},
        ]))
        
        result = await list_my_apps.handler({"creator_id": 1})
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert len(content) == 1
        assert content[0]["title"] == "Test App"


class TestGetTools:
    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful tools fetch."""
        from showapp.tools import get_tools
        
        mock_api.get("/tools/").mock(return_value=Response(200, json=[
            {"id": 1, "name": "Cursor"},
            {"id": 7, "name": "Claude Code"},
        ]))
        
        result = await get_tools.handler({})
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert len(content) == 2


class TestGetTags:
    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful tags fetch."""
        from showapp.tools import get_tags
        
        mock_api.get("/tags/").mock(return_value=Response(200, json=[
            {"id": 1, "name": "Game"},
            {"id": 8, "name": "Web App"},
        ]))
        
        result = await get_tags.handler({})
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert len(content) == 2


class TestCreateApp:
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, mock_api):
        """Test error when required fields are missing."""
        from showapp.tools import create_app
        
        result = await create_app.handler({})
        
        assert result.get("isError") is True
        assert "Missing required fields" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_invalid_status(self, mock_api):
        """Test error with invalid status."""
        from showapp.tools import create_app
        
        result = await create_app.handler({
            "title": "Test",
            "prompt_text": "Hook",
            "prd_text": "<p>Test</p>",
            "status": "Invalid",
        })
        
        assert result.get("isError") is True
        assert "Invalid status" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_live_status_requires_app_url(self, mock_api):
        """Test error when Live status without app_url."""
        from showapp.tools import create_app
        
        result = await create_app.handler({
            "title": "Test",
            "prompt_text": "Hook",
            "prd_text": "<p>Test</p>",
            "status": "Live",
        })
        
        assert result.get("isError") is True
        assert "app_url is required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful app creation."""
        from showapp.tools import create_app
        
        mock_api.post("/apps/").mock(return_value=Response(201, json={
            "id": 123,
            "title": "Test App",
            "status": "Live",
        }))
        
        result = await create_app.handler({
            "title": "Test App",
            "prompt_text": "A test app hook",
            "prd_text": "<h2>Test</h2><p>Description</p>",
            "status": "Live",
            "app_url": "https://test.app",
            "tool_ids": "7",
            "tag_ids": "1,8",
        })
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert content["id"] == 123


class TestUpdateApp:
    @pytest.mark.asyncio
    async def test_missing_app_id(self, mock_api):
        """Test error when app_id is missing."""
        from showapp.tools import update_app
        
        result = await update_app.handler({})
        
        assert result.get("isError") is True
        assert "app_id is required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_no_fields_to_update(self, mock_api):
        """Test error when no fields provided."""
        from showapp.tools import update_app
        
        result = await update_app.handler({"app_id": 1})
        
        assert result.get("isError") is True
        assert "No fields provided" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful app update."""
        from showapp.tools import update_app
        
        mock_api.patch("/apps/123").mock(return_value=Response(200, json={
            "id": 123,
            "title": "Updated Title",
        }))
        
        result = await update_app.handler({
            "app_id": 123,
            "title": "Updated Title",
        })
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert content["title"] == "Updated Title"


class TestGetPresignedUrl:
    @pytest.mark.asyncio
    async def test_missing_params(self, mock_api):
        """Test error when params are missing."""
        from showapp.tools import get_presigned_url
        
        result = await get_presigned_url.handler({})
        
        assert result.get("isError") is True
        assert "required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful presigned URL fetch."""
        from showapp.tools import get_presigned_url
        
        mock_api.post("/media/presigned-url").mock(return_value=Response(200, json={
            "upload_url": "https://s3.example.com/upload",
            "download_url": "https://cdn.example.com/image.png",
            "file_key": "images/abc123.png",
        }))
        
        result = await get_presigned_url.handler({
            "filename": "screenshot.png",
            "content_type": "image/png",
        })
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert "upload_url" in content
        assert "download_url" in content


class TestUploadFileToS3:
    @pytest.mark.asyncio
    async def test_missing_params(self, mock_api):
        """Test error when params are missing."""
        from showapp.tools import upload_file_to_s3
        
        result = await upload_file_to_s3.handler({})
        
        assert result.get("isError") is True
        assert "required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_file_not_found(self, mock_api):
        """Test error when file doesn't exist."""
        from showapp.tools import upload_file_to_s3
        
        result = await upload_file_to_s3.handler({
            "file_path": "/nonexistent/path/file.png",
            "upload_url": "https://s3.example.com/upload",
            "content_type": "image/png",
        })
        
        assert result.get("isError") is True
        assert "File not found" in result["content"][0]["text"]


class TestAttachMediaToApp:
    @pytest.mark.asyncio
    async def test_missing_params(self, mock_api):
        """Test error when params are missing."""
        from showapp.tools import attach_media_to_app
        
        result = await attach_media_to_app.handler({})
        
        assert result.get("isError") is True
        assert "required" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_success(self, mock_api):
        """Test successful media attach."""
        from showapp.tools import attach_media_to_app
        
        mock_api.post("/apps/123/media").mock(return_value=Response(201, json={
            "id": 456,
            "media_url": "https://cdn.example.com/image.png",
        }))
        
        result = await attach_media_to_app.handler({
            "app_id": 123,
            "media_url": "https://cdn.example.com/image.png",
        })
        
        assert "isError" not in result
        content = json.loads(result["content"][0]["text"])
        assert content["id"] == 456
