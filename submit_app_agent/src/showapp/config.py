"""Configuration and Pydantic models for ShowApp Agent."""

import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# API Configuration
API_BASE = "https://show-your.app/api"
API_KEY = os.getenv("SHOWAPP_API_KEY", "cqHarxuNEEbdSBxhIo3hFGlQnmpgKi6Uu7KSSGPPALA")


def get_headers() -> dict[str, str]:
    """Get default headers for API requests."""
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


# Enums
class AppStatus(str, Enum):
    """App status enum matching backend."""
    CONCEPT = "Concept"
    WIP = "WIP"
    LIVE = "Live"


# Request Models
class AppCreate(BaseModel):
    """Schema for creating a new app."""
    title: str = Field(..., description="App name. Be specific, not generic.")
    prompt_text: str = Field(..., description="1-2 sentence hook that sells the app.")
    prd_text: str = Field(..., description="Full description in HTML format.")
    status: AppStatus = Field(default=AppStatus.CONCEPT, description="Concept | WIP | Live")
    is_agent_submitted: bool = Field(default=True, description="Must be true for agent submissions.")
    tool_ids: list[int] = Field(default_factory=list, description="IDs from /tools/ endpoint.")
    tag_ids: list[int] = Field(default_factory=list, description="IDs from /tags/ endpoint.")
    app_url: Optional[str] = Field(default=None, description="Required if status is Live.")
    youtube_url: Optional[str] = Field(default=None, description="Demo video URL (YouTube only).")
    extra_specs: Optional[dict] = Field(default=None, description="Additional specifications.")


class AppUpdate(BaseModel):
    """Schema for updating an existing app."""
    title: Optional[str] = None
    prompt_text: Optional[str] = None
    prd_text: Optional[str] = None
    status: Optional[AppStatus] = None
    is_agent_submitted: Optional[bool] = None
    tool_ids: Optional[list[int]] = None
    tag_ids: Optional[list[int]] = None
    app_url: Optional[str] = None
    youtube_url: Optional[str] = None
    extra_specs: Optional[dict] = None


class PresignedUrlRequest(BaseModel):
    """Schema for requesting a presigned upload URL."""
    filename: str = Field(..., description="Name of the file to upload.")
    content_type: str = Field(..., description="MIME type (e.g., image/png, image/jpeg).")


class MediaAttach(BaseModel):
    """Schema for attaching media to an app."""
    media_url: str = Field(..., description="The download_url from presigned URL response.")


# Response Models
class User(BaseModel):
    """User response model."""
    id: int
    username: str
    avatar: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    reputation_score: float = 0.0
    is_admin: bool = False
    email: Optional[str] = None
    api_key: Optional[str] = None


class Tool(BaseModel):
    """Tool response model."""
    id: int
    name: str


class Tag(BaseModel):
    """Tag response model."""
    id: int
    name: str


class MediaItem(BaseModel):
    """Media item in app response."""
    id: int
    media_url: str


class AppCreator(BaseModel):
    """Creator info in app response."""
    id: int
    username: str
    avatar: Optional[str] = None


class App(BaseModel):
    """App response model."""
    id: int
    title: Optional[str] = None
    slug: Optional[str] = None
    prompt_text: Optional[str] = None
    prd_text: Optional[str] = None
    status: AppStatus
    app_url: Optional[str] = None
    youtube_url: Optional[str] = None
    is_agent_submitted: bool = False
    is_owner: bool = False
    is_dead: bool = False
    is_liked: bool = False
    likes_count: int = 0
    comments_count: int = 0
    creator_id: int
    creator: Optional[AppCreator] = None
    tools: list[Tool] = []
    tags: list[Tag] = []
    media: list[MediaItem] = []
    parent_app_id: Optional[int] = None
    extra_specs: Optional[dict] = None


class PresignedUrlResponse(BaseModel):
    """Response from presigned URL request."""
    upload_url: str
    download_url: str
    file_key: str
