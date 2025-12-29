import api from '../api';
import type { Dream, DreamCreate } from '../types';

export const dreamService = {
    getDreams: async (params?: any): Promise<Dream[]> => {
        const response = await api.get('/dreams/', { params });
        return response.data;
    },

    getDream: async (id: number): Promise<Dream> => {
        const response = await api.get(`/dreams/${id}`);
        return response.data;
    },

    createDream: async (dream: DreamCreate): Promise<Dream> => {
        const response = await api.post('/dreams/', dream);
        return response.data;
    },

    updateDream: async (id: number, dream: Partial<DreamCreate>): Promise<Dream> => {
        const response = await api.patch(`/dreams/${id}`, dream);
        return response.data;
    },

    forkDream: async (id: number): Promise<Dream> => {
        const response = await api.post(`/dreams/${id}/fork`);
        return response.data;
    },
};
