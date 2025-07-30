
import React, { createContext, useContext, useEffect, useState } from 'react'
import { loginAPI, getUserMessagesAPI, userFeedbackAPI, renameConversationAPI, resendCodeAPI, verifyAPI, logoutAPI, registerAPI, verifyUser, createConversationAPI, createMessageAPI, getConversationsAPI } from '../services/AuthService';
import type { LoginAPIOutput, UserProfile, Message, Conversations, ErrorMessage } from '../models/Types';


interface AuthContextType {
    user: UserProfile | null;
    userMessages: Message[] | null;
    conversations: Conversations[] | null;
    loading: boolean;
    createConversation: (conversation_name: string, username: string) => Promise<Conversations | undefined>;
    createMessage: (conversation_id: string, text: string, role: string, id: string, feedback: boolean | null) => Promise<void>;
    fetchUserMessages: (conversation_id: string) => Promise<void>;
    loginUser: (username: string, password: string) => Promise<LoginAPIOutput | ErrorMessage> | null;
    logoutUser: () => Promise<void>;
    fetchConversations: (username: string) => Promise<void>;
    RegisterUser: (username: string, password: string, email: string) => Promise<boolean | ErrorMessage>;
    verifyCodeUser: (username: string, code: string) => Promise<boolean | ErrorMessage>;
    resendCode: (username: string, email: string) => Promise<void>;
    userFeedback: (message_id: string, conversation_id: string, feedback: boolean) => Promise<void>;
    renameConversation: (conversation_name: string, conversation_id: string) => Promise<void | ErrorMessage>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [userMessages, setMessages] = useState<Message[] | null>(null);
    const [conversations, setConversations] = useState<Conversations[]>([]);
    const [loading, setLoading] = useState(true);

    const RegisterUser = async (username: string, password: string, email: string): Promise<boolean | ErrorMessage> => {
        try {
            const res = await registerAPI(username, password, email);
            if (res && res === true) {
                setUser({ username: username, email: email, verified: false })
                return true;
            }
            else if (res && typeof res === 'object' && 'error_message' in res) {
                setUser(null);
                return { error_message: res.error_message }
            }
            else {
                setUser(null);
                return { error_message: 'Something went wrong in registration' }
            }
        }
        catch (err) {
            setUser(null);
            return { error_message: String(err) };
        }
    }

    const verifyCodeUser = async (username: string, code: string): Promise<boolean | ErrorMessage> => {
        try {
            const res = await verifyAPI(username, code);
            if (res === true) {
                return true;
            }
            else if (res && typeof res == 'object' && 'error_message' in res) {
                return { error_message: res.error_message }
            }
            else {
                return { error_message: 'Something went wrong in verification' }
            }
        }
        catch (err) {
            console.error("Verification failed", err);
            setUser(null);
            return { error_message: String(err) };
        }
    }

    const resendCode = async (username: string, email: string): Promise<void> => {
        try {
            const res = await resendCodeAPI(username, email);
            if (res) {
                return;
            }
            else {
                throw new Error("Resend Code failed: No response from API");
            }
        }
        catch (err) {
            console.error("Resend Code failed", err);
            setUser(null);
            throw err;
        }
    }

    const userFeedback = async (message_id: string, conversation_id: string, feedback: boolean | undefined): Promise<void> => {
        try {
            const res = await userFeedbackAPI(message_id, conversation_id, feedback);
            if (res) {
                return;
            }
            else {
                throw new Error("userFeedback failed: No response from API");
            }
        }
        catch (err) {
            console.error("userFeedback failed", err);
            setUser(null);
            throw err;
        }
    }



    const loginUser = async (username: string, password: string): Promise<LoginAPIOutput | ErrorMessage> => {
        try {
            const res = await loginAPI(username, password);
            if (res && typeof res === 'object' && "user_details" in res) {
                setUser({ username: res.user_details.username, email: res.user_details.email, verified: res.user_details.verified })
                return res;
            }
            else if (res && typeof res === 'object' && "error_message" in res) {
                setUser(null);
                return { error_message: res.error_message }
            }
            // Ensure a return value in all cases
            setUser(null);
            return { error_message: "Unknown error during login" };
        }
        catch (err) {
            console.error("Login failed", err);
            setUser(null);
            return { error_message: String(err) }
        }
    }

    const createConversation = async (conversation_name: string, username: string): Promise<Conversations | undefined> => {
        try {
            const res = await createConversationAPI(conversation_name, username);
            if (res) {
                setConversations(prev => [res, ...prev]);
                return res;
            }
            else {
                throw new Error("Conversation was not created properly");
            }
        }
        catch (err) {
            console.error(`Could not create new Conversation with name:${conversation_name}. Error:`, err);
        }
    }

    const fetchConversations = async (username: string) => {
        try {
            const res = await getConversationsAPI(username);
            if (res) {
                setConversations(res)
            }
        }
        catch (err) {
            console.error(`Could not fetch Conversations from user:${username}. Error:`, err);
        }
    }

    const createMessage = async (conversation_id: string, text: string, role: string, id: string, feedback: boolean | null) => {
        try {
            const res = await createMessageAPI(conversation_id, text, role, id, feedback);
            const newMessage = { conversation_id, message: text, role, id, feedback, timestamp: new Date().toISOString() };
            if (res) {
                setMessages(prev => [...(prev ?? []), newMessage])
            }
            else {
                throw new Error("Message was not created properly");
            }
        }
        catch (err) {
            console.error(`Could not create new Message with id:${conversation_id}, message: ${text}. Error:`, err);
        }
    }

    const fetchUserMessages = async (conversation_id: string) => {
        try {
            const messages = await getUserMessagesAPI(conversation_id);
            if (messages) {
                setMessages(messages);
            }
            else {
                setMessages(null);
            }
        }
        catch (err) {
            console.error(`Messages were not fetched from user in conversation ${conversation_id}`, err);
            setMessages(null);
        }
    }

    const logoutUser = async () => {
        try {
            const res = await logoutAPI();
            if (res) {
                setUser(null);
                setMessages(null);
            }
            else {
                setUser(null);
                setMessages(null);
            }

        }
        catch (err) {
            setUser(null);
            setMessages(null);
            console.error("Logout failed", err);
        }
    }

    const renameConversation = async (conversation_id: string, conversation_name: string): Promise<void | ErrorMessage> => {
        try {
            console.log("Renaming Conversation", conversation_name, conversation_id);
            const res = await renameConversationAPI(conversation_name, conversation_id);

            if (typeof res === 'object' && 'error_message' in res) {
                return { error_message: res.error_message };
            }

            // Success: do nothing
            return;
        }
        catch (err) {
            console.error("Updating Conversation Name failed", err);
            setUser(null);
            return { error_message: String(err) }
        }
    }

    useEffect(() => {
        const initialize = async () => {
            try {
                const res = await verifyUser();
                if (res) {
                    setUser(res);
                }
            }
            catch {
                setUser(null);
            }
            finally {
                setLoading(false);
            }
        };
        initialize();
    }, [])

    return (
        <AuthContext.Provider value={{ user, userMessages, renameConversation, userFeedback, resendCode, verifyCodeUser, RegisterUser, loginUser, logoutUser, fetchUserMessages, loading, conversations, createConversation, createMessage, fetchConversations }}>
            {children}
        </AuthContext.Provider>
    )

}

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
