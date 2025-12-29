import { useEffect, useState, useCallback } from 'react';
import { dreamService, type DreamQueryParams } from '~/lib/services/dream-service';
import type { Dream } from '~/lib/types';
import DreamCard from '~/components/dreams/DreamCard';
import DreamCardSkeleton from '~/components/dreams/DreamCardSkeleton';
import Header from '~/components/layout/Header';

type FilterCategory = 'all' | 'agents' | 'components' | 'apps' | 'games';
type SortOption = 'trending' | 'newest' | 'top_rated' | 'likes';

// Map aspect ratios for masonry variety
const aspectRatios: Array<'square' | 'video' | 'portrait' | 'landscape'> = [
    'landscape',
    'portrait',
    'video',
    'landscape',
    'square',
    'landscape',
    'portrait',
    'landscape',
];

export default function Home() {
    const [dreams, setDreams] = useState<Dream[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeFilter, setActiveFilter] = useState<FilterCategory>('all');
    const [sortBy, setSortBy] = useState<SortOption>('trending');
    const [searchQuery, setSearchQuery] = useState('');
    const [page, setPage] = useState(1);
    const [showSortDropdown, setShowSortDropdown] = useState(false);
    const itemsPerPage = 20;

    const fetchDreams = useCallback(async () => {
        setLoading(true);
        try {
            const params: DreamQueryParams = {
                skip: (page - 1) * itemsPerPage,
                limit: itemsPerPage,
                sort_by: sortBy,
            };

            // Add search if present
            if (searchQuery) {
                params.search = searchQuery;
            }

            // Add tag filter based on category
            if (activeFilter !== 'all') {
                const tagMap: Record<FilterCategory, string> = {
                    all: '',
                    agents: 'agent',
                    components: 'ui-component',
                    apps: 'full-app',
                    games: 'game',
                };
                params.tag = tagMap[activeFilter];
            }

            const data = await dreamService.getDreams(params);
            setDreams(data);
        } catch (err) {
            console.error('Failed to fetch dreams:', err);
        } finally {
            setLoading(false);
        }
    }, [page, sortBy, activeFilter, searchQuery]);

    useEffect(() => {
        fetchDreams();
    }, [fetchDreams]);

    // Debounced search handler
    useEffect(() => {
        const timer = setTimeout(() => {
            if (searchQuery !== '') {
                setPage(1);
                fetchDreams();
            }
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const handleFilterChange = (filter: FilterCategory) => {
        setActiveFilter(filter);
        setPage(1);
    };

    const handleSortChange = (sort: SortOption) => {
        setSortBy(sort);
        setPage(1);
        setShowSortDropdown(false);
    };

    const sortLabels: Record<SortOption, string> = {
        trending: 'Trending',
        newest: 'Newest',
        top_rated: 'Top Rated',
        likes: 'Most Liked',
    };

    const filterButtons: { key: FilterCategory; label: string; icon: string }[] = [
        { key: 'all', label: 'All', icon: '' },
        { key: 'agents', label: 'Agents', icon: 'smart_toy' },
        { key: 'components', label: 'UI Components', icon: 'view_quilt' },
        { key: 'apps', label: 'Full Apps', icon: 'web_asset' },
        { key: 'games', label: 'Games', icon: 'stadia_controller' },
    ];

    return (
        <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden">
            {/* Header */}
            <Header onSearch={setSearchQuery} />

            {/* Main Content */}
            <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 md:px-10 py-8">
                {/* Hero Headline */}
                <div className="flex flex-col items-center justify-center text-center pb-10 pt-4 max-w-3xl mx-auto">
                    <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-[#0d111b] dark:text-white mb-3">
                        Discover the future of{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-500">
                            AI applications
                        </span>
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 text-lg">
                        Browse thousands of community-generated agents, UI components, and full-stack dreams.
                    </p>
                </div>

                {/* Filters & Sort */}
                <div className="sticky top-[72px] z-40 bg-[var(--background)]/95 backdrop-blur-sm py-4 mb-8 flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-gray-200 dark:border-gray-800">
                    {/* Filter Chips */}
                    <div className="w-full sm:w-auto overflow-x-auto pb-2 sm:pb-0 scrollbar-hide">
                        <div className="flex gap-3">
                            {filterButtons.map((btn) => (
                                <button
                                    key={btn.key}
                                    onClick={() => handleFilterChange(btn.key)}
                                    className={`flex h-9 items-center justify-center gap-2 rounded-full px-5 whitespace-nowrap transition-all ${
                                        activeFilter === btn.key
                                            ? 'bg-primary text-white shadow-sm hover:bg-primary-dark'
                                            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700 shadow-sm hover:border-primary hover:text-primary'
                                    }`}
                                >
                                    {btn.icon && (
                                        <span className="material-symbols-outlined text-[18px]">{btn.icon}</span>
                                    )}
                                    <span className="text-sm font-medium">{btn.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Sort Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowSortDropdown(!showSortDropdown)}
                            className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 hover:text-primary transition-colors whitespace-nowrap"
                        >
                            <span className="material-symbols-outlined">sort</span>
                            <span>Sort by: {sortLabels[sortBy]}</span>
                            <span className="material-symbols-outlined text-[18px]">keyboard_arrow_down</span>
                        </button>

                        {showSortDropdown && (
                            <div className="absolute right-0 top-full mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 min-w-[160px] z-50">
                                {(Object.keys(sortLabels) as SortOption[]).map((option) => (
                                    <button
                                        key={option}
                                        onClick={() => handleSortChange(option)}
                                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                                            sortBy === option
                                                ? 'text-primary font-semibold'
                                                : 'text-gray-700 dark:text-gray-300'
                                        }`}
                                    >
                                        {sortLabels[option]}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="masonry-grid pb-12">
                        {Array.from({ length: 8 }).map((_, index) => (
                            <DreamCardSkeleton key={index} />
                        ))}
                    </div>
                )}

                {/* Empty State */}
                {!loading && dreams.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <span className="material-symbols-outlined text-6xl text-gray-300 mb-4">
                            lightbulb
                        </span>
                        <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            No dreams found
                        </h3>
                        <p className="text-gray-500 dark:text-gray-400 max-w-md">
                            {searchQuery
                                ? `No results for "${searchQuery}". Try a different search term.`
                                : 'Be the first to submit a dream and share your AI creation with the community!'}
                        </p>
                    </div>
                )}

                {/* Masonry Grid */}
                {!loading && dreams.length > 0 && (
                    <div className="masonry-grid pb-12">
                        {dreams.map((dream, index) => (
                            <DreamCard
                                key={dream.id}
                                dream={dream}
                                aspectRatio={aspectRatios[index % aspectRatios.length]}
                            />
                        ))}
                    </div>
                )}

                {/* Pagination */}
                {!loading && dreams.length > 0 && (
                    <div className="flex items-center justify-center pt-8 pb-12">
                        <nav className="flex items-center gap-2">
                            <button
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="flex items-center justify-center size-10 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <span className="material-symbols-outlined text-[20px]">chevron_left</span>
                            </button>

                            {[1, 2, 3].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setPage(p)}
                                    className={`flex items-center justify-center size-10 rounded-full text-sm font-medium transition-colors ${
                                        page === p
                                            ? 'bg-primary text-white shadow-md shadow-primary/30 font-bold'
                                            : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400'
                                    }`}
                                >
                                    {p}
                                </button>
                            ))}

                            <span className="flex items-center justify-center size-10 text-gray-400 pb-2">...</span>

                            <button
                                onClick={() => setPage(12)}
                                className="flex items-center justify-center size-10 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 text-sm font-medium transition-colors"
                            >
                                12
                            </button>

                            <button
                                onClick={() => setPage((p) => p + 1)}
                                className="flex items-center justify-center size-10 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 transition-colors"
                            >
                                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
                            </button>
                        </nav>
                    </div>
                )}
            </main>
        </div>
    );
}
