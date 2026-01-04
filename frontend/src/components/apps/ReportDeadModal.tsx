import React, { useState } from 'react';
import { appService } from '~/lib/services/app-service';

interface ReportDeadModalProps {
    isOpen: boolean;
    onClose: () => void;
    appId: number;
    appTitle: string;
    onSuccess: () => void;
}

const ReportDeadModal: React.FC<ReportDeadModalProps> = ({
    isOpen,
    onClose,
    appId,
    appTitle,
    onSuccess
}) => {
    const [reason, setReason] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError(null);

        try {
            await appService.reportDeadApp(appId, { reason: reason || undefined });
            onSuccess();
            onClose();
        } catch (err: any) {
            console.error('Failed to submit report:', err);
            setError(err.response?.data?.detail || 'Failed to submit report. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="bg-white dark:bg-[var(--card)] w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border border-[var(--border)] animate-in fade-in zoom-in duration-200">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                            <span className="material-symbols-outlined text-amber-500">flag</span>
                            Report Dead Link
                        </h3>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors"
                        >
                            <span className="material-symbols-outlined">close</span>
                        </button>
                    </div>

                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 font-medium">
                        Is the link for <span className="text-slate-900 dark:text-white font-bold">"{appTitle}"</span> no longer working?
                        Help the community by reporting it. An admin will review and verify.
                    </p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                                Reason (Optional)
                            </label>
                            <textarea
                                value={reason}
                                onChange={(e) => setReason(e.target.value)}
                                className="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-gray-50 dark:bg-gray-800/50 focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none transition-all min-h-[100px] text-sm"
                                placeholder="E.g., Returns 404 error, domain expired, page shows error message..."
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
                                className="flex-1 px-4 py-3 rounded-xl bg-amber-500 text-white font-bold shadow-lg shadow-amber-500/20 hover:shadow-amber-500/40 hover:bg-amber-600 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
                            >
                                {isSubmitting ? (
                                    <>
                                        <div className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        <span>Submitting...</span>
                                    </>
                                ) : (
                                    <span>Submit Report</span>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ReportDeadModal;
