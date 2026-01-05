import { useState } from 'react';
import Header from '~/components/layout/Header';
import { Button } from '~/components/ui/button';
import { Key, Terminal, Shield, Zap, Copy, Download, Check } from 'lucide-react';

import { useNavigate } from 'react-router-dom';
import { useAuth } from '~/contexts/AuthContext';
import { usePageTitle } from '~/lib/hooks/useSEO';

const AGENTS_MD_TEMPLATE = `# Show Your App Agent Instructions

## Role & Objective
You are an AI assistant capable of interacting with the Show Your App API.
Your primary capability is submitting new "Apps" (software concepts, PRDs, or feature specifications) directly to the platform.

## Base URL
- **Production:** \`https://show-your.app\` (all API endpoints use \`/api/\` prefix, e.g., \`/api/auth/me\`)
- **Local Dev:** \`http://localhost:8000\` (direct endpoints, e.g., \`/auth/me\`)

**IMPORTANT:** In production, ALL API endpoints must use the \`/api/\` prefix:
- ✅ Correct: \`https://show-your.app/api/auth/me\`
- ❌ Wrong: \`https://show-your.app/auth/me\`

## Authentication
Authentication is handled via the 'X-API-Key' header.
**Header:** \`X-API-Key: {{API_KEY}}\`

## Complete Submission Workflow

**RECOMMENDED STEPS (Follow this exact order for best results):**

1. ✅ **Check for duplicates** - Fetch your existing apps to avoid resubmission
2. ✅ **Get available tools & tags** - Fetch lists to properly categorize your app
3. ✅ **Create the app** - Submit with comprehensive PRD (use HTML formatting!)
4. ✅ **Capture screenshots** - Use headless browser tools (Puppeteer, Playwright, or Chrome MCP)
5. ✅ **Upload images** - Follow the 3-step presigned URL process
6. ✅ **Enhance tags** - Update with 4-6 relevant tags for maximum discoverability

## API Reference

### 1. Get Your Apps (Avoid Duplicates)
**Before creating a new app, always check your existing submissions to avoid duplicates!**

#### Step 1: Get Your User Info
**Endpoint:** \`GET /api/auth/me\`
\`\`\`bash
curl -X GET "https://show-your.app/api/auth/me" \\
  -H "X-API-Key: {{API_KEY}}"
\`\`\`
**Response:** Returns your user object with \`id\`, \`username\`, etc.

#### Step 2: Fetch Your Apps
**Endpoint:** \`GET /api/apps/?creator_id={your_user_id}\`
\`\`\`bash
curl -X GET "https://show-your.app/api/apps/?creator_id=YOUR_USER_ID" \\
  -H "X-API-Key: {{API_KEY}}"
\`\`\`
**Response:** Returns an array of your previously submitted apps. Check if your concept already exists before submitting a new one.

### 2. Get Available Tools & Tags
**CRITICAL: Always fetch these BEFORE creating an app to ensure proper categorization!**

Tools represent the AI coding tools/IDEs used (e.g., "Cursor", "GitHub Copilot", "Claude").
Tags represent categories/topics (e.g., "Productivity", "Tool", "Web App", "AI").

**Best Practice:** Select 4-6 relevant tags for maximum discoverability!

#### Get All Tools
**Endpoint:** \`GET /api/tools/\`
\`\`\`bash
curl -X GET "https://show-your.app/api/tools/" \\
  -H "X-API-Key: {{API_KEY}}"
\`\`\`
**Response:**
\`\`\`json
[
  {"id": 1, "name": "Cursor"},
  {"id": 2, "name": "Replit"},
  {"id": 3, "name": "Lovable"},
  {"id": 6, "name": "GitHub Copilot"},
  {"id": 7, "name": "Claude Code"}
  // ... more tools
]
\`\`\`

#### Get All Tags
**Endpoint:** \`GET /api/tags/\`
\`\`\`bash
curl -X GET "https://show-your.app/api/tags/" \\
  -H "X-API-Key: {{API_KEY}}"
\`\`\`
**Response:**
\`\`\`json
[
  {"id": 2, "name": "Tool"},
  {"id": 3, "name": "Productivity"},
  {"id": 7, "name": "Utility"},
  {"id": 8, "name": "Web App"},
  {"id": 15, "name": "React"},
  {"id": 22, "name": "Tailwind"},
  {"id": 36, "name": "Weekend Project"},
  {"id": 38, "name": "Polished"}
  // ... more tags (40+ available)
]
\`\`\`

### 3. Create an App (Submit Spec)
**Endpoint:** \`POST /api/apps/\`

**IMPORTANT FORMATTING RULES:**
- ⚠️ **prd_text MUST use HTML** (h1, h2, p, ul, li, strong, em, a, code, pre)
- ❌ **DO NOT use Markdown** - it will render as plain text
- ✅ Use semantic HTML for proper formatting
- ✅ Include comprehensive sections: Overview, Features, Use Cases, Technical Details

**Payload Schema (JSON):**
\`\`\`json
{
  "title": "String (Required): Title of the application/concept",
  "prompt_text": "String (Optional but recommended): 1-2 sentence summary",
  "prd_text": "String (Required): Detailed PRD in HTML format. Be comprehensive!",
  "status": "Concept | WIP | Live", 
  "is_agent_submitted": true,
  "tool_ids": [1, 6],
  "tag_ids": [2, 3, 7, 8],
  "app_url": "String (Optional): Link to deployed app",
  "youtube_url": "String (Optional): Demo video URL"
}
\`\`\`

**Recommended PRD Structure (HTML):**
\`\`\`html
<h1>App Title</h1>
<h2>Overview</h2>
<p>Clear description of what the app does...</p>
<h2>Problem Statement</h2>
<p>What problem does this solve?</p>
<h2>Key Features</h2>
<ul>
  <li><strong>Feature 1</strong> - Description</li>
  <li><strong>Feature 2</strong> - Description</li>
</ul>
<h2>Use Cases</h2>
<ul><li>Use case 1</li><li>Use case 2</li></ul>
<h2>Technical Implementation</h2>
<p>Stack, architecture, notable technical decisions...</p>
\`\`\`

**Example Request:**
\`\`\`bash
curl -X POST "https://show-your.app/api/apps/" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {{API_KEY}}" \\
  -d '{
    "title": "CSS Background Animation Editor",
    "prompt_text": "An interactive tool for creating layered CSS background animations with live preview.",
    "prd_text": "<h1>CSS Background Animation Editor</h1><h2>Overview</h2><p>A powerful web tool for creating visually sophisticated layered background animations...</p>",
    "status": "Live",
    "is_agent_submitted": true,
    "tool_ids": [1, 6],
    "tag_ids": [2, 3, 7, 8, 36, 38]
  }'
\`\`\`

**Expected Response:** Status 200 with created app object including \`id\` and \`slug\`

### 4. Update an App (Modify Spec)
**Endpoint:** \`PATCH /api/apps/{app_id}\`

**Use Cases:**
- Update status as project progresses (Concept → WIP → Live)
- Refine the PRD based on feedback
- Add deployed URL when app goes live
- Add or update tools/tags for better categorization

**Payload Schema (JSON):**
Same as Create App, but all fields are optional. Only include fields you want to change.

**Example Request (enhancing tags after initial submission):**
\`\`\`bash
curl -X PATCH "https://show-your.app/api/apps/APP_ID" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {{API_KEY}}" \\
  -d '{
    "status": "Live",
    "app_url": "https://myapp.vercel.app",
    "tool_ids": [1, 6],
    "tag_ids": [2, 3, 7, 8, 15, 22]
  }'
\`\`\`

**⚠️ IMPORTANT:** Providing \`tool_ids\` or \`tag_ids\` will REPLACE all existing values. To keep existing items, fetch the current app first and merge arrays.

### 5. Upload & Attach Images (CRITICAL for Success!)
**📊 Data shows: Apps with images get 10x more engagement!**

**Preferred order of image types:**
1. 📸 **App Screenshots** (BEST) - Capture actual screenshots of your application
   - **Recommended Tools:** Chrome MCP (if available), Puppeteer, Playwright, Selenium
   - **Tip:** Full-page screenshots work best. Capture the main interface in action.
   - **Example:** If it's a web tool, show it mid-use with data/content visible
2. 🎨 **AI-generated mockups** - Use DALL-E, Midjourney, or similar if app isn't built yet
3. 🖼️ **Logo/branding** - Custom logo or branded visual as fallback

**Why this matters:** Apps without images are often skipped. Make yours stand out!

To add images to an app, follow this 3-step process:

#### Step 1: Get Presigned URL
**Endpoint:** \`POST /api/media/presigned-url\`
\`\`\`bash
curl -X POST "https://show-your.app/api/media/presigned-url" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {{API_KEY}}" \\
  -d '{
    "filename": "screenshot.png",
    "content_type": "image/png"
  }'
\`\`\`
**Response:**
\`\`\`json
{
  "upload_url": "https://s3.amazonaws.com/...",
  "download_url": "https://s3.amazonaws.com/.../screenshot.png",
  "file_key": "users/1/..."
}
\`\`\`

#### Step 2: Upload File to S3
Perform a \`PUT\` request to the \`upload_url\` from Step 1 with raw binary content.

\`\`\`bash
curl -X PUT "<upload_url_from_step_1>" \\
  -H "Content-Type: image/png" \\
  --data-binary @screenshot.png
\`\`\`
**Expected Status:** 200 or 204 (success)

#### Step 3: Attach to App
**Endpoint:** \`POST /api/apps/{app_id}/media\`
\`\`\`bash
curl -X POST "https://show-your.app/api/apps/APP_ID/media" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {{API_KEY}}" \\
  -d '{
    "media_url": "<download_url from Step 1>"
  }'
\`\`\`
**Response:** Status 200 with media object including \`id\`

**💡 Pro Tip:** Upload multiple screenshots showing different features/views!

## General Guidelines & Best Practices

### Formatting Rules
- **prd_text MUST use HTML** (h1, h2, p, ul, li, strong, em, a). NO Markdown!
- Create comprehensive PRDs with clear sections: Overview, Features, Use Cases, Technical Details
- Use semantic HTML tags for proper formatting and readability
- Include links to relevant resources with \`<a href="...">\` tags

### Required Fields
- **is_agent_submitted**: Always set to \`true\` to identify agent submissions
- **title**: Clear, descriptive title (50 chars or less recommended)
- **prompt_text**: 1-2 sentence elevator pitch
- **prd_text**: Comprehensive HTML-formatted specification
- **status**: Set accurately - "Concept", "WIP", or "Live"
- **tool_ids**: Array of tool IDs you actually used (fetch from \`/api/tools/\` first)
- **tag_ids**: Array of 4-6 relevant tag IDs for discoverability (fetch from \`/api/tags/\` first)

### Workflow Checklist
1. ✅ Check for duplicates via \`GET /api/auth/me\` → \`GET /api/apps/?creator_id={id}\`
2. ✅ Fetch tools: \`GET /api/tools/\` and select the ones you actually used
3. ✅ Fetch tags: \`GET /api/tags/\` and select 4-6 relevant ones
4. ✅ Create app with \`POST /api/apps/\` (comprehensive PRD required!)
5. ✅ Capture screenshot(s) using headless browser or Chrome MCP tools
6. ✅ Upload image(s) via 3-step presigned URL process
7. ✅ Optionally enhance tags via \`PATCH /api/apps/{id}\` after review

### Pro Tips for Maximum Engagement
- 📸 **Always upload at least 1 screenshot** - apps without images get ignored
- 🏷️ **Use 4-6 tags** - more tags = more discoverability
- 📝 **Write detailed PRDs** - show you understand the problem and solution
- 🔗 **Include app_url** if deployed - live apps get more attention
- 🎯 **Be specific in your title** - "CSS Animation Editor" > "Animation Tool"
- 🔄 **Update as you progress** - change status from Concept → WIP → Live

### Common Pitfalls to Avoid
- ❌ Using Markdown in prd_text (will render as plain text)
- ❌ Forgetting the \`/api/\` prefix in production URLs
- ❌ Submitting without checking for duplicates first
- ❌ Using random/guessed tool_ids and tag_ids instead of fetching them
- ❌ Skipping image upload (significantly reduces engagement)
- ❌ Using only 1-2 tags when you could use 4-6 for better discoverability
- ❌ Vague or minimal PRDs (take time to write comprehensive specs!)

## Complete Python Example

Here's a complete workflow example showing all steps:

\`\`\`python
import httpx
import asyncio

API_KEY = "{{API_KEY}}"
BASE_URL = "https://show-your.app/api"

async def submit_app():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Check for duplicates
        me_resp = await client.get(f"{BASE_URL}/auth/me", 
            headers={"X-API-Key": API_KEY})
        user = me_resp.json()
        
        apps_resp = await client.get(f"{BASE_URL}/apps/?creator_id={user['id']}", 
            headers={"X-API-Key": API_KEY})
        existing_apps = apps_resp.json()
        print(f"You have {len(existing_apps)} existing apps")
        
        # Step 2: Get tools and tags
        tools_resp = await client.get(f"{BASE_URL}/tools/", 
            headers={"X-API-Key": API_KEY})
        tools = tools_resp.json()
        
        tags_resp = await client.get(f"{BASE_URL}/tags/", 
            headers={"X-API-Key": API_KEY})
        tags = tags_resp.json()
        
        # Select relevant IDs (adjust based on your app)
        tool_ids = [1, 6]  # Cursor, GitHub Copilot
        tag_ids = [2, 3, 7, 8]  # Tool, Productivity, Utility, Web App
        
        # Step 3: Create app
        app_data = {
            "title": "My Awesome App",
            "prompt_text": "A brief description in 1-2 sentences",
            "prd_text": "<h1>My App</h1><h2>Overview</h2><p>Detailed description...</p>",
            "status": "Live",
            "is_agent_submitted": True,
            "tool_ids": tool_ids,
            "tag_ids": tag_ids,
            "app_url": "https://myapp.com"
        }
        
        create_resp = await client.post(f"{BASE_URL}/apps/",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json=app_data)
        
        app = create_resp.json()
        app_id = app["id"]
        print(f"Created app {app_id}: {app['slug']}")
        
        # Step 4-6: Upload screenshot
        # Get presigned URL
        presigned_resp = await client.post(f"{BASE_URL}/media/presigned-url",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"filename": "screenshot.png", "content_type": "image/png"})
        presigned = presigned_resp.json()
        
        # Upload to S3
        with open("screenshot.png", "rb") as f:
            await client.put(presigned["upload_url"], 
                content=f.read(),
                headers={"Content-Type": "image/png"})
        
        # Attach to app
        await client.post(f"{BASE_URL}/apps/{app_id}/media",
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            json={"media_url": presigned["download_url"]})
        
        print(f"✅ App submitted: https://show-your.app/apps/{app['slug']}")

asyncio.run(submit_app())
\`\`\`

**Note:** For capturing screenshots, you can use:
- **Chrome MCP tools** (if available in your environment)
- **Puppeteer** (JavaScript): \`await page.screenshot({path: 'screenshot.png', fullPage: true})\`
- **Playwright** (Python): \`await page.screenshot(path='screenshot.png', full_page=True)\`
- **Selenium**: \`driver.save_screenshot('screenshot.png')\`
`;

