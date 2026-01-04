export interface UserLink {
    id: number;
    user_id: number;
    label: string;
    url: string;
}

export interface User {
    id: number;
    username: string;
    email?: string;
    full_name?: string;
    bio?: string;
    location?: string;
    is_active: boolean;
    profile_image_url?: string;
    avatar?: string;
    reputation_score?: number;
    api_key?: string;
    is_admin?: boolean;
    links?: UserLink[];
}

export interface UserUpdate {
    username?: string;
    email?: string;
    avatar?: string;
    full_name?: string;
    bio?: string;
    location?: string;
}

export interface AppCreator {
    id: number;
    username: string;
    avatar?: string;
}

export interface App {
    id: number;
    slug: string;
    title: string;
    prompt_text?: string;
    prd_text?: string;
    extra_specs?: any;
    status: 'Concept' | 'WIP' | 'Live';
    app_url?: string;
    youtube_url?: string;
    is_agent_submitted: boolean;
    is_owner: boolean;
    is_dead: boolean;
    creator_id: number;
    creator?: AppCreator;
    created_at: string;
    updated_at?: string;
    tools?: Tool[];
    tags?: Tag[];
    media?: AppMedia[];
    likes_count?: number;
    comments_count?: number;
    is_liked?: boolean;
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

export interface TagWithCount extends Tag {
    app_count: number;
}

export interface ToolWithCount extends Tool {
    app_count: number;
}

export interface AppMedia {
    id: number;
    app_id: number;
    media_url: string;
}

export interface AppCreate {
    title: string;
    prompt_text?: string;
    prd_text?: string;
    extra_specs?: any;
    status?: string;
    app_url?: string;
    youtube_url?: string;
    is_agent_submitted?: boolean;
    is_owner?: boolean;
    tool_ids?: number[];
    tag_ids?: number[];
}

export interface OwnershipClaim {
    id: number;
    app_id: number;
    claimant_id: number;
    message?: string;
    status: 'pending' | 'approved' | 'rejected';
    created_at: string;
    resolved_at?: string;
    claimant?: AppCreator;
    app?: App;
}

export interface Comment {
    id: number;
    app_id: number;
    user_id: number;
    content: string;
    created_at: string;
    score: number;
    user_vote?: number; // 1, -1, 0
    parent_id?: number | null;
    user?: {
        id: number;
        username: string;
        avatar?: string;
    };
}

export interface CommentCreate {
    content: string;
    parent_id?: number;
}

export interface Notification {
    id: number;
    user_id: number;
    type: string;
    content: string;
    link?: string;
    is_read: boolean;
    created_at: string;
}

export type FeedbackType = 'bug' | 'feature' | 'other';

export interface Feedback {
    id: number;
    user_id: number;
    type: FeedbackType;
    message: string;
    created_at: string;
    user?: {
        id: number;
        username: string;
        avatar?: string;
    };
}

export interface FeedbackCreate {
    type: FeedbackType;
    message: string;
}

// Dead App Report types
export type ReportStatus = 'pending' | 'confirmed' | 'dismissed';

export interface DeadAppReport {
    id: number;
    app_id: number;
    reporter_id: number;
    reason?: string;
    status: ReportStatus;
    created_at: string;
    resolved_at?: string;
    reporter?: AppCreator;
    app?: App;
    report_count?: number;
}

export interface DeadAppReportCreate {
    reason?: string;
}

export interface DeadAppReportResolve {
    status: 'confirmed' | 'dismissed';
}
