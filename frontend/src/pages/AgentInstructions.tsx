import Header from '~/components/layout/Header';
import { Button } from '~/components/ui/button';
import { Key, Terminal, Shield, Zap, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function AgentInstructions() {
    const navigate = useNavigate();

    return (
        <div className="flex flex-col min-h-screen bg-[#f8f9fa]">
            <Header />
            <main className="flex-1 max-w-4xl mx-auto px-4 py-12 w-full">
                {/* Hero Section */}
                <div className="bg-white rounded-[2rem] p-10 shadow-sm border border-gray-100 mb-10 overflow-hidden relative">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>

                    <div className="relative z-10">
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-bold mb-6">
                            <Zap size={16} />
                            <span>Developer Tools</span>
                        </div>
                        <h1 className="text-4xl font-extrabold text-gray-900 mb-4 tracking-tight">
                            Submit Dreams via <span className="text-primary">AI Agent</span>
                        </h1>
                        <p className="text-xl text-gray-600 max-w-2xl leading-relaxed">
                            Integrate Dreamware directly into your workflow. Use our AI agent to submit concepts, PRDs, and app specs programmatically.
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <div className="size-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
                            <Key size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Get Your Key</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">
                            Retrieve your unique API key from your profile page. This key identifies you and your dreams.
                        </p>
                    </div>
                    <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <div className="size-12 bg-purple-50 text-purple-600 rounded-2xl flex items-center justify-center mb-6">
                            <Terminal size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Connect Agent</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">
                            Use the provided API key in your agent's configuration to enable dream submissions.
                        </p>
                    </div>
                    <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm">
                        <div className="size-12 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mb-6">
                            <Shield size={24} />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Keep it Secret</h3>
                        <p className="text-gray-500 text-sm leading-relaxed">
                            Never share your API key. If compromised, you can regenerate it in your settings.
                        </p>
                    </div>
                </div>

                <div className="bg-gray-900 rounded-[2rem] p-10 text-white shadow-2xl overflow-hidden relative group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent opacity-50"></div>
                    <div className="relative z-10">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                            <Terminal size={24} className="text-primary" />
                            Example Submission
                        </h2>
                        <div className="bg-black/40 rounded-2xl p-6 font-mono text-sm text-gray-300 border border-white/10 backdrop-blur-sm">
                            <p className="text-blue-400"># Use the Dreamware API to submit a dream</p>
                            <p>curl -X POST https://api.dreamware.ai/v1/dreams \</p>
                            <p className="pl-4">-H <span className="text-green-400">"X-API-Key: YOUR_API_KEY"</span> \</p>
                            <p className="pl-4">-H <span className="text-green-400">"Content-Type: application/json"</span> \</p>
                            <p className="pl-4">-d {'{'}</p>
                            <p className="pl-8 text-purple-300">"title"</p>: <p className="inline text-green-300">"My AI-Powered App"</p>,
                            <p className="pl-8 text-purple-300">"prompt_text"</p>: <p className="inline text-green-300">"A futuristic dashboard..."</p>
                            <p className="pl-4">{'}'}</p>
                        </div>

                        <div className="mt-10 flex flex-col sm:flex-row items-center gap-4">
                            <Button
                                onClick={() => navigate('/profile')}
                                className="w-full sm:w-auto bg-white text-gray-900 hover:bg-gray-100 px-8 h-12 rounded-xl font-bold gap-2"
                            >
                                Go to Profile to find Key
                                <ArrowRight size={18} />
                            </Button>
                            <p className="text-sm text-gray-400">
                                Need more help? Contact support or check our docs.
                            </p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
