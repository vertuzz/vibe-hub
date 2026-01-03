import api from '../api';
import type { Tool, ToolWithCount } from '../types';

export const toolService = {
    getTools: async (): Promise<Tool[]> => {
        const response = await api.get('/tools/');
        return response.data;
    },

    getToolsWithCounts: async (): Promise<ToolWithCount[]> => {
        const response = await api.get('/tools/with-counts');
        return response.data;
    },

    createTool: async (name: string): Promise<Tool> => {
        const response = await api.post('/tools/', { name });
        return response.data;
    },

    updateTool: async (id: number, name: string): Promise<Tool> => {
        const response = await api.put(`/tools/${id}`, { name });
        return response.data;
    },

    deleteTool: async (id: number): Promise<void> => {
        await api.delete(`/tools/${id}`);
    }
};
