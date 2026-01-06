"""MCP Tools for interacting with Show Your App API."""

from pathlib import Path
from typing import Any

import httpx
from claude_code_sdk import tool

from .config import (
    API_BASE,
    AppCreate,
    AppStatus,
    AppUpdate,
    MediaAttach,
    PresignedUrlRequest,
    get_headers,
)


def _make_error(message: str) -> dict[str, Any]:
    """Create an error response."""
    return {
        "content": [{"type": "text", "text": f"Error: {message}"}],
        "isError": True,
    }


def _make_success(data: Any) -> dict[str, Any]:
    """Create a success response."""
    import json
    if isinstance(data, (dict, list)):
        text = json.dumps(data, indent=2)
    else:
        text = str(data)
    return {
        "content": [{"type": "text", "text": text}],
    }


# ============================================================================
# Authentication & User Tools
# ============================================================================

@tool(
    "get_current_user",
    "Get the current authenticated user's info including their ID, username, and email.",
    {},
)
async def get_current_user(args: dict[str, Any]) -> dict[str, Any]:
    """Get current user info from /auth/me endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/auth/me",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


# ============================================================================
# Apps Tools
# ============================================================================

@tool(
    "list_my_apps",
    "List apps created by a specific user. Use this to check for duplicates before creating a new app.",
    {
        "creator_id": int,
        "limit": int,
        "offset": int,
    },
)
async def list_my_apps(args: dict[str, Any]) -> dict[str, Any]:
    """List apps by creator ID."""
    creator_id = args.get("creator_id")
    if not creator_id:
        return _make_error("creator_id is required")
    
    params = {"creator_id": creator_id}
    if "limit" in args:
        params["limit"] = args["limit"]
    if "offset" in args:
        params["offset"] = args["offset"]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/apps/",
                headers=get_headers(),
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


@tool(
    "get_tools",
    "Get all available tools for categorizing apps. Tools represent how the app was built (e.g., 'Cursor', 'Claude Code', 'Replit').",
    {},
)
async def get_tools(args: dict[str, Any]) -> dict[str, Any]:
    """Get available tools from /tools/ endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/tools/",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


@tool(
    "get_tags",
    "Get all available tags for categorizing apps. Tags represent what the app is about (e.g., 'Game', 'Productivity', 'AI-Powered').",
    {},
)
async def get_tags(args: dict[str, Any]) -> dict[str, Any]:
    """Get available tags from /tags/ endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{API_BASE}/tags/",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


@tool(
    "create_app",
    """Create a new app listing on Show Your App.

Required fields: title, prompt_text, prd_text, status
Recommended: tool_ids, tag_ids, app_url (required if status is 'Live')
Optional: youtube_url

Status values: 'Concept', 'WIP', 'Live'
prd_text must be HTML format with tags like <h2>, <p>, <ul>, <li>

tool_ids and tag_ids: Pass as comma-separated integers, e.g., "7,12" or "1,8,15"
""",
    {
        "title": str,
        "prompt_text": str,
        "prd_text": str,
        "status": str,
        "tool_ids": str,
        "tag_ids": str,
        "app_url": str,
        "youtube_url": str,
    },
)
async def create_app(args: dict[str, Any]) -> dict[str, Any]:
    """Create a new app listing."""
    # Validate required fields
    required = ["title", "prompt_text", "prd_text", "status"]
    missing = [f for f in required if not args.get(f)]
    if missing:
        return _make_error(f"Missing required fields: {', '.join(missing)}")
    
    # Validate status
    status_str = args["status"]
    try:
        status = AppStatus(status_str)
    except ValueError:
        return _make_error(f"Invalid status: {status_str}. Must be 'Concept', 'WIP', or 'Live'.")
    
    # Validate app_url for Live status
    if status == AppStatus.LIVE and not args.get("app_url"):
        return _make_error("app_url is required when status is 'Live'")
    
    # Parse tool_ids and tag_ids from comma-separated strings
    tool_ids = []
    if args.get("tool_ids"):
        try:
            tool_ids = [int(x.strip()) for x in str(args["tool_ids"]).split(",") if x.strip()]
        except ValueError:
            return _make_error("tool_ids must be comma-separated integers, e.g., '7,12'")
    
    tag_ids = []
    if args.get("tag_ids"):
        try:
            tag_ids = [int(x.strip()) for x in str(args["tag_ids"]).split(",") if x.strip()]
        except ValueError:
            return _make_error("tag_ids must be comma-separated integers, e.g., '1,8,15'")
    
    # Build request body
    app_data = AppCreate(
        title=args["title"],
        prompt_text=args["prompt_text"],
        prd_text=args["prd_text"],
        status=status,
        is_agent_submitted=True,
        tool_ids=tool_ids,
        tag_ids=tag_ids,
        app_url=args.get("app_url"),
        youtube_url=args.get("youtube_url"),
    )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/apps/",
                headers=get_headers(),
                json=app_data.model_dump(exclude_none=True),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


@tool(
    "update_app",
    """Update an existing app listing. Only provide fields you want to change.

