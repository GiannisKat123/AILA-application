type UserProfile = {
    username: string;
    email: string;
    verified: boolean | null;
    role: string;
}

type Message = {
    id: string;
    message: string;
    timestamp: string;
    role: string;
    feedback: boolean | undefined;
}

type MessageCreation = {
    message: string;
    timestamp: string;
    role: string;
    feedback: boolean | undefined;
}

type LoginAPIOutput = {
    user_details: UserProfile;
}

type Conversation = {
    conversation_name: string;
    conversation_id: string;
    conversation_type: string;
}

type ErrorMessage = {
    error_message: string;
}

type messageFeedbackDetails = {
    fileDoc: File | null;
    message_id: string;
    conversation_id: string;
    query_id: string;
    generated_answer_id: string;
    theme: string;
    context: string;
    generalFeedback: string;

}

export type { messageFeedbackDetails, UserProfile, Message, MessageCreation, LoginAPIOutput, Conversation, ErrorMessage }