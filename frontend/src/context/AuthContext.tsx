
import React, { createContext, useContext, useEffect, useState } from 'react'
import { loginAPI, getUserMessagesAPI, userFeedbackAPI, resendCodeAPI, verifyAPI, logoutAPI, registerAPI, verifyUser, createConversationAPI, createMessageAPI, getConversationsAPI } from '../services/AuthService';
import type { LoginAPIOutput, UserProfile, Message, Conversations } from '../models/Types';


interface AuthContextType {
    user: UserProfile | null;
    userMessages: Message[] | null;
    conversations: Conversations[] | null;
    loading: boolean;
    createConversation: (conversation_name: string, username: string) => Promise<Conversations | undefined>;
    createMessage: (conversation_name: string, text: string, role: string, id: string, feedback: boolean | null) => Promise<void>;
    fetchUserMessages: (conversation_name: string) => Promise<void>;
    loginUser: (username: string, password: string) => Promise<LoginAPIOutput> | null;
    logoutUser: () => Promise<void>;
    fetchConversations: (username: string) => Promise<void>;
    RegisterUser: (username: string, password: string, email: string) => Promise<void>;
    verifyCodeUser: (username: string, code: string) => Promise<boolean>;
    resendCode: (username: string, email: string) => Promise<void>;
    userFeedback: (message_id: string, conversation_id: string, feedback: boolean) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [userMessages, setMessages] = useState<Message[] | null>(null);
    const [conversations, setConversations] = useState<Conversations[]>([]);
    const [loading, setLoading] = useState(true);

    const RegisterUser = async (username: string, password: string, email: string): Promise<void> => {
        try {
            const res = await registerAPI(username, password, email);
            console.log(res);
            if (res) {
                setUser({ username: username, email: email, verified: false })
            }
            else {
                setUser(null);
                throw new Error("Registration failed: No response from API");
            }
        }
        catch (err) {
            console.error("Registration failed", err);
            setUser(null);
            throw err;
        }
    }

    const verifyCodeUser = async (username: string, code: string): Promise<boolean> => {
        try {
            const res = await verifyAPI(username, code);
            if (res) {
                return true;
            }
            else {
                return false;
            }
        }
        catch (err) {
            console.error("Verification failed", err);
            setUser(null);
            throw err;
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

    const loginUser = async (username: string, password: string): Promise<LoginAPIOutput> => {
        try {
            const res = await loginAPI(username, password);
            if (res) {
                console.log(res.user_details)
                setUser({ username: res.user_details.username, email: res.user_details.email, verified: res.user_details.verified })
                return res;
            }
            else {
                setUser(null);
                throw new Error("Login failed: No response from API");
            }
        }
        catch (err) {
            console.error("Login failed", err);
            setUser(null);
            throw err;
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

    const createMessage = async (conversation_name: string, text: string, role: string, id: string, feedback: boolean | null) => {
        try {
            const res = await createMessageAPI(conversation_name, text, role, id, feedback);
            const newMessage = { conversation_name, message: text, role, id, feedback, timestamp: new Date().toISOString() };
            if (res) {
                setMessages(prev => [...(prev ?? []), newMessage])
            }
            else {
                throw new Error("Message was not created properly");
            }
        }
        catch (err) {
            console.error(`Could not create new Message with name:${conversation_name}, message: ${text}. Error:`, err);
        }
    }

    const fetchUserMessages = async (conversation_name: string) => {
        try {
            const messages = await getUserMessagesAPI(conversation_name);
            if (messages) {
                console.log(messages)
                setMessages(messages);
            }
            else {
                setMessages(null);
            }
        }
        catch (err) {
            console.error(`Messages were not fetched from user in conversation ${conversation_name}`, err);
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
                console.log("Something went completely wrong");
            }

        }
        catch (err) {
            setUser(null);
            setMessages(null);
            console.error("Logout failed", err);
        }
    }

    useEffect(() => {
        const initialize = async () => {
            try {
                const res = await verifyUser();
                console.log("User Verified", res);
                if (res) {
                    setUser(res);
                }
            }
            catch {
                console.log("Something happened");
                setUser(null);
            }
            finally {
                setLoading(false);
            }
        };
        initialize();
    }, [])

    return (
        <AuthContext.Provider value={{ user, userMessages, userFeedback, resendCode, verifyCodeUser, RegisterUser, loginUser, logoutUser, fetchUserMessages, loading, conversations, createConversation, createMessage, fetchConversations }}>
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
