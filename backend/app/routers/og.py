"""
Open Graph meta tags endpoint for social media sharing.

Social media crawlers (Telegram, WhatsApp, Discord, Twitter, Facebook, etc.) 
don't execute JavaScript, so they can't see the dynamically loaded content in SPAs.
This endpoint serves HTML pages with proper OG meta tags for each app.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from html import escape

from app.database import get_db
from app.models import App

router = APIRouter()

BASE_URL = "https://show-your.app"
DEFAULT_OG_IMAGE = f"{BASE_URL}/og-image.png"


def get_app_og_image(app: App) -> str:
    """Get the best image for OG sharing from app media."""
    if app.media and len(app.media) > 0:
        # Use the first media image
        return app.media[0].media_url
    return DEFAULT_OG_IMAGE


def get_app_description(app: App) -> str:
    """Generate a description for the app."""
    if app.prompt_text:
        # Truncate to ~200 chars for OG description
        desc = app.prompt_text[:200]
        if len(app.prompt_text) > 200:
            desc += "..."
        return desc
    return "Discover this AI-powered app on Show Your App - the launchpad for AI-generated software."


def generate_og_html(
    title: str,
    description: str,
    image: str,
    url: str,
    site_name: str = "Show Your App",
    og_type: str = "website"
) -> str:
    """Generate an HTML page with Open Graph meta tags."""
    # Escape all user content to prevent XSS
    title = escape(title)
    description = escape(description)
    image = escape(image)
    url = escape(url)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>{title}</title>
    <meta name="title" content="{title}">
    <meta name="description" content="{description}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="{og_type}">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{image}">
    <meta property="og:site_name" content="{site_name}">
    <meta property="og:locale" content="en_US">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="{url}">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{image}">
    
    <!-- Telegram specific -->
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{url}">
    
    <!-- Redirect browsers to the SPA -->
    <meta http-equiv="refresh" content="0;url={url}">
    <script>window.location.href = "{url}";</script>
</head>
<body>
    <p>Redirecting to <a href="{url}">{title}</a>...</p>
</body>
</html>"""


@router.get("/apps/{slug}", response_class=HTMLResponse)
async def get_app_og(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Serve Open Graph meta tags for an app.
    This endpoint is hit by social media crawlers to get preview data.
    """
    # Try to find the app
    query = select(App).options(
        selectinload(App.media),
        selectinload(App.creator)
    )
    
    if slug.isdigit():
        query = query.filter(App.id == int(slug))
    else:
        query = query.filter(App.slug == slug)
    
    result = await db.execute(query)
    app = result.scalars().first()
    
    if not app:
        # Return generic OG tags for 404
        return HTMLResponse(
            content=generate_og_html(
                title="App Not Found - Show Your App",
                description="This app could not be found on Show Your App.",
                image=DEFAULT_OG_IMAGE,
                url=BASE_URL
            ),
            status_code=200  # Return 200 so crawlers still get meta tags
        )
    
    # Build app-specific OG tags
    app_url = f"{BASE_URL}/apps/{app.slug}"
    title = f"{app.title} - Show Your App" if app.title else "AI App - Show Your App"
    description = get_app_description(app)
    image = get_app_og_image(app)
    
    return HTMLResponse(
        content=generate_og_html(
            title=title,
            description=description,
            image=image,
            url=app_url,
            og_type="article"
        )
    )


@router.get("/users/{username}", response_class=HTMLResponse)
async def get_user_og(username: str, db: AsyncSession = Depends(get_db)):
    """
    Serve Open Graph meta tags for a user profile.
    """
    from app.models import User
    
    result = await db.execute(
        select(User).filter(User.username == username)
    )
    user = result.scalars().first()
    
    if not user:
        return HTMLResponse(
            content=generate_og_html(
                title="User Not Found - Show Your App",
                description="This user could not be found on Show Your App.",
                image=DEFAULT_OG_IMAGE,
                url=BASE_URL
            ),
            status_code=200
        )
    
    user_url = f"{BASE_URL}/users/{user.username}"
    title = f"{user.full_name or user.username} - Show Your App"
    description = user.bio if user.bio else f"Check out {user.username}'s AI apps on Show Your App."
    image = user.avatar if user.avatar else DEFAULT_OG_IMAGE
    
    return HTMLResponse(
        content=generate_og_html(
            title=title,
            description=description,
            image=image,
            url=user_url,
            og_type="profile"
        )
    )
