import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import type { Message } from '../models/Types';
import { Menu, X, User, Bot } from 'lucide-react'; // install `lucide-react` or use your preferred icon library

const Chat = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [userQuery, setUserQuery] = useState('');
    const [botResponse, setBotResponse] = useState('');
    const [currentConversation, setCurrentConversation] = useState('');
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { user, userMessages, logoutUser, fetchUserMessages, conversations, createConversation, createMessage, fetchConversations } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (user) fetchConversations(user.username);
    }, []);

    useEffect(() => {
        if (conversations?.length) {
            const initial = conversations[0];
            setCurrentConversation(initial);
            fetchUserMessages(initial);
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
            { message: userMessage, role: 'user', timestamp: now },
            { message: '', role: 'assistant', timestamp: now }
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
                body: JSON.stringify({ message: userMessage })
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
                    await createMessage(currentConversation, userMessage, 'user');
                    await createMessage(currentConversation, fullBotResponse, 'assistant');
                    await fetchUserMessages(currentConversation);
                    break;
                }
            }
        } catch (err) {
            console.error("Streaming failed:", err);
            setBotResponse("Streaming failed");
        }
    };

    const createNewConversation = async () => {
        if (user) {
            const conversation_name = `Conversation ${conversations?.length}`;
            await createConversation(conversation_name, user?.username);
            setCurrentConversation(conversation_name);
            setMessages([]);
        }
    };

    const getMessagesFromConversations = async (conversation_name: string) => {
        setCurrentConversation(conversation_name);
        await fetchUserMessages(conversation_name);
    };

    const logoutButton = async () => {
        await logoutUser();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100 text-gray-800 relative">
            {/* Overlay when sidebar is open on mobile */}
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
                    <button
                        onClick={createNewConversation}
                        className="w-full mb-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        + New Conversation
                    </button>

                    <ul className="space-y-2 overflow-y-auto flex-1">
                        {conversations?.map((conversation_name, index) => (
                            <li
                                key={index}
                                onClick={() => {
                                    setSidebarOpen(false);
                                    getMessagesFromConversations(conversation_name);
                                }}
                                className={`p-2 cursor-pointer rounded ${conversation_name === currentConversation
                                    ? 'bg-blue-100 font-semibold'
                                    : 'hover:bg-gray-200'
                                    }`}
                            >
                                {conversation_name}
                            </li>
                        ))}
                    </ul>

                    <button
                        onClick={logoutButton}
                        className="p-2 bg-red-500 text-white rounded hover:bg-red-600 mt-4"
                    >
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main chat area */}
            <div className="flex-1 flex flex-col z-0">
                {/* Top Nav (mobile only) */}
                <div className="md:hidden flex justify-between items-center p-4 bg-white shadow">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)}>
                        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                    <h1 className="text-lg font-bold">AILA INTERFACE DEMO</h1>
                </div>

                {/* Desktop title */}
                <h1 className="text-xl font-bold text-center mt-4 mb-2 hidden md:block">
                    AILA INTERFACE DEMO
                </h1>

                {/* Chat messages */}
                <div className="flex-1 overflow-y-auto p-4">
                    <div className="bg-white rounded-lg shadow p-4 space-y-4">
                        {currentConversation ? (
                            <ul className="space-y-4">
                                {messages.map((mes, index) => (
                                    <li
                                        key={index}
                                        className={`flex items-start gap-2 max-w-3xl ${mes.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                                            }`}
                                    >
                                        <div className="mt-1">
                                            {mes.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                                        </div>
                                        <div className={`px-4 py-3 rounded-md shadow-sm text-sm whitespace-pre-line ${mes.role === 'user'
                                            ? 'bg-blue-100 text-right'
                                            : 'bg-gray-200 text-left'
                                            }`}>
                                            {mes.message}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <div className="text-gray-500">Select or create a conversation</div>
                        )}
                    </div>
                </div>

                {/* Bot error */}
                {botResponse && (
                    <div className="mb-2 text-red-500 px-4">{botResponse}</div>
                )}

                {/* Input box */}
                {currentConversation && (
                    <form onSubmit={handleSubmit} className="flex p-4 bg-white border-t">
                        <input
                            type="text"
                            value={userQuery}
                            onChange={(e) => setUserQuery(e.target.value)}
                            className="flex-1 border border-gray-300 rounded-l-md p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Type your message here..."
                            required
                        />
                        <button
                            type="submit"
                            className="px-6 bg-blue-600 text-white font-semibold rounded-r-md hover:bg-blue-700 transition"
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
