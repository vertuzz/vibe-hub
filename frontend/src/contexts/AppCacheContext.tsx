import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { App } from '~/lib/types';

interface AppCacheState {
    apps: App[];
    page: number;
    hasMore: boolean;
    scrollPosition: number;
    paramsKey: string; // Unique key to validate cache (serialized URL params)
}

interface AppCacheContextType {
    cache: AppCacheState | null;
    saveCache: (state: AppCacheState) => void;
    loadCache: (currentParamsKey: string) => AppCacheState | null;
    clearCache: () => void;
}

const AppCacheContext = createContext<AppCacheContextType | undefined>(undefined);

export function AppCacheProvider({ children }: { children: ReactNode }) {
    const [cache, setCache] = useState<AppCacheState | null>(null);

    const saveCache = useCallback((state: AppCacheState) => {
        setCache(state);
    }, []);

    const loadCache = useCallback((currentParamsKey: string): AppCacheState | null => {
        if (cache && cache.paramsKey === currentParamsKey) {
            return cache;
        }
        return null;
    }, [cache]);

    const clearCache = useCallback(() => {
        setCache(null);
    }, []);

    return (
        <AppCacheContext.Provider value={{ cache, saveCache, loadCache, clearCache }}>
            {children}
        </AppCacheContext.Provider>
    );
}

export function useAppCache() {
    const context = useContext(AppCacheContext);
    if (context === undefined) {
        throw new Error('useAppCache must be used within a AppCacheProvider');
    }
    return context;
}
