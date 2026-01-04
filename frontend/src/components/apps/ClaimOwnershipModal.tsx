import React, { useState } from 'react';
import { appService } from '~/lib/services/app-service';

interface ClaimOwnershipModalProps {
    isOpen: boolean;
    onClose: () => void;
    appId: number;
    appTitle: string;
    onSuccess: () => void;
}

const ClaimOwnershipModal: React.FC<ClaimOwnershipModalProps> = ({
    isOpen,
    onClose,
    appId,
    appTitle,
    onSuccess
}) => {
    const [message, setMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError(null);

        try {
            await appService.claimOwnership(appId, message);
            onSuccess();
            onClose();
        } catch (err: any) {
            console.error('Failed to submit claim:', err);
            setError(err.response?.data?.detail || 'Failed to submit ownership claim. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-white dark:bg-[var(--card)] w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border border-[var(--border)] animate-in fade-in zoom-in duration-200">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-black text-slate-900 dark:text-white">Claim Ownership</h3>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
                        >
                            <span className="material-symbols-outlined">close</span>
                        </button>
                    </div>

                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 font-medium">
                        Are you the real owner of <span className="text-slate-900 dark:text-white font-bold">"{appTitle}"</span>?
                        Please provide some proof (e.g., a link to your website where you mention this project, or a DNS record).
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                                Proof or Message
                            </label>
                            <textarea
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-gray-50 dark:bg-gray-800/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all min-h-[120px] text-sm"
                                placeholder="I am the creator of this app. You can verify this by looking at..."
                                required
                            />
                        </div>

                        {error && (
                            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-xs font-medium flex items-center gap-2">
                                <span className="material-symbols-outlined text-[18px]">error</span>
                                {error}
                            </div>
                        )}

                        <div className="flex gap-3 pt-2">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={isSubmitting}
                                className="flex-1 px-4 py-3 rounded-xl border border-[var(--border)] text-slate-600 dark:text-slate-300 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1 px-4 py-3 rounded-xl bg-primary text-white font-bold shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                            >
                                {isSubmitting ? (
                                    <>
                                        <div className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        <span>Submitting...</span>
                                    </>
                                ) : (
                                    <span>Submit Claim</span>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ClaimOwnershipModal;
