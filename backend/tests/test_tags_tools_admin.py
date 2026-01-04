import pytest
from httpx import AsyncClient


# =============================================================================
# TAG CRUD TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_get_tags_public(client: AsyncClient):
    """Test that anyone can get tags list (no auth required)."""
    response = await client.get("/tags/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_tags_with_counts(client: AsyncClient):
    """Test getting tags with app counts."""
    response = await client.get("/tags/with-counts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Each tag should have app_count field
    if len(data) > 0:
        assert "app_count" in data[0]
        assert "name" in data[0]
        assert "id" in data[0]


@pytest.mark.asyncio
async def test_create_tag_requires_admin(client: AsyncClient, auth_headers: dict):
    """Test that non-admin cannot create tags."""
    response = await client.post("/tags/", json={"name": "TestTag"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_create_tag(client: AsyncClient, admin_headers: dict):
    """Test that admin can create tags."""
    response = await client.post("/tags/", json={"name": "AdminCreatedTag"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AdminCreatedTag"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_tag_fails(client: AsyncClient, admin_headers: dict):
    """Test that creating a duplicate tag name fails with 400."""
    # Create first tag
    await client.post("/tags/", json={"name": "DuplicateTag"}, headers=admin_headers)
    
    # Try to create duplicate
    response = await client.post("/tags/", json={"name": "DuplicateTag"}, headers=admin_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_tag_requires_admin(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Test that non-admin cannot update tags."""
    # Create a tag first
    create_resp = await client.post("/tags/", json={"name": "TagToUpdate"}, headers=admin_headers)
    tag_id = create_resp.json()["id"]
    
    # Try to update as non-admin
    response = await client.put(f"/tags/{tag_id}", json={"name": "UpdatedTag"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_update_tag(client: AsyncClient, admin_headers: dict):
    """Test that admin can update tags."""
    # Create a tag
    create_resp = await client.post("/tags/", json={"name": "TagForUpdate"}, headers=admin_headers)
    tag_id = create_resp.json()["id"]
    
    # Update the tag
    response = await client.put(f"/tags/{tag_id}", json={"name": "UpdatedTagName"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedTagName"


@pytest.mark.asyncio
async def test_update_tag_not_found(client: AsyncClient, admin_headers: dict):
    """Test updating non-existent tag returns 404."""
    response = await client.put("/tags/99999", json={"name": "NoTag"}, headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Tag not found"


@pytest.mark.asyncio
async def test_update_tag_duplicate_name_fails(client: AsyncClient, admin_headers: dict):
    """Test updating tag to duplicate name fails."""
    # Create two tags
    await client.post("/tags/", json={"name": "ExistingTag1"}, headers=admin_headers)
    create_resp = await client.post("/tags/", json={"name": "ExistingTag2"}, headers=admin_headers)
    tag2_id = create_resp.json()["id"]
    
    # Try to update tag2 to have tag1's name
    response = await client.put(f"/tags/{tag2_id}", json={"name": "ExistingTag1"}, headers=admin_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_tag_requires_admin(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Test that non-admin cannot delete tags."""
    # Create a tag
    create_resp = await client.post("/tags/", json={"name": "TagToDelete"}, headers=admin_headers)
    tag_id = create_resp.json()["id"]
    
    # Try to delete as non-admin
    response = await client.delete(f"/tags/{tag_id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_delete_tag(client: AsyncClient, admin_headers: dict):
    """Test that admin can delete tags."""
    # Create a tag
    create_resp = await client.post("/tags/", json={"name": "TagToBeDeleted"}, headers=admin_headers)
    tag_id = create_resp.json()["id"]
    
    # Delete the tag
    response = await client.delete(f"/tags/{tag_id}", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify it's gone
    get_resp = await client.get("/tags/")
    tags = get_resp.json()
    assert not any(t["id"] == tag_id for t in tags)


@pytest.mark.asyncio
async def test_delete_tag_not_found(client: AsyncClient, admin_headers: dict):
    """Test deleting non-existent tag returns 404."""
    response = await client.delete("/tags/99999", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Tag not found"


@pytest.mark.asyncio
async def test_delete_tag_removes_from_apps(client: AsyncClient, admin_headers: dict, auth_headers: dict):
    """Test that deleting a tag removes it from associated apps."""
    # Create a tag
    tag_resp = await client.post("/tags/", json={"name": "TagForApp"}, headers=admin_headers)
    tag_id = tag_resp.json()["id"]
    
    # Create an app with the tag
    app_resp = await client.post("/apps/", json={
        "title": "App With Tag",
        "prompt_text": "Testing tag deletion",
        "tag_ids": [tag_id]
    }, headers=auth_headers)
    app_slug = app_resp.json()["slug"]
    
    # Verify app has the tag
    app_detail = await client.get(f"/apps/{app_slug}")
    assert any(t["id"] == tag_id for t in app_detail.json()["tags"])
    
    # Delete the tag
    await client.delete(f"/tags/{tag_id}", headers=admin_headers)
    
    # Verify app no longer has the tag
    app_detail = await client.get(f"/apps/{app_slug}")
    assert not any(t["id"] == tag_id for t in app_detail.json()["tags"])


# =============================================================================
# TOOL CRUD TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_get_tools_public(client: AsyncClient):
    """Test that anyone can get tools list (no auth required)."""
    response = await client.get("/tools/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_tools_with_counts(client: AsyncClient):
    """Test getting tools with app counts."""
    response = await client.get("/tools/with-counts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Each tool should have app_count field
    if len(data) > 0:
        assert "app_count" in data[0]
        assert "name" in data[0]
        assert "id" in data[0]


@pytest.mark.asyncio
async def test_create_tool_requires_admin(client: AsyncClient, auth_headers: dict):
    """Test that non-admin cannot create tools."""
    response = await client.post("/tools/", json={"name": "TestTool"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_create_tool(client: AsyncClient, admin_headers: dict):
    """Test that admin can create tools."""
    response = await client.post("/tools/", json={"name": "AdminCreatedTool"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AdminCreatedTool"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_tool_fails(client: AsyncClient, admin_headers: dict):
    """Test that creating a duplicate tool name fails with 400."""
    # Create first tool
    await client.post("/tools/", json={"name": "DuplicateTool"}, headers=admin_headers)
    
    # Try to create duplicate
    response = await client.post("/tools/", json={"name": "DuplicateTool"}, headers=admin_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_tool_requires_admin(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Test that non-admin cannot update tools."""
    # Create a tool first
    create_resp = await client.post("/tools/", json={"name": "ToolToUpdate"}, headers=admin_headers)
    tool_id = create_resp.json()["id"]
    
    # Try to update as non-admin
    response = await client.put(f"/tools/{tool_id}", json={"name": "UpdatedTool"}, headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


@pytest.mark.asyncio
async def test_admin_can_update_tool(client: AsyncClient, admin_headers: dict):
    """Test that admin can update tools."""
    # Create a tool
    create_resp = await client.post("/tools/", json={"name": "ToolForUpdate"}, headers=admin_headers)
    tool_id = create_resp.json()["id"]
    
    # Update the tool
    response = await client.put(f"/tools/{tool_id}", json={"name": "UpdatedToolName"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedToolName"


@pytest.mark.asyncio
async def test_update_tool_not_found(client: AsyncClient, admin_headers: dict):
    """Test updating non-existent tool returns 404."""
    response = await client.put("/tools/99999", json={"name": "NoTool"}, headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Tool not found"


@pytest.mark.asyncio
async def test_update_tool_duplicate_name_fails(client: AsyncClient, admin_headers: dict):
    """Test updating tool to duplicate name fails."""
    # Create two tools
    await client.post("/tools/", json={"name": "ExistingTool1"}, headers=admin_headers)
    create_resp = await client.post("/tools/", json={"name": "ExistingTool2"}, headers=admin_headers)
    tool2_id = create_resp.json()["id"]
    
    # Try to update tool2 to have tool1's name
    response = await client.put(f"/tools/{tool2_id}", json={"name": "ExistingTool1"}, headers=admin_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_tool_requires_admin(client: AsyncClient, auth_headers: dict, admin_headers: dict):
    """Test that non-admin cannot delete tools."""
    # Create a tool
    create_resp = await client.post("/tools/", json={"name": "ToolToDelete"}, headers=admin_headers)
    tool_id = create_resp.json()["id"]
    
    # Try to delete as non-admin
    response = await client.delete(f"/tools/{tool_id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_delete_tool(client: AsyncClient, admin_headers: dict):
    """Test that admin can delete tools."""
    # Create a tool
    create_resp = await client.post("/tools/", json={"name": "ToolToBeDeleted"}, headers=admin_headers)
    tool_id = create_resp.json()["id"]
    
    # Delete the tool
    response = await client.delete(f"/tools/{tool_id}", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify it's gone
    get_resp = await client.get("/tools/")
    tools = get_resp.json()
    assert not any(t["id"] == tool_id for t in tools)


@pytest.mark.asyncio
async def test_delete_tool_not_found(client: AsyncClient, admin_headers: dict):
    """Test deleting non-existent tool returns 404."""
    response = await client.delete("/tools/99999", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Tool not found"


@pytest.mark.asyncio
async def test_delete_tool_removes_from_apps(client: AsyncClient, admin_headers: dict, auth_headers: dict):
    """Test that deleting a tool removes it from associated apps."""
    # Create a tool
    tool_resp = await client.post("/tools/", json={"name": "ToolForApp"}, headers=admin_headers)
    tool_id = tool_resp.json()["id"]
    
    # Create an app with the tool
    app_resp = await client.post("/apps/", json={
        "title": "App With Tool",
        "prompt_text": "Testing tool deletion",
        "tool_ids": [tool_id]
    }, headers=auth_headers)
    app_slug = app_resp.json()["slug"]
    
    # Verify app has the tool
    app_detail = await client.get(f"/apps/{app_slug}")
    assert any(t["id"] == tool_id for t in app_detail.json()["tools"])
    
    # Delete the tool
    await client.delete(f"/tools/{tool_id}", headers=admin_headers)
    
    # Verify app no longer has the tool
    app_detail = await client.get(f"/apps/{app_slug}")
    assert not any(t["id"] == tool_id for t in app_detail.json()["tools"])
