import api from '../api';
import type { User } from '../types';

export const authService = {
    login: async (credentials: any) => {
        const response = await api.post('/auth/login', credentials);
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    signup: async (userData: any) => {
        const response = await api.post('/auth/signup', userData);
        return response.data;
    },

    getMe: async (): Promise<User> => {
        const response = await api.get('/users/me');
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('token');
    },
};
