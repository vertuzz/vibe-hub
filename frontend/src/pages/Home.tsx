import { useEffect, useState, useCallback, useRef, useLayoutEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { appService, type AppQueryParams } from '~/lib/services/app-service';
import type { App, Tag, Tool } from '~/lib/types';
import AppCard from '~/components/apps/AppCard';
import AppCardSkeleton from '~/components/apps/AppCardSkeleton';
import FilterBar from '~/components/apps/FilterBar';
import Header from '~/components/layout/Header';
import { useAppCache } from '~/contexts/AppCacheContext';
import { useSEO } from '~/lib/hooks/useSEO';

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

// Helper to create a unique key from search params for cache validation
function createParamsKey(params: URLSearchParams): string {
    const sortedParams = new URLSearchParams([...params.entries()].sort());
    return sortedParams.toString();
}

// Helper to parse comma-separated strings/ids from URL
function parseParams(value: string | null): string[] {
    if (!value) return [];
    return value.split(',').filter(Boolean);
}

export default function Home() {
    const [searchParams, setSearchParams] = useSearchParams();
    const { saveCache, loadCache } = useAppCache();

    // SEO - Home page uses default site title
    useSEO({ url: '/' });

    // Initialize state from URL params
    const getInitialTagIds = () => parseParams(searchParams.get('tag_id')).map(Number).filter(n => !isNaN(n));
    const getInitialToolIds = () => parseParams(searchParams.get('tool_id')).map(Number).filter(n => !isNaN(n));
    const getInitialStatuses = () => parseParams(searchParams.get('status')) as App['status'][];
    const getInitialSort = (): SortOption => (searchParams.get('sort_by') as SortOption) || 'trending';
    const getInitialSearch = () => searchParams.get('search') || '';

    const [apps, setApps] = useState<App[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingMore, setLoadingMore] = useState(false);
    const [tags, setTags] = useState<Tag[]>([]);
    const [tools, setTools] = useState<Tool[]>([]);
    const [selectedTagIds, setSelectedTagIds] = useState<number[]>(getInitialTagIds);
    const [selectedToolIds, setSelectedToolIds] = useState<number[]>(getInitialToolIds);
    const [selectedStatuses, setSelectedStatuses] = useState<App['status'][]>(getInitialStatuses);
    const [sortBy, setSortBy] = useState<SortOption>(getInitialSort);
    const [searchQuery, setSearchQuery] = useState(getInitialSearch);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [showSortDropdown, setShowSortDropdown] = useState(false);
    const [cacheRestored, setCacheRestored] = useState(false);
    const [hasMounted, setHasMounted] = useState(false);
    const itemsPerPage = 20;

    // Ref for scroll restoration
    const pendingScrollRestore = useRef<number | null>(null);
    // Track if initial fetch was done by this component instance
    const didInitialFetch = useRef(false);

    const observer = useRef<IntersectionObserver | null>(null);
    const lastAppElementRef = useCallback(
        (node: HTMLDivElement | null) => {
            if (loading || loadingMore) return;
            if (observer.current) observer.current.disconnect();
            observer.current = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting && hasMore) {
                    setPage((prevPage) => prevPage + 1);
                }
            });
            if (node) observer.current.observe(node);
        },
        [loading, loadingMore, hasMore]
    );

    // Sync state to URL params
    useEffect(() => {
        const newParams = new URLSearchParams();
        if (selectedTagIds.length > 0) {
            newParams.set('tag_id', selectedTagIds.join(','));
        }
        if (selectedToolIds.length > 0) {
            newParams.set('tool_id', selectedToolIds.join(','));
        }
        if (selectedStatuses.length > 0) {
            newParams.set('status', selectedStatuses.join(','));
        }
        if (sortBy !== 'trending') {
            newParams.set('sort_by', sortBy);
        }
        if (searchQuery) {
            newParams.set('search', searchQuery);
        }
        setSearchParams(newParams, { replace: true });
    }, [selectedTagIds, selectedToolIds, selectedStatuses, sortBy, searchQuery, setSearchParams]);

    const fetchApps = useCallback(async (isInitial: boolean = false) => {
        if (isInitial) {
            setLoading(true);
        } else {
            setLoadingMore(true);
        }

        try {
            const params: AppQueryParams = {
                skip: ((isInitial ? 1 : page) - 1) * itemsPerPage,
                limit: itemsPerPage,
                sort_by: sortBy,
            };

            // Add search if present
            if (searchQuery) {
                params.search = searchQuery;
            }

            // Add multi-select filters
            if (selectedTagIds.length > 0) {
                params.tag_id = selectedTagIds;
            }
            if (selectedToolIds.length > 0) {
                params.tool_id = selectedToolIds;
            }
            if (selectedStatuses.length > 0) {
                // Backend usually takes single status or we might need to handle multi-status if supported
                // For now backend schemas.py line 68 shows status: Optional[AppStatus]
                // Let's check how backend handles it. 
                // Currently backend only supports single status filter in get_apps.
                // We'll just take the first one or pass as list if backend updated.
                // Looking at apps.py:115: if status: query = query.filter(App.status == status)
                // It only supports one. Let's send the first one or we can update backend.
                // For now, let's keep it consistent with what backend supports.
                params.status = selectedStatuses[0];
            }

            const data = await appService.getApps(params);

            if (isInitial) {
                setApps(data);
            } else {
                setApps((prev) => [...prev, ...data]);
            }

            setHasMore(data.length === itemsPerPage);
        } catch (err) {
            console.error('Failed to fetch apps:', err);
        } finally {
            setLoading(false);
            setLoadingMore(false);
        }
    }, [page, sortBy, selectedTagIds, selectedToolIds, selectedStatuses, searchQuery]);

    // Load filter data (tags, tools) on mount - service handles caching/deduplication
    useEffect(() => {
        const loadInitialData = async () => {
            try {
                const [tagsData, toolsData] = await Promise.all([
                    appService.getTags(),
                    appService.getTools()
                ]);
                setTags(tagsData);
                setTools(toolsData);
            } catch (err) {
                console.error('Failed to fetch filter data:', err);
            }
        };
        loadInitialData();
    }, []);

    // Check cache on mount and restore if valid - this is the ONLY place that triggers initial fetch
    useEffect(() => {
        if (didInitialFetch.current) return;
        didInitialFetch.current = true;

        const paramsKey = createParamsKey(searchParams);
        const cached = loadCache(paramsKey);

        if (cached) {
            setApps(cached.apps);
            setPage(cached.page);
            setHasMore(cached.hasMore);
            pendingScrollRestore.current = cached.scrollPosition;
            setLoading(false);
            setCacheRestored(true);
        } else {
            fetchApps(true);
        }

        // Mark as mounted after initial fetch is done
        setHasMounted(true);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Restore scroll position after apps render from cache
    useLayoutEffect(() => {
        if (cacheRestored && pendingScrollRestore.current !== null && apps.length > 0) {
            window.scrollTo(0, pendingScrollRestore.current);
            pendingScrollRestore.current = null;
            setCacheRestored(false);
        }
    }, [cacheRestored, apps]);

    // Filter/sort changes - only trigger AFTER mount (not on initial render)
    useEffect(() => {
        // Skip on initial mount or when cache was just restored
        if (!hasMounted || cacheRestored) return;

        setPage(1);
        setHasMore(true);
        fetchApps(true);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [sortBy, selectedTagIds, selectedToolIds, selectedStatuses]);

    // Fetch more when page changes (infinite scroll)
    useEffect(() => {
        if (page > 1) {
            fetchApps(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page]);

    // Debounced search handler - only trigger AFTER mount
    const prevSearchQuery = useRef(searchQuery);
    useEffect(() => {
        // Skip on initial mount or if cache was restored
        if (!hasMounted || cacheRestored) return;
        // Skip if search query hasn't actually changed
        if (prevSearchQuery.current === searchQuery) return;
        prevSearchQuery.current = searchQuery;

        const timer = setTimeout(() => {
            setPage(1);
            setHasMore(true);
            fetchApps(true);
        }, 300);
        return () => clearTimeout(timer);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchQuery, hasMounted]);

    // Save cache on unmount
    useEffect(() => {
        return () => {
            const paramsKey = createParamsKey(new URLSearchParams(window.location.search));
            saveCache({
                apps,
                page,
                hasMore,
                scrollPosition: window.scrollY,
                paramsKey,
            });
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [apps, page, hasMore, saveCache]);

    const handleFilterChange = (selected: { tagIds: number[]; toolIds: number[]; statuses: App['status'][] }) => {
        setCacheRestored(false); // Reset flag so filters work
        setSelectedTagIds(selected.tagIds);
        setSelectedToolIds(selected.toolIds);
        setSelectedStatuses(selected.statuses);
    };

    const handleSortChange = (sort: SortOption) => {
        setCacheRestored(false);
        setSortBy(sort);
        setShowSortDropdown(false);
    };

    const handleSearch = (query: string) => {
        setCacheRestored(false);
        setSearchQuery(query);
    };

    const sortLabels: Record<SortOption, string> = {
        trending: 'Trending',
        newest: 'Newest',
        top_rated: 'Top Rated',
        likes: 'Most Liked',
    };

    const handleLike = async (app: App) => {
        // Optimistic update
        setApps(prev => prev.map(a => {
            if (a.id === app.id) {
                return {
                    ...a,
                    is_liked: !a.is_liked,
                    likes_count: (a.likes_count || 0) + (a.is_liked ? -1 : 1)
                };
            }
            return a;
        }));

        try {
            if (app.is_liked) {
                await appService.unlikeApp(app.id);
            } else {
                await appService.likeApp(app.id);
            }
        } catch (err) {
            console.error('Failed to toggle like:', err);
            // Revert on failure
            setApps(prev => prev.map(a => {
                if (a.id === app.id) {
                    return {
                        ...a,
                        is_liked: app.is_liked,
                        likes_count: app.likes_count
                    };
                }
                return a;
            }));
        }
    };

    return (
        <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden">
            {/* Header */}
            <Header onSearch={handleSearch} />

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
                        Browse thousands of community-generated agents, UI components, and full-stack apps.
                    </p>
                </div>

                {/* Filters & Sort */}
                <div className="sticky top-[72px] z-40 bg-[var(--background)]/95 backdrop-blur-sm py-4 mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 border-b border-gray-200 dark:border-gray-800">
                    <div className="flex items-center gap-3 overflow-x-auto scrollbar-hide pb-1 sm:pb-0 -mx-4 px-4 sm:mx-0 sm:px-0">
                        <FilterBar
                            tags={tags}
                            tools={tools}
                            selectedTagIds={selectedTagIds}
                            selectedToolIds={selectedToolIds}
                            selectedStatuses={selectedStatuses}
                            onChange={handleFilterChange}
                        />

                        {/* Selected chips for quick individual removal */}
                        <div className="hidden md:flex flex-wrap gap-2 overflow-x-auto scrollbar-hide">
                            {selectedStatuses.map(status => (
                                <button
                                    key={`status-${status}`}
                                    onClick={() => {
                                        setCacheRestored(false);
                                        setSelectedStatuses(prev => prev.filter(s => s !== status));
                                    }}
                                    className="inline-flex h-7 items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 text-[12px] font-medium text-primary hover:bg-primary/10 transition-colors"
                                >
                                    <span className="material-symbols-outlined text-[14px]">flag</span>
                                    {status}
                                    <span className="material-symbols-outlined text-[14px]">close</span>
                                </button>
                            ))}
                            {selectedTagIds.map(id => {
                                const tag = tags.find(t => t.id === id);
                                if (!tag) return null;
                                return (
                                    <button
                                        key={`tag-${id}`}
                                        onClick={() => {
                                            setCacheRestored(false);
                                            setSelectedTagIds(prev => prev.filter(tid => tid !== id));
                                        }}
                                        className="inline-flex h-7 items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 text-[12px] font-medium text-primary hover:bg-primary/10 transition-colors"
                                    >
                                        {tag.name}
                                        <span className="material-symbols-outlined text-[14px]">close</span>
                                    </button>
                                );
                            })}
                            {selectedToolIds.map(id => {
                                const tool = tools.find(t => t.id === id);
                                if (!tool) return null;
                                return (
                                    <button
                                        key={`tool-${id}`}
                                        onClick={() => {
                                            setCacheRestored(false);
                                            setSelectedToolIds(prev => prev.filter(tid => tid !== id));
                                        }}
                                        className="inline-flex h-7 items-center gap-1.5 rounded-full border border-purple-200 bg-purple-50 px-3 text-[12px] font-medium text-purple-600 hover:bg-purple-100 transition-colors"
                                    >
                                        {tool.name}
                                        <span className="material-symbols-outlined text-[14px]">close</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Sort Dropdown */}
                    <div className="relative flex-shrink-0 self-end sm:self-auto">
                        <button
                            onClick={() => setShowSortDropdown(!showSortDropdown)}
                            className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 hover:text-primary transition-colors whitespace-nowrap"
                        >
                            <span className="material-symbols-outlined">sort</span>
                            <span>Sort by: {sortLabels[sortBy] || 'Trending'}</span>
                            <span className="material-symbols-outlined text-[18px]">keyboard_arrow_down</span>
                        </button>

                        {showSortDropdown && (
                            <div className="absolute right-0 top-full mt-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-2 min-w-[160px] z-50">
                                {(Object.keys(sortLabels) as SortOption[]).map((option) => (
                                    <button
                                        key={option}
                                        onClick={() => handleSortChange(option)}
                                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${sortBy === option
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

                {/* Empty State */}
                {!loading && apps.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <span className="material-symbols-outlined text-6xl text-gray-300 mb-4">
                            lightbulb
                        </span>
                        <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            No apps found
                        </h3>
                        <p className="text-gray-500 dark:text-gray-400 max-w-md">
                            {searchQuery
                                ? `No results for "${searchQuery}". Try a different search term.`
                                : 'Be the first to submit an app and share your AI creation with the community!'}
                        </p>
                    </div>
                )}

                {/* Masonry Grid */}
                {apps.length > 0 && (
                    <div className="masonry-grid pb-12">
                        {apps.map((app, index) => {
                            if (apps.length === index + 1) {
                                return (
                                    <div ref={lastAppElementRef} key={app.id}>
                                        <AppCard
                                            app={app}
                                            aspectRatio={aspectRatios[index % aspectRatios.length]}
                                            onLike={handleLike}
                                        />
                                    </div>
                                );
                            } else {
                                return (
                                    <AppCard
                                        key={app.id}
                                        app={app}
                                        aspectRatio={aspectRatios[index % aspectRatios.length]}
                                        onLike={handleLike}
                                    />
                                );
                            }
                        })}
                    </div>
                )}

                {/* Loading State */}
                {(loading || loadingMore) && (
                    <div className="masonry-grid pb-12">
                        {Array.from({ length: loading ? 8 : 4 }).map((_, index) => (
                            <AppCardSkeleton key={index} />
                        ))}
                    </div>
                )}

                {/* End of List Message */}
                {!loading && !loadingMore && !hasMore && apps.length > 0 && (
                    <div className="flex items-center justify-center py-10">
                        <p className="text-gray-400 text-sm font-medium">You've reached the end of the universe ✨</p>
                    </div>
                )}
            </main>
        </div>
    );
}
