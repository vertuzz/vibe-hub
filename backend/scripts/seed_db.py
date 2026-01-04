
import asyncio
import sys
import os
import random
from datetime import datetime, timedelta

# Add the backend directory to sys.path to allow importing from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import AsyncSessionLocal, engine
from app.models import Tool, Tag, User, App, AppMedia, Comment, Like, AppStatus
from app.core.security import generate_api_key
from app.utils import slugify

TOOLS = [
    "Cursor", "Windsurf", "Trae", "PearAI", "Replit Agent", "v0", "Bolt.new", 
    "Lovable", "Tempo", "Marblism", "Create.xyz", "Claude", "GPT", "DeepSeek", 
    "Gemini", "Grok", "Llama", "Midjourney", "Flux", "Ideogram", "Recraft", 
    "Google Image Gen", "Adobe Firefly", "Stable Diffusion", "DALL-E", 
    "GitHub Copilot", "TabNine", "Pieces for Developers", "Qodo", "Uizard", 
    "Figma AI", "Canva Magic Studio", "Runway", "Galileo AI", "Khroma"
]

TAGS = [
    "Cyberpunk", "Minimalist", "Brutalist", "SaaS", "Dashboard", "E-commerce", 
    "Portfolio", "AI-Native", "Prompt-to-App", "Dream Coding", "Full-Stack AI", 
    "Glassmorphism", "Neumorphism", "Dark Mode", "Light Mode", "Mobile First", 
    "Landing Page", "Retro", "Futuristic", "Clean", "Bento Grid", "Shadcn UI", 
    "Tailwind CSS", "Next.js"
]

# Users with predictable API keys for E2E testing
# Format: e2e-{username}-api-key for E2E test compatibility
USERS = [
    {
        "username": "admin",
        "email": "admin@show-your.app",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=admin",
        "is_admin": True,
        "reputation_score": 100.0,
        "github_id": "github_admin_123",
        "api_key": "e2e-admin-api-key"  # Predictable key for E2E tests
    },
    {
        "username": "vibe_master",
        "email": "vibe@show-your.app",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=vibe",
        "reputation_score": 85.5,
        "google_id": "google_vibe_456",
        "api_key": "e2e-vibe-master-api-key"
    },
    {
        "username": "agent_alpha",
        "email": "agent@show-your.app",
        "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alpha",
        "reputation_score": 50.0,
        "github_id": "github_agent_789",
        "api_key": "e2e-agent-alpha-api-key"  # Agent always has API key
    },
    {
        "username": "early_bird",
        "email": "tester@show-your.app",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=bird",
        "reputation_score": 12.0,
        "google_id": "google_bird_012",
        "api_key": "e2e-early-bird-api-key"
    }
]

APPS = [
    {
        "title": "Neon Dreams Dashboard",
        "creator": "admin",
        "description": "A futuristic dashboard for tracking app metrics. Built with Cursor and Shadcn UI.",
        "status": AppStatus.LIVE,
        "app_url": "https://neon-dreams.vercel.app",
        "tags": ["Cyberpunk", "Dashboard", "Dark Mode"],
        "tools": ["Cursor", "v0"],
        "media": ["https://images.unsplash.com/photo-1550745165-9bc0b252726f"]
    },
    {
        "title": "AI Snake Game",
        "creator": "agent_alpha",
        "description": "A classic snake game generated entirely by Replit Agent. Minimalist and fun.",
        "status": AppStatus.LIVE,
        "app_url": "https://ai-snake.replit.app",
        "is_agent_submitted": True,
        "tags": ["Minimalist", "Retro"],
        "tools": ["Replit Agent"],
        "media": ["https://images.unsplash.com/photo-1550745165-9bc0b252726f"]
    },
    {
        "title": "Vibe Coder Portfolio",
        "creator": "vibe_master",
        "description": "Showcasing the philosophy of vibe coding through a brutalist design.",
        "status": AppStatus.WIP,
        "tags": ["Brutalist", "Portfolio", "Dream Coding"],
        "tools": ["Windsurf", "Claude"],
        "media": ["https://images.unsplash.com/photo-1550745165-9bc0b252726f"]
    },
    {
        "title": "SaaS Starter Kit",
        "creator": "early_bird",
        "description": "Everything you need to launch your next AI app in minutes.",
        "status": AppStatus.CONCEPT,
        "tags": ["SaaS", "Next.js", "Tailwind CSS"],
        "tools": ["Cursor", "GPT"]
    }
]

