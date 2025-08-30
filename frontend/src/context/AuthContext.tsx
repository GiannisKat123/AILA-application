/**
 * @packageDocumentation
 *
 *  Provides global authentication and user data management across the React app.
 *
 * Core Responsibilities:
 * ----------------------
 * 1. Authentication lifecycle:
 *    - login, logout, register
 *    - verify user sessions with backend
 *    - resend verification codes
 *
 * 2. User state management:
 *    - Tracks current logged-in user (`user`)
 *    - Maintains user's conversations (`conversations`)
 *    - Maintains messages in active conversation (`userMessages`)
 *
 * 3. Conversation + Message features:
 *    - Create and rename conversations
 *    - Fetch user conversations
 *    - Create new messages
 *    - Fetch user messages
 *    - Submit feedback on messages
 *
 * 4. Context Hook:
 *    - `useAuth()` to access user state and actions
 *
 * Integration:
 * ------------
 * Wrap your app in the `AuthProvider` so child components can
 * consume authentication context via `useAuth()`.
 *
* 
* @remarks
* Provides global authentication and user data management across the React app.
*
* @example
* ```tsx
*   <AuthProvider>
*     <App />
*   </AuthProvider>
*
*   const { user, loginUser, logoutUser } = useAuth();
* ```
*/

import React, { createContext, useContext, useEffect, useState } from 'react';
import {
    loginAPI,
    getUserMessagesAPI,
    userFeedbackAPI,
    renameConversationAPI,
    resendCodeAPI,
    verifyAPI,
    logoutAPI,
    registerAPI,
    verifyUser,
    createConversationAPI,
    createMessageAPI,
    getConversationsAPI,
} from '../services/AuthService.jsx';
import type {
    LoginAPIOutput,
    UserProfile,
    Message,
    Conversations,
    ErrorMessage,
} from '../models/Types.jsx';


/**
 * Shape of the AuthContext — defines all state + actions
 * 
 */
export interface AuthContextType {
    /** Current logged-in user, or `null` if unauthenticated. */
    user: UserProfile | null;
    /** Messages in the active conversation. */
    userMessages: Message[] | null;
    /** List of all conversations for the user. */
    conversations: Conversations[] | null;
    /** Loading state while verifying session. */
    loading: boolean;
    /** Create a new conversation. */
    createConversation: (conversation_name: string, username: string) => Promise<Conversations | undefined>;
    /** Create a new message in a conversation. */
    createMessage: (conversation_id: string, text: string, role: string, id: string, feedback: boolean | null) => Promise<void>;
    /** Fetch all messages for a conversation. */
    fetchUserMessages: (conversation_id: string) => Promise<void>;
    /** Login a user. */
    loginUser(username: string, password: string): Promise<LoginAPIOutput | ErrorMessage | null>;
    /** Logout the current user. */
    logoutUser: () => Promise<void>;
    /** Fetch all conversations for the user. */
    fetchConversations: (username: string) => Promise<void>;
    /** Register a new user. */
    RegisterUser: (username: string, password: string, email: string) => Promise<boolean | ErrorMessage>;
    /** Verify a user with a code. */
    verifyCodeUser: (username: string, code: string) => Promise<boolean | ErrorMessage>;
    /** Resend a verification code. */
    resendCode: (username: string, email: string) => Promise<void>;
    /** Submit feedback on a message. */
    userFeedback: (message_id: string, conversation_id: string, feedback: boolean) => Promise<void>;
    /** Rename a conversation. */
    renameConversation: (conversation_name: string, conversation_id: string) => Promise<void | ErrorMessage>;
}


export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Provides the authentication context and state to all child components.
 *
 * @remarks
 * - Should wrap your entire application (usually in `main.tsx` or `index.tsx`).
 * - Exposes authentication and conversation state/actions via {@link useAuth}.
 *
 * @param children - React component tree to be wrapped by the provider.
 * @returns A React context provider that supplies {@link AuthContextType} to its children.
 *
 * @example
 * ```tsx
 * import { AuthProvider } from "./context/AuthContext";
 *
 * const root = createRoot(document.getElementById("root")!);
 * root.render(
 *   <AuthProvider>
 *     <App />
 *   </AuthProvider>
 * );
 * ```
 */
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [userMessages, setMessages] = useState<Message[] | null>(null);
    const [conversations, setConversations] = useState<Conversations[]>([]);
    const [loading, setLoading] = useState(true);

    /**
     * Register a new user
     * param username string – desired username
     * param password string – plaintext password (validated backend-side)
     * param email string – user’s email
     * returns Promise<boolean | ErrorMessage> – true if successful, otherwise error object
     */
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


    /**
     * Verify user with a code sent to their email
     * param username string – username of the account
     * param code string – verification code provided via email
     * returns Promise<boolean | ErrorMessage>
     */
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

    /**
     * Resend verification code
     * param username string
     * param email string
     * returns void – throws error if resend fails
     */
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


    /**
     * Submit user feedback for a message
     * param message_id string
     * param conversation_id string
     * param feedback boolean | undefined – true/false/null
     * returns void – throws error if backend rejects
     */
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


    /**
   * Login user
   * param username string
   * param password string
   * returns Promise<LoginAPIOutput | ErrorMessage>
   * - On success: updates `user` state
   * - On failure: clears `user` state and returns error
   */
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

    /**
     * Create a new conversation
     * param conversation_name string
     * param username string
     * returns Promise<Conversations | undefined>
     * - Updates state with new conversation if successful
     */
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

    /**
     * Fetch all conversations for a user
     * param username string
     * returns Promise<void> – updates `conversations` state
     */
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

    /**
   * Create a new message inside a conversation
   * param conversation_id string
   * param text string – message content
   * param role string – sender role ("user" | "assistant")
   * param id string – UUID for message
   * param feedback boolean | null – initial feedback (optional)
   * returns Promise<void> – appends message to state
   */
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

    /**
   * Fetch all messages for a conversation
   * param conversation_id string
   * returns Promise<void> – sets `userMessages` state
   */
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

    /**
   * Logout the user
   * - Clears cookies via backend
   * - Clears user + message state
   */
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

    /**
   * Rename an existing conversation
   * param conversation_id string
   * param conversation_name string
   * returns void | ErrorMessage
   */
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

    /**
     * On mount: verify if a session exists with backend.
     * If valid → hydrate user state
     * If invalid → clear user
     */
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

/**
* Hook to access {@link AuthContextType}.
*
* @remarks
* Must be used within an {@link AuthProvider}. Throws an error otherwise.
*
* @returns The current authentication context.
*
* @example
* ```tsx
* const { user, loginUser, logoutUser } = useAuth();
* ```
*/
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
