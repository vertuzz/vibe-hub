export interface User {
    id: number;
    username: string;
    email?: string;
    full_name?: string;
    is_active: boolean;
    profile_image_url?: string;
    bio?: string;
}

export interface Dream {
    id: number;
    title: string;
    prompt_text?: string;
    prd_text?: string;
    extra_specs?: any;
    status: string;
    app_url?: string;
    youtube_url?: string;
    is_agent_submitted: boolean;
    creator_id: number;
    created_at: string;
    updated_at: string;
    tools?: Tool[];
    tags?: Tag[];
    media?: DreamMedia[];
}

export interface Tool {
    id: number;
    name: string;
    description?: string;
    website_url?: string;
    logo_url?: string;
}

export interface Tag {
    id: number;
    name: string;
}

export interface DreamMedia {
    id: number;
    dream_id: number;
    media_type: string;
    url: string;
    caption?: string;
}

export interface DreamCreate {
    title: string;
    prompt_text?: string;
    prd_text?: string;
    extra_specs?: any;
    status?: string;
    app_url?: string;
    youtube_url?: string;
    is_agent_submitted?: boolean;
    tool_ids?: number[];
    tag_ids?: number[];
}
