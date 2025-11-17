
import { useRef } from 'react';
import { User, Bot, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.tsx';
import UseChatLogic from './funcs.ts';
import { useChat } from '../../context/ChatPageContext.tsx';

const InlineSpinner = () => (
    <span
        className="inline-flex items-center gap-2 text-gray-600 text-sm leading-6 max-w-full"
        aria-live="polite"
    >
        <Loader2 className="animate-spin w-4 h-4 shrink-0" aria-hidden="true" />
        <span className="break-words" > Preparing Answer...</span>
    </span >
);



const ChatContainer = () => {

    const {
        handleUserFeedback,
    } = UseChatLogic();

    const {
        setmessageFeedbackDetails,
        currentConversation,
        userMessages, isStreaming,
        setFeedbackFormOpen
    } = useChat();

    const { user } = useAuth();

    const chatRef = useRef<HTMLDivElement | null>(null);

    console.log(currentConversation)

    return (
        <div
            ref={chatRef}
            className="flex-1 w-full px-3 sm:px-4 md:px-6 overflow-y-auto overflow-x-hidden"
        >
            <div className="mx-auto w-full max-w-full sm:max-w-3xl lg:max-w-5xl xl:max-w-6xl">
                <div className="bg-white rounded-lg shadow p-3 sm:p-4 space-y-3 sm:space-y-4">
                    {currentConversation ? (
                        <ul className="space-y-3 sm:space-y-4">
                            {userMessages?.map((mes, index) => (
                                <li
                                    key={mes.id}
                                    className={`flex flex-col gap-1 ${mes.role === 'user' ? 'items-end' : 'items-start'}`}
                                >
                                    <div className="flex items-start sm:items-center gap-2 max-w-full">
                                        <div className="mt-0.5 sm:mt-1 shrink-0">
                                            {mes.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                                        </div>
                                        <div
                                            className={`px-4 py-3 rounded-md shadow-sm text-xs sm:text-sm md:text-base whitespace-pre-line break-words max-w-[85vw] sm:max-w-[70vw] md:max-w-[60vw] ${mes.role === 'user'
                                                ? 'bg-blue-100 text-blue-800'
                                                : 'bg-gray-200 text-gray-800'
                                                }`}
                                        >
                                            {mes.role === 'assistant' ? (
                                                (() => {
                                                    const isLastAssistant =
                                                        userMessages?.length > 0 &&
                                                        userMessages[userMessages.length - 1]?.id === mes.id &&
                                                        mes.role === 'assistant';

                                                    const hasStarted = !!mes.message;

                                                    if (isStreaming && isLastAssistant && !hasStarted) {
                                                        return <InlineSpinner />;
                                                    }

                                                    if (isStreaming && isLastAssistant && hasStarted) {
                                                        return (
                                                            <span>
                                                                {mes.message}
                                                                <span className="inline-block align-baseline w-[0.6ch] animate-pulse">▍</span>
                                                            </span>
                                                        );
                                                    }

                                                    return mes.message;
                                                })()
                                            ) : (
                                                mes.message
                                            )}
                                        </div>
                                    </div>

                                    {/* Feedback row */}
                                    {mes.role === 'assistant' && user?.role === 'user' && mes.id && currentConversation?.conversation_id && (
                                        <div className="flex justify-end w-full pr-4 sm:pr-6 mt-1">
                                            <button
                                                type="button"
                                                disabled={mes.feedback === false}
                                                onClick={(e) => handleUserFeedback(mes.id, currentConversation.conversation_id, false, e)}
                                                aria-pressed={mes.feedback === false}
                                                aria-label="Mark as unhelpful"
                                                className={`text-xs sm:text-sm md:text-base mr-3 transition-colors ${mes.feedback === false
                                                    ? 'text-red-600 font-bold cursor-default'
                                                    : (mes.feedback !== null)
                                                        ? 'text-gray-600 opacity-50 hover:opacity-100 hover:text-red-500 cursor-pointer'
                                                        : 'text-gray-600 hover:text-red-500 cursor-pointer'
                                                    }`}
                                                title="Thumbs down"
                                            >
                                                👎
                                            </button>
                                            <button
                                                type="button"
                                                disabled={mes.feedback === true}
                                                onClick={(e) => handleUserFeedback(mes.id, currentConversation.conversation_id, true, e)}
                                                aria-pressed={mes.feedback === true}
                                                aria-label="Mark as helpful"
                                                className={`text-xs sm:text-sm md:text-base mr-3 transition-colors ${mes.feedback === true
                                                    ? 'text-red-600 font-bold cursor-default'
                                                    : (mes.feedback !== null)
                                                        ? 'text-gray-600 opacity-50 hover:opacity-100 hover:text-red-500 cursor-pointer'
                                                        : 'text-gray-600 hover:text-red-500 cursor-pointer'
                                                    }`}
                                                title="Thumbs up"
                                            >
                                                👍
                                            </button>
                                        </div>
                                    )}

                                    {mes.role === 'assistant' && user?.role === 'lawyer' && mes.id && currentConversation?.conversation_id && (
                                        <div className="flex justify-end w-full pr-4 sm:pr-6 mt-1">
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setmessageFeedbackDetails(prev => ({
                                                        ...prev,
                                                        message_id: mes.id,
                                                        conversation_id: currentConversation.conversation_id,
                                                        query_id: userMessages[index - 1].id,
                                                        generated_answer_id: mes.id
                                                    }))
                                                    setFeedbackFormOpen(true);
                                                }}
                                                className="px-3 py-1 bg-blue-600 text-white text-xs sm:text-sm md:text-base rounded-lg shadow hover:bg-blue-700 transition-colors"
                                            >
                                                Feedback
                                            </button>
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <div className="text-gray-500 text-sm sm:text-base">Select or create a conversation</div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ChatContainer;
