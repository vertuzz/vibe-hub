import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

/**
 * OAuth Callback Page
 * 
 * This page is opened in a popup window after the user authenticates with Google/GitHub.
 * It extracts the authorization code from the URL and sends it back to the parent window
 * via postMessage, then closes itself.
 */
export default function OAuthCallback() {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
    const [errorMessage, setErrorMessage] = useState<string>('');
    const hasProcessed = useRef(false);

    useEffect(() => {
        // Prevent processing more than once
        if (hasProcessed.current) return;
        hasProcessed.current = true;
        
        const code = searchParams.get('code');
        const state = searchParams.get('state'); // 'google' or 'github'
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Handle OAuth errors
        if (error) {
            setStatus('error');
            setErrorMessage(errorDescription || error);
            
            // Send error to parent window
            if (window.opener) {
                window.opener.postMessage(
                    { type: 'oauth-callback', error: errorDescription || error },
                    window.location.origin
                );
                setTimeout(() => window.close(), 2000);
            }
            return;
        }

        // Handle successful OAuth callback
        if (code && state) {
            setStatus('success');
            
            // Send code to parent window
            if (window.opener) {
                window.opener.postMessage(
                    { type: 'oauth-callback', code, provider: state },
                    window.location.origin
                );
                // Close popup after sending message
                setTimeout(() => window.close(), 500);
            } else {
                // If no opener (user navigated directly), show message
                setStatus('error');
                setErrorMessage('This page should be opened in a popup. Please go back and try logging in again.');
            }
        } else {
            setStatus('error');
            setErrorMessage('Invalid callback parameters. Please try logging in again.');
        }
    }, [searchParams]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <div className="text-center space-y-4 p-8">
                {status === 'processing' && (
                    <>
                        <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                        <p className="text-muted-foreground">Processing authentication...</p>
                    </>
                )}
                
                {status === 'success' && (
                    <>
                        <div className="h-8 w-8 mx-auto text-green-500">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </div>
                        <p className="text-muted-foreground">Authentication successful! This window will close automatically.</p>
                    </>
                )}
                
                {status === 'error' && (
                    <>
                        <div className="h-8 w-8 mx-auto text-destructive">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M15 9l-6 6M9 9l6 6" strokeLinecap="round" />
                            </svg>
                        </div>
                        <p className="text-destructive font-medium">Authentication failed</p>
                        <p className="text-muted-foreground text-sm">{errorMessage}</p>
                    </>
                )}
            </div>
        </div>
    );
}
