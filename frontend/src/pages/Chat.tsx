/**
* @packageDocumentation
*
* @remarks
* The main chat UI for **AILA**. Provides:
* - Conversation list (create, select, inline rename)
* - Streaming chat with backend (`/request` endpoint)
* - Persistence via {@link AuthContextType}
* - Per‑message feedback (👍/👎)
* - Responsive sidebar (mobile overlay)
*
* **Data Flow**
* 1. On mount → fetch user’s conversations.
* 2. Auto‑select first conversation & fetch messages.
* 3. Local `messages` mirror context `userMessages` for real‑time patching.
* 4. On submit:
* - Append user + placeholder assistant messages.
* - Stream tokens and patch assistant message.
* - Persist messages and refresh conversation.
*
* Accessibility
* -------------
* - Uses semantic buttons & aria-friendly state updates.
*
* Styling
* -------
* - TailwindCSS for layout & theming.
* - lucide-react icons (User, Bot, Menu, X).
* - Framer Motion for subtle entrance animation on greeting.
* 
* @example
* ```tsx
* import Chat from './pages/Chat';
* <Route path="/chat" element={<Chat />} />
* ```
*/

import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios.jsx';
import type { Message, Conversations } from '../models/Types.jsx';
import { Menu, X, User, Bot } from 'lucide-react';
import { motion } from 'framer-motion';



/**
 * Chat component — renders the main conversation interface.
 *
 * @remarks
 * This component is the core chat UI for AILA. It manages conversation state,
 * message streaming, feedback, and user interactions.
 *
 * ## Responsibilities
 * - Display a sidebar of conversations (with create, select, and rename).
 * - Render the chat viewport with user and assistant messages.
 * - Stream assistant responses from the backend in real time.
 * - Capture 👍 / 👎 feedback on assistant messages.
 * - Manage authentication lifecycle actions (logout).
 * - Provide mobile-friendly sidebar toggle and responsive layout.
 *
 * ## Props
 * None. This component consumes global state from {@link useAuth}.
 *
 * ## Returns
 * A React element representing the chat UI with sidebar + main conversation area.
 *
 * @example
 * ```tsx
 * import { Chat } from "./pages/Chat";
 *
 * <Route path="/chat" element={<Chat />} />
 * ```
 */
