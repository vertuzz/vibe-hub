import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { App } from '~/lib/types';
import { useAuth } from '~/contexts/AuthContext';
import { userService } from '~/lib/services/user-service';

interface AppActionPanelProps {
    app: App;
    likesCount: number;
    isLiked: boolean;
    onLike: () => void;
    onShare: () => void;
    onDelete: () => void;
    onClaim: () => void;
}

const statusConfig = {
    Live: {
        bg: 'bg-emerald-50 dark:bg-emerald-900/20',
        border: 'border-emerald-100 dark:border-emerald-900/50',
        text: 'text-emerald-700 dark:text-emerald-400',
        dot: 'bg-emerald-500',
        label: 'Live'
    },
    WIP: {
        bg: 'bg-amber-50 dark:bg-amber-900/20',
        border: 'border-amber-100 dark:border-amber-900/50',
        text: 'text-amber-700 dark:text-amber-400',
        dot: 'bg-amber-500',
        label: 'Work in Progress'
    },
    Concept: {
        bg: 'bg-blue-50 dark:bg-blue-900/20',
        border: 'border-blue-100 dark:border-blue-900/50',
        text: 'text-blue-700 dark:text-blue-400',
        dot: 'bg-blue-500',
        label: 'Concept'
    },
};

export default function AppActionPanel({
    app,
    likesCount,
    isLiked,
    onLike,
    onShare,
    onDelete,
    onClaim
}: AppActionPanelProps) {
    const { user, isAuthenticated } = useAuth();
    const isOwner = user?.id === app.creator_id;
    const status = statusConfig[app.status] || statusConfig.Concept;

    // Follow state
    const [isFollowing, setIsFollowing] = useState(false);
    const [followLoading, setFollowLoading] = useState(false);

    // Check follow status on mount
    useEffect(() => {
        const fetchFollowStatus = async () => {
            if (!app.creator?.id || !isAuthenticated || app.creator.id === user?.id) return;
            try {
                const status = await userService.checkFollowStatus(app.creator.id);
                setIsFollowing(status.is_following);
            } catch (err) {
                console.error('Failed to fetch follow status:', err);
            }
        };
        fetchFollowStatus();
    }, [app.creator?.id, isAuthenticated, user?.id]);

    const handleFollowClick = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!app.creator?.id || !isAuthenticated) return;

        setFollowLoading(true);
        try {
            if (isFollowing) {
                await userService.unfollowUser(app.creator.id);
                setIsFollowing(false);
            } else {
                await userService.followUser(app.creator.id);
                setIsFollowing(true);
            }
        } catch (err) {
            console.error('Failed to update follow status:', err);
        } finally {
            setFollowLoading(false);
        }
    };

    return (
        <div className="sticky top-24 space-y-6">
            {/* Main Action Card */}
            <div className="bg-white dark:bg-[var(--card)] rounded-2xl p-6 shadow-lg border border-[var(--border)] flex flex-col gap-6">
                {/* Status */}
                <div className="flex items-center justify-between">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${status.bg} border ${status.border}`}>
                        <span className="relative flex h-2.5 w-2.5">
                            {app.status === 'Live' && (
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${status.dot} opacity-75`} />
                            )}
                            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${status.dot}`} />
                        </span>
                        <span className={`text-xs font-bold ${status.text} uppercase tracking-wide`}>{status.label}</span>
                    </div>

                    {isOwner && (
                        <div className="flex items-center gap-2">
                            <Link
                                to={`/apps/${app.slug}/edit`}
                                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors"
                                title="Edit App"
                            >
                                <span className="material-symbols-outlined text-[20px]">edit</span>
                            </Link>
                            <button
                                onClick={onDelete}
                                className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-500 hover:text-red-600 transition-colors"
                                title="Delete App"
                            >
                                <span className="material-symbols-outlined text-[20px]">delete</span>
                            </button>
                        </div>
                    )}
                </div>

                {/* CTA */}
                {app.app_url ? (
                    <a
                        href={app.app_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-br from-blue-600 to-primary p-4 shadow-xl shadow-blue-500/30 transition-all hover:shadow-blue-500/50 hover:scale-[1.02] block"
                    >
                        <div className="relative z-10 flex items-center justify-center gap-2 text-white font-bold text-lg">
                            <span>Try It Now</span>
                            <span className="material-symbols-outlined">rocket_launch</span>
                        </div>
                    </a>
                ) : (
                    <div className="w-full rounded-xl bg-gray-100 dark:bg-gray-800 p-4 text-center">
                        <span className="text-gray-500 font-medium">No live app yet</span>
                    </div>
                )}

                {/* Claim Ownership */}
                {!app.is_owner && !isOwner && isAuthenticated && (
                    <button
                        onClick={onClaim}
                        className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl border-2 border-dashed border-primary/30 text-primary font-bold text-sm hover:border-primary/60 hover:bg-primary/5 transition-all"
                    >
                        <span className="material-symbols-outlined text-[20px]">verified_user</span>
                        <span>Claim Ownership</span>
                    </button>
                )}

                {/* Secondary Actions */}
                <div className="grid grid-cols-2 gap-3">
                    <button
                        onClick={onLike}
                        className={`flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border transition-colors font-medium text-sm ${isLiked
                            ? 'border-rose-200 bg-rose-50 text-rose-600 dark:border-rose-900 dark:bg-rose-900/20 dark:text-rose-400'
                            : 'border-[var(--border)] bg-transparent text-[var(--foreground)] hover:bg-gray-50 dark:hover:bg-gray-800'
                            }`}
                    >
                        <span className={`material-symbols-outlined text-rose-500 ${isLiked ? 'filled' : ''}`}>favorite</span>
                        {likesCount.toLocaleString()} {likesCount === 1 ? 'Like' : 'Likes'}
                    </button>
                    <button
                        onClick={onShare}
                        className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl border border-[var(--border)] bg-transparent text-[var(--foreground)] hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium text-sm"
                    >
                        <span className="material-symbols-outlined text-gray-500">share</span>
                        Share
                    </button>
                </div>

                <div className="h-px w-full bg-[var(--border)]" />

                {/* Creator Mini Profile */}
                {app.creator && (
                    <Link to={`/users/${app.creator.username}`} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                        <div className="size-12 rounded-full border-2 border-white dark:border-gray-700 shadow-sm overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                            {app.creator.avatar ? (
                                <img src={app.creator.avatar} alt={app.creator.username} className="w-full h-full object-cover" />
                            ) : (
                                <span className="text-lg font-bold text-gray-500">{app.creator.username.charAt(0).toUpperCase()}</span>
                            )}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs text-gray-500 dark:text-gray-400">Created by</p>
                            <p className="font-bold text-[var(--foreground)] truncate">@{app.creator.username}</p>
                        </div>
                        <button
                            onClick={handleFollowClick}
                            disabled={followLoading || !isAuthenticated || app.creator.id === user?.id}
                            className={`text-xs font-bold transition-colors ${isFollowing
                                ? 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
                                : 'text-primary hover:text-primary-dark dark:text-blue-400 dark:hover:text-blue-300'
                                } ${(!isAuthenticated || app.creator.id === user?.id) ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            {followLoading ? '...' : isFollowing ? 'Following' : 'Follow'}
                        </button>
                    </Link>
                )}
            </div>

            {/* Related Info / Tags */}
            {app.tags && app.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {app.tags.map((tag) => (
                        <Link
                            key={tag.id}
                            to={`/?tag_id=${tag.id}`}
                            className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-xs font-medium text-gray-500 dark:text-gray-400 hover:bg-primary/10 hover:text-primary transition-colors"
                        >
                            #{tag.name}
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
