import api from '../api';
import type { User } from '../types';

export const authService = {
    getMe: async (): Promise<User> => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    googleLogin: async (code: string) => {
        const redirectUri = `${window.location.origin}/auth/callback`;
        const response = await api.post('/auth/google', { code, redirect_uri: redirectUri });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    githubLogin: async (code: string) => {
        const response = await api.post('/auth/github', { code });
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('token');
    },
};
