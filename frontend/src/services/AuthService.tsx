/**
* @packageDocumentation
*
* Axios-based client for the AILA backend API.
* 
* @remarks
* Axios client for the AILA backend. Encapsulates all HTTP calls:
* - Login, logout, register, verify
* - Conversations (create, fetch, rename)
* - Messages (create, fetch)
* - Feedback submission
* - Request endpoint (chat)
* 
* Responsibilities
* ----------------
* - Encapsulates all HTTP calls (login, register, verify, conversations, messages, feedback, logout).
* - Normalizes error handling and return shapes for the frontend.
*
* Conventions
* -----------
* - All requests use `withCredentials: true` to send HttpOnly cookies (JWT).
* - On Axios errors, functions return `{ error_message: string }` where applicable.
* - Functions that don't need a payload from the server return `boolean | undefined`.
* - Functions that must return data bubble it through `.data` as typed.
*
* Conventions:
* - All requests → `withCredentials: true` (send cookies)
* - Errors → return `{ error_message }` where possible
* - Functions without data → return `boolean | undefined`
* - Functions with data → bubble `.data`
*
* @example
* ```ts
* import { loginAPI } from '../services/AuthService';
* const res = await loginAPI('alice', 's3cret');
* if ('user_details' in res) {
* console.log(res.user_details.username);
* }
* ```
*/


import axios from 'axios';
import api from '../api/axios.jsx';
import type {
    LoginAPIOutput,
    UserProfile,
    Message,
    Conversations,
    ErrorMessage,
} from '../models/Types.jsx';





/**
 * Login with username/password.
 *
 * @param username - Account username
 * @param password - Account password (plaintext)
 * @returns
 *  - On success: `{ user_details: UserProfile }`
 *  - On failure: `{ error_message: string }`
 */
const loginAPI = async (username: string, password: string): Promise<LoginAPIOutput | ErrorMessage> => {
    try {
        const response = await api.post('/login', { username: username, password: password }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            console.error("Non-Axios error:", err);
            return { error_message: String(err) };
        }
    }
}

/**
 * Rename a conversation title.
 *
 * @param conversation_name - New title
 * @param conversation_id - Conversation UUID
 * @returns
 *  - On success: `true`
 *  - On failure: `{ error_message: string }`
 */
const renameConversationAPI = async (conversation_name: string, conversation_id: string): Promise<boolean | ErrorMessage> => {
    try {
        console.log("Renaming Conversation API called with:", conversation_name, conversation_id);
        const response = await api.post('/update_conversation', { conversation_name: conversation_name, conversation_id: conversation_id }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            console.error("Non-Axios error:", err);
            return { error_message: String(err) };
        }
    }
}


/**
 * Register a new user.
 *
 * @param username - Desired username
 * @param password - Desired password (policy enforced server-side)
 * @param email - User email (verification code sent here)
 * @returns
 *  - On success: `true`
 *  - On failure: `{ error_message: string }`
 */
const registerAPI = async (username: string, password: string, email: string): Promise<boolean | ErrorMessage> => {
    try {
        const response = await api.post('/register', { username: username, password: password, email: email }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            console.error("Non-Axios error:", err);
            return { error_message: String(err) };
        }
    }
}


/**
 * Verify a user using a code emailed to them.
 *
 * @param username - Username to verify
 * @param code - One-time verification code
 * @returns
 *  - On success: `true`
 *  - On failure: `{ error_message: string }`
 */
const verifyAPI = async (username: string, code: string): Promise<boolean | ErrorMessage> => {
    try {
        const response = await api.post('/verify', { username: username, code: code }, { withCredentials: true });
        return response.data;
    }
    catch (err) {
        if (axios.isAxiosError(err)) {
            return { error_message: err.response?.data.detail };
        }
        else {
            console.error("Non-Axios error:", err);
            return { error_message: String(err) };
        }
    }
}



/**
 * Resend the verification code to a user.
 *
 * @param username - Username
 * @param email - Registered email address
 * @returns
 *  - On success: `true`
 *  - On failure: `undefined` (and logs error)
 */
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

/**
 * Submit feedback for a specific assistant message.
 *
 * @param message_id - Message UUID
 * @param conversation_id - Conversation UUID
 * @param feedback - true = 👍, false = 👎, undefined = clear/reset
 * @returns
 *  - On success: `true`
 *  - On failure: `undefined` (and logs error)
 */
const userFeedbackAPI = async (message_id: string, conversation_id: string, feedback: boolean | undefined): Promise<boolean | undefined> => {
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

/**
 * Create a new conversation for the user.
 *
 * @param conversation_name - Initial title
 * @param username - Owner username
 * @returns
 *  - On success: `{ conversation_id, conversation_name }`
 *  - On failure: `undefined` (and logs error)
 */
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

/**
 * Create a new message within a conversation.
 *
 * @param conversation_id - Conversation UUID
 * @param text - Message content
 * @param role - 'user' | 'assistant'
 * @param id - Client-generated UUID for the message
 * @param feedback - Initial feedback (optional)
 * @returns
 *  - On success: `Message`
 *  - On failure: `undefined` (and logs error)
 */
const createMessageAPI = async (conversation_id: string, text: string, role: string, id: string, feedback: boolean | null): Promise<Message | undefined> => {
    try {
        const response = await api.post('/new_message', { conversation_id: conversation_id, text: text, role: role, id: id, feedback: feedback }, { withCredentials: true });
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

/**
 * Fetch all conversations for a user.
 *
 * @param username - Username whose conversations to fetch
 * @returns
 *  - On success: `Conversations[]`
 *  - On failure: `undefined` (and logs error)
 */
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

/**
 * Fetch all messages for a conversation.
 *
 * @param conversation_id - Conversation UUID
 * @returns
 *  - On success: `Message[]`
 *  - On failure: throws Axios error (caller should handle)
 */
const getUserMessagesAPI = async (conversation_id: string): Promise<Message[] | undefined> => {
    const response = await api.get('/messages', {
        params: { conversation_id },
        withCredentials: true
    });
    return response.data;
}

/**
 * Verify current session and return user profile from cookie.
 *
 * @returns
 *  - On success: `UserProfile`
 *  - On failure: throws Axios error (caller should handle)
 */
const verifyUser = async (): Promise<UserProfile | undefined> => {
    const response = await api.get('/get_user', { withCredentials: true });
    return response.data;
}

/**
 * Direct request to chat endpoint without streaming.
 *
 * @param userQuery - Message to send
 * @returns
 *  - On success: backend response body
 *  - On failure: `void` (and logs error)
 */
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

/**
 * Logout user (clears the HttpOnly cookie on server).
 *
 * @returns
 *  - `true` if the call resolves
 *  - `false` if the call fails
 */
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

export { loginAPI, getUserMessagesAPI, userFeedbackAPI, resendCodeAPI, verifyAPI, renameConversationAPI, logoutAPI, registerAPI, requestAPI, verifyUser, createConversationAPI, createMessageAPI, getConversationsAPI };

