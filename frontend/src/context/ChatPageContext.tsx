import { createContext, useCallback, useContext, useState } from "react";
import type { Conversation, ErrorMessage, Message, messageFeedbackDetails } from "../models/Types";
import { createAutomatedMessageAPI, createConversationAPI, createDocumentFeedbackAPI, createMessageAPI, getConversationsAPI, getUserMessagesAPI, renameConversationAPI, userFeedbackAPI } from "../services/ChatPageService";

export interface ChatContextType {
    userMessages: Message[] | null;
    conversations: Conversation[] | null;
    uploadedFiles: File[] | null;
    messageFeedbackDetails: messageFeedbackDetails;
    currentConversation: Conversation;
    isOnline: boolean;
    isStreaming: boolean;
    sidebarOpen: boolean;
    userQuery: string;
    openFeedback: boolean;
    setUserQuery: React.Dispatch<React.SetStateAction<string>>;
    setOnlineMode: React.Dispatch<React.SetStateAction<boolean>>;
    setSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
    setStreaming: React.Dispatch<React.SetStateAction<boolean>>;
    setCurrentConversation: React.Dispatch<React.SetStateAction<Conversation>>;
    setUploadedFiles: React.Dispatch<React.SetStateAction<File[]>>;
    setmessageFeedbackDetails: React.Dispatch<React.SetStateAction<messageFeedbackDetails>>;
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    setConversations: React.Dispatch<React.SetStateAction<Conversation[]>>;
    setFeedbackFormOpen: React.Dispatch<React.SetStateAction<boolean>>;
    renameConversation: (username: string, conversation_id: string, conversation_name: string) => Promise<void | ErrorMessage>;
    createDocumentFeedback: (username: string, query_id: string, negative_query_id: string, doc_name: string, doc_text: string, context: string, theme: string) => Promise<void | ErrorMessage>;
    createConversation: (username: string, conversation_name: string, conversation_type: string) => Promise<Conversation | undefined>;
    createMessage: (username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined) => Promise<void>;
    fetchUserMessages: (username: string, conversation_id: string) => Promise<void>;
    createAutomatedMessage: (conversation_id: string, conversation_name: string, conversation_type: string) => Promise<string | ErrorMessage>;
    fetchConversations: (username: string) => Promise<void>;
    userFeedback: (message_id: string, username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined) => Promise<void>;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
    const [isOnline, setOnlineMode] = useState(false);
    const [isStreaming, setStreaming] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [userMessages, setMessages] = useState<Message[]>([]);
    const [userQuery, setUserQuery] = useState("");
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
    const [openFeedback, setFeedbackFormOpen] = useState(false);
    const [currentConversation, setCurrentConversation] = useState<Conversation>({
        conversation_name: '', conversation_id: '', conversation_type: ''
    });
    const [messageFeedbackDetails, setmessageFeedbackDetails] = useState<messageFeedbackDetails>({
        fileDoc: null as File | null,
        message_id: '',
        conversation_id: '',
        query_id: '',
        generated_answer_id: '',
        theme: '',
        context: '',
        generalFeedback: ''
    });


    const userFeedback = async (message_id: string, username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined): Promise<void> => {
        try {
            const res = await userFeedbackAPI(message_id, username, conversation_id, text, role, feedback);
            if (res) {
                return;
            }
            else {
                throw new Error("userFeedback failed: No response from API");
            }
        }
        catch (err) {
            console.error("userFeedback failed", err);
            throw err;
        }
    }

    const createConversation = async (username: string, conversation_name: string, conversation_type: string): Promise<Conversation | undefined> => {
        try {
            const res = await createConversationAPI(username, conversation_name, conversation_type);
            console.log('createConversation', res)
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

    const createDocumentFeedback = async (username: string, query_id: string, negative_query_id: string, doc_name: string, doc_text: string, context: string, theme: string) => {
        try {
            const res = await createDocumentFeedbackAPI(username, query_id, negative_query_id, doc_name, doc_text, context, theme);
            if (res) {
                return;
            }
            else {
                throw new Error("Conversation was not created properly");
            }
        }
        catch (err) {
            console.error(`Could not create new Document Feedback on Message:${query_id}. Error:`, err);
        }
    }

    const fetchConversations = useCallback(async (username: string) => {
        try {
            const res = await getConversationsAPI(username);
            console.log("CONVERSATIONS", res)
            if (res) {
                setConversations(res);
            }
        }
        catch (err) {
            console.error(`Could not fetch Conversations from user:${username}. Error:`, err);
        }
    }, []);

    const createMessage = async (username: string, conversation_id: string, text: string, role: string, feedback: boolean | undefined) => {
        try {
            const res = await createMessageAPI(username, conversation_id, text, role, feedback);
            if ('error_message' in res) { throw new Error("Message was not created properly") }
            const newMessage = { id: res.id, message: text, timestamp: new Date().toISOString(), role: role, feedback: feedback };
            setMessages(prev => [...(prev ?? []), newMessage])
        }
        catch (err) {
            console.error(`Could not create new Message with id:${conversation_id}, message: ${text}. Error:`, err);
        }
    }

    const fetchUserMessages = async (username: string, conversation_id: string) => {
        try {
            const messages = await getUserMessagesAPI(username, conversation_id);
            if (messages) {
                console.log(messages)
                setMessages(messages);
            }
            else {
                setMessages([]);
            }
        }
        catch (err) {
            console.error(`Messages were not fetched from user in conversation ${conversation_id}`, err);
            setMessages([]);
        }
    }

    const renameConversation = async (username: string, conversation_id: string, conversation_name: string): Promise<void | ErrorMessage> => {
        try {
            // console.log("Renaming Conversation", conversation_name, conversation_id);
            const res = await renameConversationAPI(username, conversation_id, conversation_name);

            if (typeof res === 'object' && 'error_message' in res) {
                return { error_message: res.error_message };
            }

            // Success: do nothing
            return;
        }
        catch (err) {
            return { error_message: String(err) }
        }
    }

    const createAutomatedMessage = async (conversation_id: string, conversation_name: string, conversation_type: string): Promise<string | ErrorMessage> => {
        try {
            // console.log("Renaming Conversation", conversation_name, conversation_id);
            const res = await createAutomatedMessageAPI(conversation_id, conversation_name, conversation_type);
            if (res) {
                return res;
            }
            else {
                console.log("Something went completely wrong with automated message");
                return { error_message: 'Something went completely wrong with automated message ' }
            }
        }
        catch (err) {
            return { error_message: String(err) }
        }
    }

    return (
        <ChatContext.Provider value={{ openFeedback, setFeedbackFormOpen, setConversations, userQuery, setUserQuery, isOnline, setOnlineMode, isStreaming, setStreaming, sidebarOpen, setSidebarOpen, setMessages, messageFeedbackDetails, setmessageFeedbackDetails, currentConversation, setCurrentConversation, uploadedFiles, setUploadedFiles, userMessages, createAutomatedMessage, renameConversation, createDocumentFeedback, userFeedback, fetchUserMessages, conversations, createConversation, createMessage, fetchConversations }}>
            {children}
        </ChatContext.Provider>
    )

}

export const useChat = (): ChatContextType => {
    const context = useContext(ChatContext);
    if (context === undefined) throw new Error("useChat must be used within a ChatProvider");
    return context
}

