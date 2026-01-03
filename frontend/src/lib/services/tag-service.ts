import api from '../api';
import type { Tag, TagWithCount } from '../types';

export const tagService = {
    getTags: async (): Promise<Tag[]> => {
        const response = await api.get('/tags/');
        return response.data;
    },

    getTagsWithCounts: async (): Promise<TagWithCount[]> => {
        const response = await api.get('/tags/with-counts');
        return response.data;
    },

    createTag: async (name: string): Promise<Tag> => {
        const response = await api.post('/tags/', { name });
        return response.data;
    },

    updateTag: async (id: number, name: string): Promise<Tag> => {
        const response = await api.put(`/tags/${id}`, { name });
        return response.data;
    },

    deleteTag: async (id: number): Promise<void> => {
        await api.delete(`/tags/${id}`);
    }
};
