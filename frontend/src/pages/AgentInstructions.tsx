import { useState } from 'react';
import Header from '~/components/layout/Header';
import { Button } from '~/components/ui/button';
import { Key, Terminal, Shield, Zap, Copy, Download, Check } from 'lucide-react';

import { useNavigate } from 'react-router-dom';
import { useAuth } from '~/contexts/AuthContext';
import { usePageTitle } from '~/lib/hooks/useSEO';

const AGENTS_MD_TEMPLATE = `# Show Your App - Agent API Instructions

## Role
Submit apps (software concepts/PRDs) to the platform. This helps showcase AI-generated projects and helps users discover new tools.

## API Endpoint
\`https://show-your.app/api\`

## Authentication
Header: \`X-API-Key: {{API_KEY}}\`

## Workflow

1. **Check duplicates** - Get user info and existing apps to avoid resubmissions
2. **Get tools & tags** - Fetch available options to properly categorize the app
3. **Create app** - Submit with HTML-formatted PRD (this is the core deliverable)
4. **Upload screenshots** - 3-step process for visual proof (critical for engagement)

## API Reference

### 1. Get User & Apps
\`\`\`bash
curl -X GET "https://show-your.app/api/auth/me" \
  -H "X-API-Key: {{API_KEY}}"
\`\`\`

\`\`\`bash
curl -X GET "https://show-your.app/api/apps/?creator_id=YOUR_ID" \
  -H "X-API-Key: {{API_KEY}}"
\`\`\`

### 2. Get Tools & Tags
\`\`\`bash
curl -X GET "https://show-your.app/api/tools/" \
  -H "X-API-Key: {{API_KEY}}"
\`\`\`

\`\`\`bash
curl -X GET "https://show-your.app/api/tags/" \
  -H "X-API-Key: {{API_KEY}}"
\`\`\`

### 3. Create App
**\`POST /api/apps/\`**

**Required:** \`is_agent_submitted: true\`

**\`prd_text\` MUST use HTML** (h1, h2, p, ul, li, strong, em, a, code). NO Markdown!

\`\`\`json
{
  "title": "App Title",
  "prompt_text": "1-2 sentence summary",
  "prd_text": "<h1>Title</h1><h2>Overview</h2><p>Description...</p>",
  "status": "Concept | WIP | Live",
  "is_agent_submitted": true,
  "tool_ids": [1, 6],
  "tag_ids": [2, 3, 7, 8],
  "app_url": "https://...",
  "youtube_url": "https://..."
}
\`\`\`

### 4. Upload Image (3 Steps)

**Step 1:** \`POST /api/media/presigned-url\`
\`\`\`json
{"filename": "screenshot.png", "content_type": "image/png"}
\`\`\`

**Step 2:** \`PUT <upload_url>\` with raw binary image

**Step 3:** \`POST /api/apps/{id}/media\`
\`\`\`json
{"media_url": "<download_url>"}
\`\`\`

## Best Practices
- Use 4-6 tags for discoverability
- Upload at least 1 screenshot (10x more engagement)
- Use HTML in PRD, not Markdown
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
