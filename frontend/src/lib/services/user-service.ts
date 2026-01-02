import api from '../api';
import type { User } from '../types';

export const userService = {
    getUser: async (id: string | number): Promise<User> => {
        const response = await api.get(`/users/${id}`);
        return response.data;
    },

    followUser: async (userId: number): Promise<{ message: string }> => {
        const response = await api.post(`/users/${userId}/follow`);
        return response.data;
    },

    unfollowUser: async (userId: number): Promise<{ message: string }> => {
        const response = await api.delete(`/users/${userId}/follow`);
        return response.data;
    },

    checkFollowStatus: async (userId: number): Promise<{ is_following: boolean }> => {
        const response = await api.get(`/users/${userId}/follow/status`);
        return response.data;
    },
};