COMMENTS = [
    "This looks amazing! Love the cyberpunk aesthetic.",
    "Did you use v0 for the layout? It looks very clean.",
    "Can you share the prompt you used for the snake game components?",
    "Great work! Excited to see where this goes.",
    "The brutalist design is a bit too raw for me, but I respect the execution."
]

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Seeding initial tools...")
        tool_map = {}
        for tool_name in TOOLS:
            result = await session.execute(select(Tool).where(Tool.name == tool_name))
            tool = result.scalar_one_or_none()
            if not tool:
                tool = Tool(name=tool_name)
                session.add(tool)
                print(f"Added tool: {tool_name}")
            tool_map[tool_name] = tool

        print("\nSeeding initial tags...")
        tag_map = {}
        for tag_name in TAGS:
            result = await session.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                print(f"Added tag: {tag_name}")
            tag_map[tag_name] = tag

        await session.flush() # Ensure tool/tag IDs are available

        print("\nSeeding users...")
        user_map = {}
        for user_data in USERS:
            result = await session.execute(select(User).where(User.username == user_data["username"]))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    avatar=user_data["avatar"],
                    is_admin=user_data.get("is_admin", False),
                    reputation_score=user_data["reputation_score"],
                    google_id=user_data.get("google_id"),
                    github_id=user_data.get("github_id"),
                    api_key=user_data.get("api_key") or generate_api_key()
                )
                session.add(user)
                print(f"Added user: {user_data['username']}")
            user_map[user_data["username"]] = user

        await session.flush()

        print("\nSeeding apps...")
        created_apps = []
        for app_data in APPS:
            result = await session.execute(select(App).where(App.title == app_data["title"]))
            app = result.scalar_one_or_none()
            if not app:
                creator = user_map[app_data["creator"]]
                app = App(
                    title=app_data["title"],
                    creator_id=creator.id,
                    prompt_text=app_data["description"],
                    status=app_data["status"],
                    app_url=app_data.get("app_url"),
                    is_agent_submitted=app_data.get("is_agent_submitted", False),
                    slug=slugify(app_data["title"])
                )
                
                # Add tags
                for tag_name in app_data.get("tags", []):
                    if tag_name in tag_map:
                        app.tags.append(tag_map[tag_name])
                
                # Add tools
                for tool_name in app_data.get("tools", []):
                    if tool_name in tool_map:
                        app.tools.append(tool_map[tool_name])
                
                session.add(app)
                await session.flush() # Get app ID
                
                # Add media
                for media_url in app_data.get("media", []):
                    media = AppMedia(app_id=app.id, media_url=media_url)
                    session.add(media)
                
                print(f"Added app: {app_data['title']}")
            
            created_apps.append(app)

        print("\nSeeding interactions (comments and likes)...")
        all_users = list(user_map.values())
        for app in created_apps:
            # Add some likes
            like_count = random.randint(1, len(all_users))
            likers = random.sample(all_users, like_count)
            for liker in likers:
                result = await session.execute(
                    select(Like).where(Like.app_id == app.id, Like.user_id == liker.id)
                )
                if not result.scalar_one_or_none():
                    like = Like(app_id=app.id, user_id=liker.id)
                    session.add(like)

            # Add some comments
            comment_count = random.randint(0, 3)
            for _ in range(comment_count):
                commenter = random.choice(all_users)
                content = random.choice(COMMENTS)
                comment = Comment(
                    app_id=app.id,
                    user_id=commenter.id,
                    content=content
                )
                session.add(comment)

        await session.commit()
        print("\nSeeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