tool_ids and tag_ids: Pass as comma-separated integers, e.g., "7,12" or "1,8,15"
""",
    {
        "app_id": int,
        "title": str,
        "prompt_text": str,
        "prd_text": str,
        "status": str,
        "tool_ids": str,
        "tag_ids": str,
        "app_url": str,
        "youtube_url": str,
    },
)
async def update_app(args: dict[str, Any]) -> dict[str, Any]:
    """Update an existing app listing."""
    app_id = args.get("app_id")
    if not app_id:
        return _make_error("app_id is required")
    
    # Build update data
    update_data: dict[str, Any] = {}
    
    if "title" in args:
        update_data["title"] = args["title"]
    if "prompt_text" in args:
        update_data["prompt_text"] = args["prompt_text"]
    if "prd_text" in args:
        update_data["prd_text"] = args["prd_text"]
    if "status" in args:
        try:
            update_data["status"] = AppStatus(args["status"]).value
        except ValueError:
            return _make_error(f"Invalid status: {args['status']}")
    if "tool_ids" in args and args["tool_ids"]:
        try:
            update_data["tool_ids"] = [int(x.strip()) for x in str(args["tool_ids"]).split(",") if x.strip()]
        except ValueError:
            return _make_error("tool_ids must be comma-separated integers, e.g., '7,12'")
    if "tag_ids" in args and args["tag_ids"]:
        try:
            update_data["tag_ids"] = [int(x.strip()) for x in str(args["tag_ids"]).split(",") if x.strip()]
        except ValueError:
            return _make_error("tag_ids must be comma-separated integers, e.g., '1,8,15'")
    if "app_url" in args:
        update_data["app_url"] = args["app_url"]
    if "youtube_url" in args:
        update_data["youtube_url"] = args["youtube_url"]
    
    if not update_data:
        return _make_error("No fields provided to update")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{API_BASE}/apps/{app_id}",
                headers=get_headers(),
                json=update_data,
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


# ============================================================================
# Media Upload Tools
# ============================================================================

@tool(
    "get_presigned_url",
    "Get a presigned URL for uploading media (screenshots, images) to S3.",
    {
        "filename": str,
        "content_type": str,
    },
)
async def get_presigned_url(args: dict[str, Any]) -> dict[str, Any]:
    """Get a presigned URL for uploading media."""
    filename = args.get("filename")
    content_type = args.get("content_type")
    
    if not filename or not content_type:
        return _make_error("filename and content_type are required")
    
    request_data = PresignedUrlRequest(
        filename=filename,
        content_type=content_type,
    )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/media/presigned-url",
                headers=get_headers(),
                json=request_data.model_dump(),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


@tool(
    "upload_file_to_s3",
    """Upload a file to S3 using a presigned URL.

Use this after get_presigned_url to upload screenshots or images.
The file_path should be an absolute path to the file on disk.""",
    {
        "file_path": str,
        "upload_url": str,
        "content_type": str,
    },
)
async def upload_file_to_s3(args: dict[str, Any]) -> dict[str, Any]:
    """Upload a file to S3 using a presigned URL."""
    file_path = args.get("file_path")
    upload_url = args.get("upload_url")
    content_type = args.get("content_type")
    
    if not file_path or not upload_url or not content_type:
        return _make_error("file_path, upload_url, and content_type are required")
    
    # Read file
    path = Path(file_path)
    if not path.exists():
        return _make_error(f"File not found: {file_path}")
    
    try:
        file_data = path.read_bytes()
    except Exception as e:
        return _make_error(f"Failed to read file: {e}")
    
    # Upload to S3
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                upload_url,
                content=file_data,
                headers={"Content-Type": content_type},
                timeout=120.0,  # Longer timeout for uploads
            )
            response.raise_for_status()
            return _make_success({
                "status": "uploaded",
                "file_path": file_path,
                "size_bytes": len(file_data),
            })
        except httpx.HTTPStatusError as e:
            return _make_error(f"Upload failed - HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Upload request failed: {e}")


@tool(
    "attach_media_to_app",
    """Attach uploaded media to an app listing.

Use this after uploading a file to S3 to link it to your app.
Use the download_url from get_presigned_url response as media_url.""",
    {
        "app_id": int,
        "media_url": str,
    },
)
async def attach_media_to_app(args: dict[str, Any]) -> dict[str, Any]:
    """Attach uploaded media to an app."""
    app_id = args.get("app_id")
    media_url = args.get("media_url")
    
    if not app_id or not media_url:
        return _make_error("app_id and media_url are required")
    
    attach_data = MediaAttach(media_url=media_url)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE}/apps/{app_id}/media",
                headers=get_headers(),
                json=attach_data.model_dump(),
                timeout=30.0,
            )
            response.raise_for_status()
            return _make_success(response.json())
        except httpx.HTTPStatusError as e:
            return _make_error(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return _make_error(f"Request failed: {e}")


# ============================================================================
# Export all tools
# ============================================================================

ALL_TOOLS = [
    get_current_user,
    list_my_apps,
    get_tools,
    get_tags,
    create_app,
    update_app,
    get_presigned_url,
    upload_file_to_s3,
    attach_media_to_app,
]
