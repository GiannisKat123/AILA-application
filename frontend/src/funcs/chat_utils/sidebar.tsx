import { useState } from 'react';
import UseChatLogic from './funcs.ts';
import { useChat } from '../../context/ChatPageContext.tsx';

const SideBar = () => {
    const {
        createNewConversation,
        getMessagesFromConversations,
        handleRename,
        logoutButton,
    } = UseChatLogic();

    const {
        setSidebarOpen,
        sidebarOpen
    } = useChat();

    const { conversations, currentConversation } = useChat();
    const [editingConvId, setEditingConvId] = useState('');
    const [editConvTitle, setEditedTitle] = useState('');

    return (
        <>
            {sidebarOpen && (
                <div className="fixed inset-0 z-10 bg-black/40 backdrop-blur-sm md:hidden" onClick={() => setSidebarOpen(false)} />
            )}

            <aside
                className={`fixed md:relative top-0 left-0 w-64 md:w-72 bg-white border-r z-20
                            transform transition-transform duration-200 ease-in-out
                            flex flex-col h-[100dvh] md:h-screen
                ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}
            >
                <div className="p-3 sm:p-4 flex flex-col h-full">
                    <h2 className="font-semibold mb-2 text-center text-sm sm:text-base">Tools</h2>
                    <hr className="my-2 border-gray-300" />

                    <button
                        onClick={() => createNewConversation('lawsuit')}
                        className="w-full mb-3 sm:mb-4 p-2 bg-gradient-to-r from-blue-600 to-blue-400 text-white font-bold rounded-lg shadow hover:from-blue-700 hover:to-blue-500 transition text-sm sm:text-base"
                    >
                        ⚖️ Build Lawsuit
                    </button>

                    <hr className="my-2 border-gray-300" />
                    <button
                        onClick={() => createNewConversation('normal')}
                        className="w-full mb-3 sm:mb-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm sm:text-base"
                    >
                        New Conversation
                    </button>

                    <ul className="space-y-2 overflow-y-auto flex-1">
                        {(conversations ?? []).map((conv) => (
                            <li
                                key={conv.conversation_id}
                                onClick={() => {
                                    if (editingConvId !== conv.conversation_id) {
                                        setSidebarOpen(false);
                                        getMessagesFromConversations(conv);
                                    }
                                }}
                                onDoubleClick={() => {
                                    setEditingConvId(conv.conversation_id);
                                    setEditedTitle(conv.conversation_name);
                                }}
                                className={`p-2 cursor-pointer rounded text-sm sm:text-base ${conv.conversation_id === currentConversation.conversation_id
                                    ? "bg-blue-100 font-semibold"
                                    : "hover:bg-gray-200"
                                    }`}
                            >
                                {editingConvId === conv.conversation_id ? (
                                    <input
                                        value={editConvTitle}
                                        onChange={(e) => setEditedTitle(e.target.value)}
                                        onBlur={async () => {
                                            await handleRename(conv.conversation_id, editConvTitle);
                                            setEditingConvId('');
                                        }}
                                        onKeyDown={async (e) => {
                                            if (e.key === "Enter") {
                                                await handleRename(conv.conversation_id, editConvTitle);
                                                setEditingConvId('');
                                            }
                                            if (e.key === "Escape") setEditingConvId('');
                                        }}
                                        autoFocus
                                        className="w-full p-1 border rounded text-sm"
                                    />
                                ) : (
                                    conv.conversation_name
                                )}
                            </li>
                        ))}
                    </ul>

                    <button
                        onClick={logoutButton}
                        className="p-2 bg-red-500 text-white rounded hover:bg-red-600 mt-4 text-sm sm:text-base"
                    >
                        Logout
                    </button>
                </div>
            </aside>

        </>
    )
}

export default SideBar;
