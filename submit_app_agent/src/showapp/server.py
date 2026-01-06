"""MCP Server setup for Show Your App agent with Playwright integration."""

import json
from typing import Any

import httpx
from claude_code_sdk import create_sdk_mcp_server

from .config import API_BASE, get_headers
from .tools import ALL_TOOLS


def create_showapp_server():
    """Create the ShowApp MCP server with all tools."""
    return create_sdk_mcp_server(
        name="showapp",
        version="0.1.0",
        tools=ALL_TOOLS,
    )


def get_playwright_server_config() -> dict[str, Any]:
    """Get the Playwright MCP server configuration (external subprocess)."""
    return {
        "type": "stdio",
        "command": "npx",
        "args": ["@playwright/mcp@latest"],
        "env": {},
    }


def get_combined_mcp_servers() -> dict[str, Any]:
    """Get combined MCP servers configuration (ShowApp + Playwright)."""
    return {
        "showapp": create_showapp_server(),
        "playwright": get_playwright_server_config(),
    }


def get_allowed_tools() -> list[str]:
    """Get list of all allowed tool names for Claude."""
    # ShowApp tools
    showapp_tools = [
        "mcp__showapp__get_current_user",
        "mcp__showapp__list_my_apps",
        "mcp__showapp__get_tools",
        "mcp__showapp__get_tags",
        "mcp__showapp__create_app",
        "mcp__showapp__update_app",
        "mcp__showapp__get_presigned_url",
        "mcp__showapp__upload_file_to_s3",
        "mcp__showapp__attach_media_to_app",
    ]
    
    # Playwright MCP tools for browser automation
    # See: https://github.com/microsoft/playwright-mcp
    playwright_tools = [
        "mcp__playwright__browser_navigate",
        "mcp__playwright__browser_navigate_back",
        "mcp__playwright__browser_navigate_forward",
        "mcp__playwright__browser_snapshot",
        "mcp__playwright__browser_click",
        "mcp__playwright__browser_type",
        "mcp__playwright__browser_hover",
        "mcp__playwright__browser_drag",
        "mcp__playwright__browser_select_option",
        "mcp__playwright__browser_take_screenshot",
        "mcp__playwright__browser_press_key",
        "mcp__playwright__browser_scroll_down",
        "mcp__playwright__browser_scroll_up",
        "mcp__playwright__browser_tab_list",
        "mcp__playwright__browser_tab_new",
        "mcp__playwright__browser_tab_select",
        "mcp__playwright__browser_tab_close",
        "mcp__playwright__browser_file_upload",
        "mcp__playwright__browser_close",
        "mcp__playwright__browser_network_requests",
        "mcp__playwright__browser_pdf_save",
    ]
    
    return showapp_tools + playwright_tools


async def bootstrap() -> dict[str, Any]:
    """Pre-fetch user info, tools, and tags to provide context to the agent.
    
    Returns:
        Dictionary with 'user', 'tools', and 'tags' data.
    """
    context = {
        "user": None,
        "tools": [],
        "tags": [],
        "user_apps": [],
    }
    
    async with httpx.AsyncClient() as client:
        # Fetch current user
        try:
            response = await client.get(
                f"{API_BASE}/auth/me",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            context["user"] = response.json()
        except Exception as e:
            print(f"Warning: Failed to fetch user info: {e}")
        
        # Fetch tools
        try:
            response = await client.get(
                f"{API_BASE}/tools/",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            context["tools"] = response.json()
        except Exception as e:
            print(f"Warning: Failed to fetch tools: {e}")
        
        # Fetch tags
        try:
            response = await client.get(
                f"{API_BASE}/tags/",
                headers=get_headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            context["tags"] = response.json()
        except Exception as e:
            print(f"Warning: Failed to fetch tags: {e}")
        
        # Fetch user's existing apps (for duplicate detection)
        if context["user"]:
            try:
                response = await client.get(
                    f"{API_BASE}/apps/",
                    headers=get_headers(),
                    params={"creator_id": context["user"]["id"], "limit": 100},
                    timeout=30.0,
                )
                response.raise_for_status()
                context["user_apps"] = response.json()
            except Exception as e:
                print(f"Warning: Failed to fetch user apps: {e}")
    
    return context


def format_context_for_prompt(context: dict[str, Any]) -> str:
    """Format the bootstrap context into a prompt-friendly string."""
    lines = []
    
    # User info
    if context.get("user"):
        user = context["user"]
        lines.append("## Your User Info")
        lines.append(f"- User ID: {user['id']}")
        lines.append(f"- Username: {user['username']}")
        lines.append("")
    
    # Available tools
    if context.get("tools"):
        lines.append("## Available Tools (How It Was Built)")
        lines.append("Use these tool_ids when creating/updating apps:")
        for tool in context["tools"]:
            lines.append(f"- ID {tool['id']}: {tool['name']}")
        lines.append("")
    
    # Available tags
    if context.get("tags"):
        lines.append("## Available Tags (What It's About)")
        lines.append("Use these tag_ids when creating/updating apps:")
        for tag in context["tags"]:
            lines.append(f"- ID {tag['id']}: {tag['name']}")
        lines.append("")
    
    # User's existing apps
    if context.get("user_apps"):
        lines.append("## Your Existing Apps (Check for Duplicates)")
        for app in context["user_apps"]:
            lines.append(f"- ID {app['id']}: {app.get('title', 'Untitled')} ({app.get('status', 'Unknown')})")
        lines.append("")
    
    return "\n".join(lines)