export const Chat = () => {
    // -------------------------
    // Local state
    // -------------------------
    const [messages, setMessages] = useState<Message[]>([]);
    const [userQuery, setUserQuery] = useState('');
    const [botResponse, setBotResponse] = useState('');
    const [currentConversation, setCurrentConversation] = useState<Conversations>({
        conversation_name: '',
        conversation_id: ''
    });

    // Inline rename controls
    const [editingConvId, setEditingConvId] = useState('');
    const [editedTitle, setEditedTitle] = useState('');

    // Mobile sidebar toggle
    const [sidebarOpen, setSidebarOpen] = useState(false);

    // -------------------------
    // Context + navigation
    // -------------------------
    const {
        user,
        userMessages,
        userFeedback,
        logoutUser,
        fetchUserMessages,
        conversations,
        createConversation,
        createMessage,
        fetchConversations,
        renameConversation,
    } = useAuth();

    const navigate = useNavigate();
    const chatRef = useRef<HTMLDivElement | null>(null);

    /**
     * When user becomes available, fetch user conversations.
     */
    useEffect(() => {
        if (user) fetchConversations(user.username);
    }, [user]);

    /**
     * Auto-scroll chat viewport on new messages.
     */
    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollIntoView({ behavior: 'smooth' })
        }
    }, [userMessages])

    /**
     * When conversations load, auto-select the first one and fetch its messages.
     */
    useEffect(() => {
        if (conversations?.length) {
            const initial = conversations[0];
            if (initial) {
                setCurrentConversation(initial);
                fetchUserMessages(initial.conversation_id);
            }
        }
    }, [conversations]);

    /**
     * Keep local `messages` mirrored with context's `userMessages`.
     * (We still maintain local state to patch streaming chunks in real time.)
     */
    useEffect(() => {
        setMessages(userMessages ?? []);
    }, [userMessages]);


    // -------------------------
    // Handlers
    // -------------------------

    /**
     * Submit a new user query:
     * - Appends an user message + a placeholder assistant message.
     * - Streams response from backend and updates the last assistant message incrementally.
     * - On stream completion, persists both messages via context calls and refreshes.
     */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const userMessage = userQuery.trim();
        if (!userMessage) return;

        const now = new Date().toISOString();

        // Prepare messages (user + empty assistant)
        const newMessages = [
            { message: userMessage, role: 'user', timestamp: now, id: uuidv4(), feedback: null },
            { message: '', role: 'assistant', timestamp: now, id: uuidv4(), feedback: null }
        ];

        // Push to UI immediately
        setMessages(prev => [...prev, ...newMessages]);
        setUserQuery('');
        setBotResponse('');

        const controller = new AbortController();

        try {
            const res = await fetch(`${api.defaults.baseURL}/request`, {
                method: 'POST',
                signal: controller.signal,
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    message: userMessage,
                    conversation_history: messages.slice(-10)
                })
            });

            if (!res.ok || !res.body) {
                setBotResponse("Error from bot");
                return;
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let fullBotResponse = '';

            // The bot responses in streaming manner, meaning that it gives chunks of the final message. 
            // Below we try to print to the screen each of the chunks given by the bot in real time 

            // Read SSE-ish chunks
            while (true) {
                const { value, done } = await reader.read();
                const chunk = decoder.decode(value);

                // Each "event" is "data: {json}\n\n"
                const lines = chunk.split('\n\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const jsonStr = line.replace("data: ", "");
                        const parsed = JSON.parse(jsonStr);

                        // Accumulate content
                        fullBotResponse += parsed.response;

                        // Patch last assistant message on-screen
                        setMessages(prev => {
                            const updated = [...prev];
                            const lastIndex = updated.length - 1;
                            if (updated[lastIndex]) {
                                updated[lastIndex].message = fullBotResponse;
                                updated[lastIndex].timestamp = new Date().toISOString();
                            }
                            return updated;
                        });
                    } catch (err) {
                        console.error("Invalid chunk", err);
                    }
                }

                if (done) {
                    // Persist messages after stream completes
                    if (currentConversation && currentConversation.conversation_id) {
                        if (newMessages[0] && newMessages[1]) {
                            await createMessage(currentConversation.conversation_id, userMessage, 'user', newMessages[0].id, newMessages[0].feedback);
                            await createMessage(currentConversation.conversation_id, fullBotResponse, 'assistant', newMessages[1].id, newMessages[1].feedback);
                        }
                        // Refresh from backend (for canonical ordering/metadata)
                        await fetchUserMessages(currentConversation.conversation_id);
                    }
                    break;
                }
            }
        } catch (err) {
            console.error("Streaming failed:", err);
            setBotResponse("No quota to generate answer!");
        }
    };

    /**
     * Submit 👍/👎 feedback for an assistant message.
     */
    const handleUserFeedback = async (message_index: string, conversation_id: string, feedback: boolean, e?: React.MouseEvent) => {
        e?.preventDefault();
        try {
            await userFeedback(message_index, conversation_id, feedback);
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === message_index ? { ...m, feedback } : m
                )
            );
        } catch (err) {
            console.log("Something went wrong with the feedback");
        }
    }

    /**
     * Rename a conversation (inline edit).
     */
    const handleRename = async (conversationId: string) => {
        if (!editedTitle.trim()) {
            setEditingConvId('');
            return;
        }
        console.log(conversationId, editedTitle.trim());
        await renameConversation(conversationId, editedTitle.trim());

        // Optimistically update local conversation list label
        if (conversations) {
            for (let i = 0; i < conversations.length; i++) {
                const conv = conversations[i];
                if (
                    conv &&
                    conv.conversation_id &&
                    conv.conversation_name &&
                    conv.conversation_id === conversationId
                ) {
                    conv.conversation_name = editedTitle.trim();
                    break;
                }
            }
        }

        setEditingConvId('');

    }

    /**
    * Create a new conversation with a default name.
    */
    const createNewConversation = async () => {
        if (user) {
            const conversation_name = `Conversation ${conversations?.length || 0}`;
            const newConv = await createConversation(conversation_name, user?.username);
            if (newConv) {
                setCurrentConversation(newConv);
                setMessages([]);
            }

        }
    };

    /**
     * Select conversation and fetch messages for it.
     */
    const getMessagesFromConversations = async (conversation_id: string, conversation_name: string) => {
        setCurrentConversation({ conversation_id: conversation_id, conversation_name: conversation_name });
        await fetchUserMessages(conversation_id);
    };

    /**
     * Logout and redirect to login.
     */
    const logoutButton = async () => {
        await logoutUser();
        navigate('/login');
    };

    // -------------------------
    // Render
    // -------------------------
    return (
        <div className="flex h-screen bg-gray-100 text-gray-800 relative">
            {/* Overlay for mobile sidebar */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 z-10 bg-black/40 backdrop-blur-sm md:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
      fixed md:relative top-0 left-0 w-64 bg-white border-r z-20
      transform transition-transform duration-200 ease-in-out
      flex flex-col h-full md:h-screen
      ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0
    `}>
                <div className="p-4 flex flex-col h-full">
                    {/* <div className='mb-4'>
                        <input
                            type='text'
                            value = {conversationTitle}
                            onChange = {(e) => setConversationTitle(e.target.value)}
                            placeholder='Name you conversation'
                            className='w-full mb-2 p-2 border rounded text-sm'
                        />
                        <button
                            onClick={() => createNewConversation(conversationTitle)}
                            className="w-full mb-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            + New Conversation
                        </button>

                    </div>
                     */}

                    <button
                        onClick={createNewConversation}
                        className="w-full mb-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        + New Conversation
                    </button>

                    <ul className="space-y-2 overflow-y-auto flex-1">

                        {conversations?.map((conv) => (
                            <li key={conv.conversation_id}
                                onClick={() => {
                                    if (editingConvId !== conv.conversation_id) {
                                        setSidebarOpen(false);
                                        getMessagesFromConversations(conv.conversation_id, conv.conversation_name);
                                    }
                                }}
                                onDoubleClick={() => {
                                    setEditingConvId(conv.conversation_id);
                                    setEditedTitle(conv.conversation_name);
                                }}
                                className={`p-2 cursor-pointer rounded ${conv.conversation_id === currentConversation.conversation_id
                                    ? 'bg-blue-100 font-semibold'
                                    : 'hover:bg-gray-200'
                                    }`}>
                                {editingConvId === conv.conversation_id ? (
                                    <input
                                        value={editedTitle}
                                        onChange={(e) => setEditedTitle(e.target.value)}
                                        onBlur={() => handleRename(conv.conversation_id)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') handleRename(conv.conversation_id);
                                            if (e.key === 'Escape') setEditingConvId('');
                                        }}
                                        autoFocus
                                        className="w-full p-1 border rounded text-sm"
                                    />
                                ) : (
                                    conv.conversation_name
                                )}
                            </li>



                        ))}

                        {/* {conversations?.map((conv) => (
                            <li
                                key={conv.conversation_id}
                                onClick={() => {
                                    setSidebarOpen(false);
                                    getMessagesFromConversations(conv.conversation_id, conv.conversation_name);
                                }}
                                className={`p-2 cursor-pointer rounded ${conv.conversation_id === currentConversation.conversation_id
                                    ? 'bg-blue-100 font-semibold'
                                    : 'hover:bg-gray-200'
                                    }`}
                            >
                                {conv.conversation_name}
                            </li>
                        ))} */}
                    </ul>

                    <button
                        onClick={logoutButton}
                        className="p-2 bg-red-500 text-white rounded hover:bg-red-600 mt-4"
                    >
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col z-0 items-center">
                {/* Mobile Header */}
                <div className="md:hidden flex justify-between items-center p-4 bg-white shadow w-full">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)}>
                        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                    <h1 className="text-lg font-bold">AILA INTERFACE DEMO</h1>
                </div>

                {/* Desktop Title */}
                <h1 className="text-xl font-bold text-center mt-4 mb-2 hidden md:block">
                    AILA INTERFACE DEMO
                </h1>

                {/* Welcome Message */}
                {/* {user?.username && (
                    <div className="text-sm md:text-base text-gray-700 text-center mb-4">
                        Welcome, <span className="font-semibold text-blue-700">{user.username}</span>
                    </div>
                )} */}

                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="text-sm md:text-base text-gray-700 text-center mb-4"
                >
                    Welcome, <span className="font-semibold text-blue-700">{user?.username}</span>
                </motion.div>

                {/* Chat Container */}
                <div ref={chatRef} className="flex-1 w-full max-w-4xl px-6 overflow-y-auto">
                    <div className="bg-white rounded-lg shadow p-4 space-y-4">
                        {currentConversation ? (
                            <ul className="space-y-4">
                                {messages.map((mes) => (
                                    <li
                                        key={mes.id}
                                        className={`flex flex-col gap-1 ${mes.role === 'user' ? 'items-end' : 'items-start'}`}
                                    >
                                        <div className="flex items-center gap-2">
                                            <div className="mt-1">
                                                {mes.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                                            </div>
                                            <div className={`px-5 py-4 rounded-md shadow-sm text-sm whitespace-pre-line text-sm md:text-base lg:text-lg ${mes.role === 'user'
                                                ? 'bg-blue-100 text-blue-800'
                                                : 'bg-gray-200 text-gray-800'
                                                }`}>
                                                {mes.message}
                                            </div>
                                        </div>

                                        {/* Feedback aligned right */}
                                        {mes.role === 'assistant' && mes.id && currentConversation?.conversation_id && (
                                            <div className="flex justify-end w-full pr-10 mt-1">
                                                <button
                                                    type="button"
                                                    disabled={mes.feedback === false}
                                                    onClick={(e) => handleUserFeedback(mes.id, currentConversation.conversation_id, false, e)}
                                                    // className={`text-xs md:text-sm lg:text-base ${mes.feedback === false
                                                    //     ? 'text-red-600 font-bold'
                                                    //     : 'text-gray-400 hover:text-red-500'
                                                    //     } disabled:opacity-50 mr-2`}
                                                    className={`text-xs md:text-sm lg:text-base
                                                        ${mes.feedback === true ? 'text-red-600 font-bold' : 'text-gray-400'}
                                                        ${mes.feedback === true ? 'cursor-not-allowed opacity-50' : 'hover:text-red-500'}
                                                    `}
                                                    title="Thumbs down"
                                                >
                                                    👎
                                                </button>
                                                <button
                                                    type="button"
                                                    disabled={mes.feedback === true}
                                                    onClick={(e) => handleUserFeedback(mes.id, currentConversation.conversation_id, true, e)}
                                                    // className={`text-sm md:text-sm lg:text-base ${mes.feedback === true
                                                    //     ? 'text-green-600 font-bold'
                                                    //     : 'text-gray-400 hover:text-green-500'
                                                    //     } disabled:opacity-50`}
                                                    className={`text-xs md:text-sm lg:text-base
                                                    ${mes.feedback === false ? 'text-green-600 font-bold' : 'text-gray-400'}
                                                    ${mes.feedback === false ? 'cursor-not-allowed opacity-50' : 'hover:text-green-500'}
                                                    `}
                                                    title="Thumbs up"
                                                >
                                                    👍
                                                </button>
                                            </div>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="text-gray-500">Select or create a conversation</div>
                        )}
                    </div>
                </div>

                {/* Error Message */}
                {botResponse && (
                    <div className="mb-2 text-red-500 px-4">{botResponse}</div>
                )}

                {/* Input */}
                {currentConversation && (
                    <form onSubmit={handleSubmit} className="flex w-full max-w-4xl p-5 bg-white border-t">
                        <input
                            type="text"
                            value={userQuery}
                            onChange={(e) => setUserQuery(e.target.value)}
                            className="flex-1 border border-gray-300 rounded-l-md p-4 text-sm md:text-base lg:text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Type your message here..."
                            required
                        />
                        <button
                            type="submit"
                            className="px-8 py-3 bg-blue-600 text-white font-semibold text-sm md:text-base lg:text-lg rounded-r-md hover:bg-blue-700 transition"
                        >
                            Submit
                        </button>
                    </form>
                )}
            </div>
        </div>
    );


};

export default Chat;
