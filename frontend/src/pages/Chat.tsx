import { Menu, X } from 'lucide-react';
import { motion } from "framer-motion";
import SideBar from '../funcs/chat_utils/sidebar';
import FeedbackDoc from '../funcs/chat_utils/feedback_doc';
import ChatContainer from '../funcs/chat_utils/chat_container';
import Submission from '../funcs/chat_utils/submission';
import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useChat } from '../context/ChatPageContext';
import UseChatLogic from '../funcs/chat_utils/funcs';

const Chat = () => {

    const {
        user,
    } = useAuth();

    const {
        conversations,
        fetchConversations,
        fetchUserMessages,
        setCurrentConversation, currentConversation,
    } = useChat();

    const {
        setSidebarOpen, sidebarOpen
    } = UseChatLogic();


    useEffect(() => {
        if (!user) return;
        if (conversations?.length == 0) {
            fetchConversations(user.username);
        }
    }, [user?.username])

    useEffect(() => {
        if (!user || !conversations?.length) return;
        if (conversations?.length && user) {
            setCurrentConversation(conversations[0]);
            fetchUserMessages(user.username, conversations[0].conversation_id)
        }
    }, [conversations])

    useEffect(() => {
        if (!user || !currentConversation.conversation_id) return;
        fetchUserMessages(user.username, currentConversation.conversation_id);
    }, [currentConversation.conversation_id])

    // useEffect(() => {
    //     setMessages(userMessages ?? []);
    // }, [userMessages])

    return (
        <div className="flex flex-col md:flex-row min-h-[100dvh] md:h-screen bg-gray-100 text-gray-800 relative overflow-x-hidden">

            {/* Feedback Modal (unchanged logic, just better responsive spacing) */}
            <FeedbackDoc />

            {/* Overlay for mobile sidebar */}

            {/* Sidebar */}
            <SideBar />

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col z-0 items-center md:pl-0">
                {/* Mobile Header */}
                <div className="md:hidden flex justify-between items-center p-3 sm:p-4 bg-white shadow w-full sticky top-0 z-10">
                    <button onClick={() => setSidebarOpen(!sidebarOpen)}>
                        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                    <h1 className="text-base sm:text-lg font-bold">AILA INTERFACE DEMO</h1>
                    <div className="w-6" /> {/* spacer */}
                </div>

                {/* Desktop Title */}
                <h1 className="text-lg md:text-xl font-bold text-center mt-3 md:mt-4 mb-2 hidden md:block">
                    AILA INTERFACE DEMO
                </h1>

                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="text-xs sm:text-sm md:text-base text-gray-700 text-center mb-3 md:mb-4 px-3"
                >
                    Welcome, <span className="font-semibold text-blue-700">{user?.username}</span>
                </motion.div>

                {/* Chat Container */}
                <ChatContainer />

                {/* Error Message */}


                {/* Composer (sticky on mobile) */}
                {currentConversation && (
                    <Submission />
                )}
            </div>
        </div>
    );

};

export default Chat;