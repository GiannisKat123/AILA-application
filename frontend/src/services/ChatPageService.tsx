import axios from "axios";
import api from "../api/axios";
import type { Conversation, ErrorMessage, Message } from "../models/Types";

const renameConversationAPI = async (username: string, conversation_id: string, conversation_name: string): Promise<boolean | ErrorMessage> => {
    try {
        const response = await api.post('/update_conversation', { username, conversation_id, conversation_name }, { withCredentials: true })
        return response.data;
    } catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            return { error_message: String(err) };
        }
    }
}

const userFeedbackAPI = async (message_id: string, username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined): Promise<boolean | undefined> => {
    try {
        await api.post('/user_feedback', { message_id, username, conversation_id, text, role, feedback }, { withCredentials: true })
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

const createConversationAPI = async (username: string, conversation_name: string, conversation_type: string): Promise<Conversation | undefined> => {
    try {
        console.log(username, conversation_name, conversation_type)
        const response = await api.post('/new_conversation', { username, conversation_name, conversation_type }, { withCredentials: true })
        console.log('createConversationAPI', response.data)
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

const createDocumentFeedbackAPI = async (username: string, query_id: string, negative_answer_id: string, doc_name: string, doc_text: string, context: string, theme: string): Promise<boolean | ErrorMessage> => {
    try {
        console.log(username, query_id, negative_answer_id, doc_name, doc_text, context, theme)
        const response = await api.post('/new_document_feedback', { username, query_id, negative_answer_id, doc_name, doc_text, context, theme }, { withCredentials: true });
        return response.data
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            return { error_message: String(err) };
        }
    }
}

const createMessageAPI = async (username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined): Promise<Message | ErrorMessage> => {
    try {
        const response = await api.post('/new_message', { username, conversation_id, text, role, feedback }, { withCredentials: true })
        return response.data
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            return { error_message: String(err) };
        }
    }
}

const getConversationsAPI = async (username: string): Promise<Conversation[] | undefined> => {
    try {
        const response = await api.get('/conversations', {
            params: { username },
            withCredentials: true,
        });
        console.log("getConversationsAPI", response.data)
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

const getUserMessagesAPI = async (username: string, conversation_id: string): Promise<Message[] | undefined> => {
    try {
        const response = await api.get('/messages', {
            params: { username, conversation_id },
            withCredentials: true
        });
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

const createAutomatedMessageAPI = async (conversation_id: string, conversation_name: string, conversation_type: string): Promise<string | undefined> => {
    try {
        const response = await api.post('/automated_message', { conversation_id: conversation_id, conversation_name: conversation_name, conversation_type: conversation_type }, { withCredentials: true });
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

export { renameConversationAPI, createAutomatedMessageAPI, getUserMessagesAPI, getConversationsAPI, createMessageAPI, createDocumentFeedbackAPI, createConversationAPI, userFeedbackAPI }
