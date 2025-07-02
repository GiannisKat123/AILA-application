import api from '../api/axios';
import type { LoginAPIOutput, UserProfile, Message } from '../models/Types';

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

const createConversationAPI = async (conversation_name: string, username: string): Promise<string | undefined> => {
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

const createMessageAPI = async (conversation_name: string, text: string, role: string): Promise<Message | undefined> => {
    try {
        const response = await api.post('/new_message', { conversation_name: conversation_name, text: text, role: role }, { withCredentials: true });
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

const getConversationsAPI = async (username: string): Promise<string[] | undefined> => {
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


const requestAPI = async (userQuery: string): Promise<string | undefined> => {
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
        if(response){
            return true;
        }
    }
    catch (err) {
        console.error("Logout failed:", err);
        return false;
    }

}

export { loginAPI, getUserMessagesAPI, logoutAPI, requestAPI, verifyUser, createConversationAPI, createMessageAPI, getConversationsAPI };

