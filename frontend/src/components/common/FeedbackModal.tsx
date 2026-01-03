import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import type { FeedbackType } from '~/lib/types';

interface FeedbackModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (type: FeedbackType, message: string) => Promise<void>;
}

const feedbackTypes: { value: FeedbackType; label: string; icon: string; description: string }[] = [
    { value: 'feature', label: 'Feature Request', icon: '✨', description: 'Suggest a new feature or improvement' },
    { value: 'bug', label: 'Bug Report', icon: '🐛', description: 'Report something that\'s broken' },
    { value: 'other', label: 'Other', icon: '💬', description: 'General feedback or questions' },
];

export default function FeedbackModal({ isOpen, onClose, onSubmit }: FeedbackModalProps) {
    const [type, setType] = useState<FeedbackType>('feature');
    const [message, setMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isSuccess, setIsSuccess] = useState(false);

    // Prevent body scroll when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    // Handle escape key
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape' && isOpen && !isSubmitting) {
                handleClose();
            }
        };
        window.addEventListener('keydown', handleEscape);
        return () => window.removeEventListener('keydown', handleEscape);
    }, [isOpen, isSubmitting]);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) {
            setError('Please enter a message');
            return;
        }
        
        setIsSubmitting(true);
        setError(null);
        try {
            await onSubmit(type, message.trim());
            setIsSuccess(true);
            // Auto close after success
            setTimeout(() => {
                setMessage('');
                setType('feature');
                setIsSuccess(false);
                onClose();
            }, 1500);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to submit feedback. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        if (!isSubmitting) {
            setMessage('');
            setType('feature');
            setError(null);
            setIsSuccess(false);
            onClose();
        }
    };

    const selectedType = feedbackTypes.find(t => t.value === type);

    const modalContent = (
        <div 
            className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
            role="dialog"
            aria-modal="true"
            aria-labelledby="feedback-modal-title"
        >
            {/* Backdrop - covers everything */}
            <div 
                className="fixed inset-0 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200" 
                onClick={handleClose}
                aria-hidden="true"
            />
            
            {/* Modal Container */}
            <div className="relative w-full max-w-lg animate-in zoom-in-95 fade-in duration-200">
                {/* Success State */}
                {isSuccess ? (
                    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 p-8 text-center">
                        <div className="size-16 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                            <span className="material-symbols-outlined text-green-600 dark:text-green-400 text-3xl">check_circle</span>
                        </div>
                        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Thank you!</h3>
                        <p className="text-slate-600 dark:text-slate-400">Your feedback has been submitted successfully.</p>
                    </div>
                ) : (
                    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                        {/* Header */}
                        <div className="relative px-6 pt-6 pb-4">
                            <button
                                onClick={handleClose}
                                disabled={isSubmitting}
                                className="absolute right-4 top-4 size-8 flex items-center justify-center rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                                aria-label="Close"
                            >
                                <span className="material-symbols-outlined text-[20px]">close</span>
                            </button>
                            
                            <div className="flex items-center gap-3">
                                <div className="size-10 bg-primary/10 rounded-xl flex items-center justify-center">
                                    <span className="material-symbols-outlined text-primary">feedback</span>
                                </div>
                                <div>
                                    <h2 id="feedback-modal-title" className="text-lg font-bold text-slate-900 dark:text-white">
                                        Send Feedback
                                    </h2>
                                    <p className="text-sm text-slate-500 dark:text-slate-400">
                                        Help us improve Dreamware
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Body */}
                        <form onSubmit={handleSubmit} className="px-6 pb-6 space-y-5">
                            {/* Type Selection */}
                            <div className="space-y-3">
                                <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                                    What type of feedback?
                                </label>
                                <div className="grid grid-cols-3 gap-3">
                                    {feedbackTypes.map((t) => (
                                        <button
                                            key={t.value}
                                            type="button"
                                            onClick={() => setType(t.value)}
                                            className={`relative p-4 rounded-xl text-center transition-all border-2 ${
                                                type === t.value
                                                    ? 'bg-primary/5 border-primary ring-2 ring-primary/20'
                                                    : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                                            }`}
                                        >
                                            <span className="text-2xl block mb-1">{t.icon}</span>
                                            <span className={`text-sm font-medium block ${
                                                type === t.value 
                                                    ? 'text-primary' 
                                                    : 'text-slate-600 dark:text-slate-300'
                                            }`}>
                                                {t.label.split(' ')[0]}
                                            </span>
                                            {type === t.value && (
                                                <span className="absolute -top-1 -right-1 size-5 bg-primary rounded-full flex items-center justify-center">
                                                    <span className="material-symbols-outlined text-white text-xs">check</span>
                                                </span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                                {selectedType && (
                                    <p className="text-xs text-slate-500 dark:text-slate-400 text-center">
                                        {selectedType.description}
                                    </p>
                                )}
                            </div>

                            {/* Message */}
                            <div className="space-y-2">
                                <label htmlFor="feedback-message" className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                                    Your message
                                </label>
                                <textarea
                                    id="feedback-message"
                                    value={message}
                                    onChange={(e) => {
                                        setMessage(e.target.value);
                                        if (error) setError(null);
                                    }}
                                    placeholder={
                                        type === 'feature' 
                                            ? "Describe the feature you'd like to see..."
                                            : type === 'bug'
                                            ? "Describe what happened and what you expected..."
                                            : "Tell us what's on your mind..."
                                    }
                                    rows={4}
                                    className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-primary focus:bg-white dark:focus:bg-slate-800 transition-all resize-none"
                                    disabled={isSubmitting}
                                    autoFocus
                                />
                                <div className="flex justify-between items-center">
                                    <span className={`text-xs ${message.length > 1000 ? 'text-red-500' : 'text-slate-400'}`}>
                                        {message.length}/1000
                                    </span>
                                </div>
                            </div>

                            {/* Error */}
                            {error && (
                                <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                                    <span className="material-symbols-outlined text-red-500 text-lg">error</span>
                                    <p className="text-sm text-red-600 dark:text-red-400 font-medium">{error}</p>
                                </div>
                            )}

                            {/* Actions */}
                            <div className="flex gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={handleClose}
                                    disabled={isSubmitting}
                                    className="flex-1 py-3 px-4 rounded-xl border-2 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-semibold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSubmitting || !message.trim() || message.length > 1000}
                                    className="flex-1 py-3 px-4 rounded-xl bg-primary hover:bg-primary-dark text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-primary/20 hover:shadow-primary/30"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <div className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            Sending...
                                        </>
                                    ) : (
                                        <>
                                            <span className="material-symbols-outlined text-[18px]">send</span>
                                            Submit Feedback
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );

    // Use portal to render modal at document body level
    return createPortal(modalContent, document.body);
}
