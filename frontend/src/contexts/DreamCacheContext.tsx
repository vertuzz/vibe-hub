import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Dream } from '~/lib/types';

interface DreamCacheState {
    dreams: Dream[];
    page: number;
    hasMore: boolean;
    scrollPosition: number;
    paramsKey: string; // Unique key to validate cache (serialized URL params)
}

interface DreamCacheContextType {
    cache: DreamCacheState | null;
    saveCache: (state: DreamCacheState) => void;
    loadCache: (currentParamsKey: string) => DreamCacheState | null;
    clearCache: () => void;
}

const DreamCacheContext = createContext<DreamCacheContextType | undefined>(undefined);

export function DreamCacheProvider({ children }: { children: ReactNode }) {
    const [cache, setCache] = useState<DreamCacheState | null>(null);

    const saveCache = useCallback((state: DreamCacheState) => {
        setCache(state);
    }, []);

    const loadCache = useCallback((currentParamsKey: string): DreamCacheState | null => {
        if (cache && cache.paramsKey === currentParamsKey) {
            return cache;
        }
        return null;
    }, [cache]);

    const clearCache = useCallback(() => {
        setCache(null);
    }, []);

    return (
        <DreamCacheContext.Provider value={{ cache, saveCache, loadCache, clearCache }}>
            {children}
        </DreamCacheContext.Provider>
    );
}

export function useDreamCache() {
    const context = useContext(DreamCacheContext);
    if (context === undefined) {
        throw new Error('useDreamCache must be used within a DreamCacheProvider');
    }
    return context;
}
