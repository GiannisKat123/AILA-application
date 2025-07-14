export type UserProfile = {
    username: string;
    email: string;
    verified: boolean | null;
}

export type Message = {
    feedback: boolean | null;
    id: string;
    message: string;
    timestamp: string;
    role: string
}

export type LoginAPIOutput = {
    user_details: UserProfile;
}

export type Conversations = {
    conversation_name: string;
    conversation_id: string;
}

export type ErrorMessage = {
   error_message: string;
}