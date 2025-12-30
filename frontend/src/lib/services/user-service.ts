import api from '../api';
import type { User } from '../types';

export const userService = {
    getUser: async (id: string | number): Promise<User> => {
        const response = await api.get(`/users/${id}`);
        return response.data;
    },
};
