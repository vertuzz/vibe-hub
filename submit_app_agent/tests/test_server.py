"""Tests for ShowApp server module."""

import pytest

from showapp.server import (
    bootstrap,
    create_showapp_server,
    format_context_for_prompt,
    get_allowed_tools,
    get_combined_mcp_servers,
    get_playwright_server_config,
)


class TestServerSetup:
    def test_create_showapp_server(self):
        """Test creating the ShowApp MCP server."""
        server = create_showapp_server()
        assert server is not None

    def test_get_playwright_server_config(self):
        """Test Playwright server configuration."""
        config = get_playwright_server_config()
        assert config["type"] == "stdio"
        assert config["command"] == "npx"
        assert "@playwright/mcp@latest" in config["args"]

    def test_get_combined_mcp_servers(self):
        """Test combined MCP servers configuration."""
        servers = get_combined_mcp_servers()
        assert "showapp" in servers
        assert "playwright" in servers

    def test_get_allowed_tools(self):
        """Test allowed tools list."""
        tools = get_allowed_tools()
        
        # Check ShowApp tools
        assert "mcp__showapp__get_current_user" in tools
        assert "mcp__showapp__create_app" in tools
        assert "mcp__showapp__upload_file_to_s3" in tools
        
        # Check Playwright tools
        assert "mcp__playwright__browser_navigate" in tools
        assert "mcp__playwright__browser_take_screenshot" in tools
        assert "mcp__playwright__browser_snapshot" in tools


class TestFormatContextForPrompt:
    def test_format_empty_context(self):
        """Test formatting empty context."""
        context = {"user": None, "tools": [], "tags": [], "user_apps": []}
        result = format_context_for_prompt(context)
        assert result == ""

    def test_format_with_user(self):
        """Test formatting context with user."""
        context = {
            "user": {"id": 1, "username": "testuser"},
            "tools": [],
            "tags": [],
            "user_apps": [],
        }
        result = format_context_for_prompt(context)
        assert "User ID: 1" in result
        assert "Username: testuser" in result

    def test_format_with_tools(self):
        """Test formatting context with tools."""
        context = {
            "user": None,
            "tools": [
                {"id": 1, "name": "Cursor"},
                {"id": 7, "name": "Claude Code"},
            ],
            "tags": [],
            "user_apps": [],
        }
        result = format_context_for_prompt(context)
        assert "Available Tools" in result
        assert "ID 1: Cursor" in result
        assert "ID 7: Claude Code" in result

    def test_format_with_tags(self):
        """Test formatting context with tags."""
        context = {
            "user": None,
            "tools": [],
            "tags": [
                {"id": 1, "name": "Game"},
                {"id": 8, "name": "Web App"},
            ],
            "user_apps": [],
        }
        result = format_context_for_prompt(context)
        assert "Available Tags" in result
        assert "ID 1: Game" in result
        assert "ID 8: Web App" in result

    def test_format_with_user_apps(self):
        """Test formatting context with user apps."""
        context = {
            "user": {"id": 1, "username": "testuser"},
            "tools": [],
            "tags": [],
            "user_apps": [
                {"id": 123, "title": "My App", "status": "Live"},
            ],
        }
        result = format_context_for_prompt(context)
        assert "Existing Apps" in result
        assert "ID 123: My App" in result

    def test_format_full_context(self):
        """Test formatting full context."""
        context = {
            "user": {"id": 1, "username": "testuser"},
            "tools": [{"id": 7, "name": "Claude Code"}],
            "tags": [{"id": 1, "name": "Game"}],
            "user_apps": [{"id": 123, "title": "Test App", "status": "WIP"}],
        }
        result = format_context_for_prompt(context)
        
        assert "User ID: 1" in result
        assert "Claude Code" in result
        assert "Game" in result
        assert "Test App" in result
