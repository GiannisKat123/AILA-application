import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { v4 as uuidv4 } from 'uuid';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import type { Message, Conversations } from '../models/Types';
import { Menu, X, User, Bot } from 'lucide-react'; // install `lucide-react` or use your preferred icon library
import { motion } from "framer-motion";


const Chat = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [userQuery, setUserQuery] = useState('');
    const [botResponse, setBotResponse] = useState('');
    const [currentConversation, setCurrentConversation] = useState<Conversations>({
        conversation_name: '',
        conversation_id: ''
    });
    const [editingConvId, setEditingConvId] = useState('');
    const [editedTitle, setEditedTitle] = useState('');
    // const [conversationTitle,setConversationTitle] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { user, userMessages, userFeedback, logoutUser, fetchUserMessages, conversations, createConversation, createMessage, fetchConversations, renameConversation } = useAuth();
    const navigate = useNavigate();
    const chatRef = useRef<HTMLDivElement | null>(null);


    useEffect(() => {
        if (user) fetchConversations(user.username);
    }, [user]);

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollIntoView({ behavior: 'smooth' })
        }
    }, [userMessages])

    useEffect(() => {
        if (conversations?.length) {
            const initial = conversations[0];
            setCurrentConversation(initial);
            fetchUserMessages(initial.conversation_id);
        }
    }, [conversations]);

    useEffect(() => {
        setMessages(userMessages ?? []);
    }, [userMessages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const userMessage = userQuery.trim();
        if (!userMessage) return;

        const now = new Date().toISOString();
        const newMessages = [
            { message: userMessage, role: 'user', timestamp: now, id: uuidv4(), feedback: null },
            { message: '', role: 'assistant', timestamp: now, id: uuidv4(), feedback: null }
        ];

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

            while (true) {
                const { value, done } = await reader.read();
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const jsonStr = line.replace("data: ", "");
                        const parsed = JSON.parse(jsonStr);
                        fullBotResponse += parsed.response;

                        setMessages(prev => {
                            const updated = [...prev];
                            const lastIndex = updated.length - 1;
                            updated[lastIndex].message = fullBotResponse;
                            updated[lastIndex].timestamp = new Date().toISOString();
                            return updated;
                        });
                    } catch (err) {
                        console.error("Invalid chunk", err);
                    }
                }

                if (done) {
                    await createMessage(currentConversation.conversation_id, userMessage, 'user', newMessages[0].id, newMessages[0].feedback);
                    await createMessage(currentConversation.conversation_id, fullBotResponse, 'assistant', newMessages[1].id, newMessages[1].feedback);
                    await fetchUserMessages(currentConversation.conversation_id);
                    break;
                }
            }
        } catch (err) {
            console.error("Streaming failed:", err);
            setBotResponse("No quota to generate answer!");
        }
    };

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


    // const createNewConversation = async (name:string) => {
    //     if (user) {
    //         const conversation_name = name || `Conversation ${conversations?.length || 0}`;
    //         const newConv = await createConversation(conversation_name, user?.username);
    //         if (newConv) {
    //             setCurrentConversation(newConv);
    //             setMessages([]);
    //         }
    //         // setConversationTitle('');

    //     }
    // };

    const handleRename = async (conversationId: string) => {
        if (!editedTitle.trim()) {
            setEditingConvId('');
            return;
        }
        console.log(conversationId, editedTitle.trim());
        await renameConversation(conversationId, editedTitle.trim());

        if (conversations) {
            for (let i = 0; i < (conversations?.length ?? 0); i++) {
                if (conversations[i] !== null && conversations[i].conversation_id === conversationId) {
                    conversations[i].conversation_name = editedTitle.trim();
                    break;
                }
            }
        }


        // const conversations = conversations?.map(conv =>
        //     conv.conversation_id === conversationId ? {...conv, conversation_name:editedTitle.trim()} : conv
        // );

        // setCurrentConversation(updated);

        setEditingConvId('');

    }

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

    const getMessagesFromConversations = async (conversation_id: string, conversation_name: string) => {
        setCurrentConversation({ conversation_id: conversation_id, conversation_name: conversation_name });
        await fetchUserMessages(conversation_id);
    };

    const logoutButton = async () => {
        await logoutUser();
        navigate('/login');
    };

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
