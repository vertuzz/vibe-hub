

interface DeleteConfirmModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title?: string;
    message?: string;
    confirmLabel?: string;
    isDeleting?: boolean;
}

export default function DeleteConfirmModal({
    isOpen,
    onClose,
    onConfirm,
    title = 'Delete App',
    message = 'Are you sure you want to delete this app? This action cannot be undone.',
    confirmLabel = 'Delete',
    isDeleting = false,
}: DeleteConfirmModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className="relative w-full max-w-md bg-white dark:bg-[var(--card)] rounded-2xl p-8 shadow-2xl border border-[var(--border)] transform transition-all animate-in fade-in zoom-in duration-200">
                <div className="flex flex-col items-center text-center">
                    <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center mb-6">
                        <span className="material-symbols-outlined text-red-600 dark:text-red-400 text-3xl">delete_forever</span>
                    </div>

                    <h3 className="text-2xl font-bold text-[var(--foreground)] mb-3">{title}</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-8 leading-relaxed">
                        {message}
                    </p>

                    <div className="flex items-center gap-4 w-full">
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={isDeleting}
                            className="flex-1 py-3.5 px-6 rounded-xl font-bold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
                        >
                            Cancel
                        </button>
                        <button
                            type="button"
                            onClick={onConfirm}
                            disabled={isDeleting}
                            className="flex-1 py-3.5 px-6 rounded-xl font-bold bg-red-600 text-white shadow-lg shadow-red-600/30 hover:bg-red-700 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                        >
                            {isDeleting ? (
                                <>
                                    <span className="size-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    <span>Deleting...</span>
                                </>
                            ) : (
                                <span>{confirmLabel}</span>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
