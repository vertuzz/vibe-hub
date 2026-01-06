"""Entry point for ShowApp Agent."""

import argparse
import asyncio
import sys
from pathlib import Path

from claude_code_sdk import ClaudeCodeOptions, ClaudeSDKClient

from .server import (
    bootstrap,
    format_context_for_prompt,
    get_allowed_tools,
    get_combined_mcp_servers,
)


DEFAULT_SYSTEM_PROMPT = """You are an expert app submission agent for Show Your App, a launchpad for AI-generated software.

Your job is to:
1. Visit the app link provided by the user (using Playwright browser tools)
2. Explore the app and understand what it does
3. Take screenshots of the main UI and key features
4. Create a compelling listing on Show Your App using the showapp tools

## Workflow

1. **Navigate to the app URL** - Use mcp__playwright__browser_navigate to open the link
2. **Get page snapshot** - Use mcp__playwright__browser_snapshot to see the page accessibility tree and understand content
3. **Take screenshots** - Use mcp__playwright__browser_take_screenshot with these REQUIRED parameters:
   - `filename`: ALWAYS specify a filename like "screenshot1.png" to save to disk (NEVER omit this!)
   - `type`: "png" or "jpeg"
   - `fullPage`: false (avoid full page screenshots - they're too large)
4. **Explore if needed** - Click elements with mcp__playwright__browser_click to explore features
5. **Check for duplicates** - Review your existing apps list to avoid duplicates
6. **Create the listing** - Use mcp__showapp__create_app with:
   - A specific, descriptive title (not generic)
   - A compelling 1-2 sentence hook (prompt_text)
   - A full HTML description (prd_text) with sections: What It Does, Key Features, How It Was Built, Try It
   - Appropriate tool_ids and tag_ids from the available lists
   - Status: "Live" if the app is deployed, "WIP" if in progress
7. **Upload screenshots** - For each screenshot file you saved:
   - mcp__showapp__get_presigned_url (with filename and content_type e.g. "image/png")
   - mcp__showapp__upload_file_to_s3 (with the absolute file path to the screenshot and presigned URL)
   - mcp__showapp__attach_media_to_app (with the app_id and download_url)

## CRITICAL: Screenshot Rules

- ALWAYS use `filename` parameter when taking screenshots (e.g., "screenshot1.png")
- NEVER request fullPage screenshots - they exceed buffer limits
- Take viewport screenshots only (the visible portion of the page)
- If you need to capture more, scroll down and take multiple smaller screenshots
- Screenshots are saved to the current working directory

## Important Rules

- Always set is_agent_submitted: true (the tool does this automatically)
- Use HTML tags in prd_text: <h2>, <p>, <ul>, <li>, <strong>, <code>
- Pick 1-3 tool_ids based on how the app was built
- Pick 4-6 tag_ids based on what the app does
- If status is "Live", app_url is required
- Apps with screenshots get 10x more engagement - always upload them!

## Available Playwright Tools

- browser_navigate: Navigate to a URL
- browser_snapshot: Get accessibility tree of the page (use this to read page content)
- browser_click: Click an element by its ref from snapshot
- browser_type: Type text into an input field
- browser_take_screenshot: Capture screenshot - ALWAYS use filename parameter!
- browser_scroll_down / browser_scroll_up: Scroll the page
- browser_press_key: Press keyboard keys
- browser_close: Close the page when done
"""


async def run_agent(
    prompt: str,
    cwd: str | Path | None = None,
    verbose: bool = False,
) -> None:
    """Run the ShowApp agent with the given prompt."""
    
    # Bootstrap: pre-fetch context
    print("Bootstrapping agent context...")
    context = await bootstrap()
    context_str = format_context_for_prompt(context)
    
    if verbose:
        print("\n--- Pre-fetched Context ---")
        print(context_str)
        print("--- End Context ---\n")
    
    # Build the full prompt with context
    full_prompt = f"""## Pre-loaded Context

{context_str}

## User Request

{prompt}
"""
    
    # Configure the agent
    options = ClaudeCodeOptions(
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        mcp_servers=get_combined_mcp_servers(),
        allowed_tools=get_allowed_tools(),
        permission_mode="acceptEdits",  # Auto-accept file operations
        cwd=str(cwd) if cwd else None,
    )
    
    print("Starting ShowApp agent...")
    print("-" * 50)
    
    async with ClaudeSDKClient(options=options) as client:
        await client.query(full_prompt)
        
        async for message in client.receive_response():
            # Handle different message types
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        print(block.text)
                    elif hasattr(block, "name"):
                        # Tool use
                        if verbose:
                            print(f"\n[Tool: {block.name}]")
            elif hasattr(message, "type") and message.type == "result":
                if verbose:
                    print(f"\n[Result - Cost: ${message.cost_usd:.4f}]")
    
    print("-" * 50)
    print("Agent finished.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ShowApp Agent - Submit apps to Show Your App using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  showapp-agent "Submit this app: https://example.com/my-app"
  showapp-agent --verbose "Submit https://cool-demo.vercel.app"
  showapp-agent --cwd /tmp/screenshots "Submit https://app.example.com"
        """,
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="The prompt describing what to do (e.g., URL to submit)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        help="Working directory for the agent (for screenshots, etc.)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including tool calls",
    )
    parser.add_argument(
        "--bootstrap-only",
        action="store_true",
        help="Only run bootstrap and print context (for testing)",
    )
    
    args = parser.parse_args()
    
    if args.bootstrap_only:
        async def _bootstrap():
            context = await bootstrap()
            print(format_context_for_prompt(context))
        asyncio.run(_bootstrap())
        return
    
    if not args.prompt:
        parser.print_help()
        sys.exit(1)
    
    asyncio.run(run_agent(
        prompt=args.prompt,
        cwd=args.cwd,
        verbose=args.verbose,
    ))


if __name__ == "__main__":
    main()
