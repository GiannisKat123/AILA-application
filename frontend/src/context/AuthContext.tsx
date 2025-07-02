
import React, { createContext, useContext, useEffect, useState } from 'react'
import { getUserMessagesAPI, loginAPI, logoutAPI, verifyUser, getConversationsAPI, createConversationAPI, createMessageAPI } from '../services/AuthService';
import type { LoginAPIOutput, UserProfile, Message } from '../models/Types';

interface AuthContextType {
    user: UserProfile | null;
    userMessages: Message[] | null;
    conversations: string[] | null;
    loading: boolean;
    createConversation: (conversation_name: string, username: string) => Promise<void>;
    createMessage: (conversation_name: string, text: string, role: string) => Promise<void>;
    fetchUserMessages: (conversation_name: string) => Promise<void>;
    loginUser: (username: string, password: string) => Promise<LoginAPIOutput> | null;
    logoutUser: () => Promise<void>;
    fetchConversations: (username: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [userMessages, setMessages] = useState<Message[] | null>(null);
    const [conversations, setConversations] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    const loginUser = async (username: string, password: string): Promise<LoginAPIOutput> => {
        try {
            const res = await loginAPI(username, password);
            if (res) {
                setUser(res.user_details)
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

    const createConversation = async (conversation_name: string, username: string) => {
        try {
            const res = await createConversationAPI(conversation_name, username);
            if (res) {
                setConversations(prev => [conversation_name, ...prev]);
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

    const createMessage = async (conversation_name: string, text: string, role: string) => {
        try {
            const res = await createMessageAPI(conversation_name, text, role);
            if (res) {
                setMessages(prev => [...(prev ?? []), res])
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
        <AuthContext.Provider value={{ user, userMessages, loginUser, logoutUser, fetchUserMessages, loading, conversations, createConversation, createMessage, fetchConversations }}>
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
