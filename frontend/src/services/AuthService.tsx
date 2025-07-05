import api from '../api/axios';
import type { LoginAPIOutput, UserProfile, Message, Conversations } from '../models/Types';

const loginAPI = async (username: string, password: string): Promise<LoginAPIOutput | undefined> => {
    try {
        const response = await api.post('/login', { username: username, password: password }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const registerAPI = async (username: string, password: string, email: string): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/register', { username: username, password: password, email: email }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const verifyAPI = async (username: string, code: string): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/verify', { username: username, code: code }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const resendCodeAPI = async (username: string, email: string): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/resend-code', { username: username, email: email }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const userFeedbackAPI = async (message_id: string, conversation_id: string, feedback: boolean | undefined): Promise<boolean|undefined> => {
    try {
        await api.post('/user_feedback', { message_id: message_id, conversation_id: conversation_id, feedback: feedback }, { withCredentials: true })
        return true;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const createConversationAPI = async (conversation_name: string, username: string): Promise<Conversations | undefined> => {
    try {
        const response = await api.post('/new_conversation', { conversation_name: conversation_name, username: username }, { withCredentials: true })
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const createMessageAPI = async (conversation_name: string, text: string, role: string, id: string, feedback: boolean | null): Promise<Message | undefined> => {
    console.log({ conversation_name: conversation_name, text: text, role: role, id: id, feedback: feedback })
    try {
        const response = await api.post('/new_message', { conversation_name: conversation_name, text: text, role: role, id: id, feedback: feedback }, { withCredentials: true });
        return response.data
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const getConversationsAPI = async (username: string): Promise<Conversations[] | undefined> => {
    try {
        const response = await api.get('/user_conversations', {
            params: { username },
            withCredentials: true
        });
        return response.data
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const getUserMessagesAPI = async (conversation_name: string): Promise<Message[] | undefined> => {
    const response = await api.get('/messages', {
        params: { conversation_name },
        withCredentials: true
    });
    console.log("Response: ", response.data)
    return response.data;
}

const verifyUser = async (): Promise<UserProfile | undefined> => {
    const response = await api.get('/get_user', { withCredentials: true });
    return response.data;
}


const requestAPI = async (userQuery: string): Promise<boolean | void> => {
    try {
        const response = await api.post('/request', { 'message': userQuery }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (err instanceof Error) {
            console.error(err.message);
        } else {
            console.error(err);
        }
    }
}

const logoutAPI = async (): Promise<boolean | undefined> => {
    try {
        const response = await api.post('/logout')
        if (response) {
            return true;
        }
    }
    catch (err) {
        console.error("Logout failed:", err);
        return false;
    }

}

export { loginAPI, getUserMessagesAPI, userFeedbackAPI, resendCodeAPI, verifyAPI, logoutAPI, registerAPI, requestAPI, verifyUser, createConversationAPI, createMessageAPI, getConversationsAPI };