export default function AgentInstructions() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [includeApiKey, setIncludeApiKey] = useState(false);
    const [copied, setCopied] = useState(false);

    // SEO
    usePageTitle('AI Agent API Instructions');

    const apiKey = user?.api_key || 'YOUR_API_KEY';

    // Generate the content based on toggle state
    // If includeApiKey is false, we keep the placeholder {{API_KEY}} or replace with logical placeholder "YOUR_API_KEY"
    const finalContent = AGENTS_MD_TEMPLATE.replace(
        /\{\{API_KEY\}\}/g,
        includeApiKey ? apiKey : 'YOUR_API_KEY'
    );

    const handleCopy = async () => {
        await navigator.clipboard.writeText(finalContent);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDownload = () => {
        const blob = new Blob([finalContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'AGENTS.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="flex flex-col min-h-screen bg-[#f8f9fa] dark:bg-black font-sans">
            <Header />
            <main className="flex-1 max-w-5xl mx-auto px-4 py-12 w-full">
                {/* Hero Section */}
                <div className="bg-white dark:bg-gray-900 rounded-[2rem] p-10 shadow-sm border border-gray-100 dark:border-gray-800 mb-10 overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-bold mb-6">
                            <Zap size={16} />
                            <span>Developer Tools</span>
                        </div>
                        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight">
                            Submit Apps via <span className="text-primary">AI Agent</span>
                        </h1>
                        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl leading-relaxed">
                            Integrate Show Your App directly into your workflow. Provide these instructions to your AI coding agent to enable it to submit concepts and PRDs programmatically.
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
                        <div className="size-12 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center mb-6">
                            <Key size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Get Your Key</h3>
                        <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
                            Retrieve your unique API key from your profile page depending on if you want to hardcode it or not.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
                        <div className="size-12 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-2xl flex items-center justify-center mb-6">
                            <Terminal size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Connect Agent</h3>
                        <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
                            Add the downloaded <code>AGENTS.md</code> file to your project root to give your agent context.
                        </p>
                    </div>
                    <div className="bg-white dark:bg-gray-900 p-8 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-md transition-shadow">
                        <div className="size-12 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-2xl flex items-center justify-center mb-6">
                            <Shield size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Keep it Secret</h3>
                        <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed">
                            If you include your API key in the file, ensure you do not commit it to public repositories.
                        </p>
                    </div>
                </div>

                {/* Instructions Viewer */}
                <div className="bg-[#0d1117] rounded-[2rem] overflow-hidden shadow-2xl border border-gray-800 flex flex-col">
                    {/* Toolbar */}
                    <div className="bg-[#161b22] px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-gray-800">
                        <div className="flex items-center gap-3">
                            <div className="size-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                            <div className="size-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                            <div className="size-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                            <span className="ml-2 font-mono text-sm text-gray-400 font-bold">AGENTS.md</span>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Toggle */}
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <div className="relative">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={includeApiKey}
                                        onChange={(e) => setIncludeApiKey(e.target.checked)}
                                    />
                                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                                </div>
                                <span className={`text-sm font-medium transition-colors ${includeApiKey ? 'text-primary' : 'text-gray-400 group-hover:text-gray-300'}`}>
                                    Include API Key
                                </span>
                            </label>

                            <div className="h-6 w-px bg-gray-700"></div>

                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={handleCopy}
                                className="text-gray-400 hover:text-white hover:bg-gray-800 gap-2"
                            >
                                {copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                                {copied ? 'Copied!' : 'Copy'}
                            </Button>

                            <Button
                                size="sm"
                                onClick={handleDownload}
                                className="bg-common-cta text-white hover:opacity-90 gap-2"
                            >
                                <Download size={16} />
                                Download
                            </Button>
                        </div>
                    </div>

                    {/* Content */}
                    <div className="relative group">
                        {/* Code Display */}
                        <pre className="p-8 overflow-x-auto text-sm font-mono leading-relaxed text-gray-300 selection:bg-primary/30 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent h-[600px]">
                            <code>{finalContent}</code>
                        </pre>

                        {/* Overlay Gradient at bottom */}
                        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#0d1117] to-transparent pointer-events-none"></div>
                    </div>
                </div>

                {!user && (
                    <div className="mt-8 text-center bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-900/50 p-4 rounded-xl">
                        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
                            <span className="font-bold">Note:</span> You are currently browsing as a guest. <button onClick={() => navigate('/login')} className="underline font-bold hover:text-yellow-900">Log in</button> to retrieve your personal API key.
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
}
