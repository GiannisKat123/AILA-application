import { useRef } from 'react';
import UseChatLogic from './funcs.ts';
import { useChat } from '../../context/ChatPageContext.tsx';

const Submission = () => {

    const {
        handleSubmit,
        handleTextareaKeyDown,
        onSelect,
    } = UseChatLogic();

    const {
        currentConversation, uploadedFiles, setUploadedFiles, userQuery, setUserQuery,
        setOnlineMode, isStreaming, isOnline
    } = useChat();

    const inputRef = useRef<HTMLInputElement | null>(null);
    function openFileDialog() {
        inputRef.current?.click();
    }

    return (
        <form
            onSubmit={handleSubmit}
            className="w-full bg-white border-t sticky bottom-0 z-10 pb-[env(safe-area-inset-bottom)]"
        >
            <div className="mx-auto max-w-full sm:max-w-3xl lg:max-w-5xl xl:max-w-6xl p-3 sm:p-4">
                {/* Stack on mobile; row on desktop */}
                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch">
                    <textarea
                        value={userQuery}
                        onChange={(e) => setUserQuery(e.target.value)}
                        onKeyDown={handleTextareaKeyDown}
                        onInput={(e) => {
                            const el = e.currentTarget;
                            el.style.height = '0px';
                            el.style.height = el.scrollHeight + 'px';
                        }}
                        rows={1}
                        placeholder="Type your message here..."
                        required
                        className="flex-1 min-w-0 border border-gray-300 rounded-md p-3 sm:p-4 text-sm sm:text-base
                   focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none leading-6
                   max-h-40 sm:max-h-48 overflow-y-auto break-words"
                    />

                    {/* Buttons: full-width stacked on mobile; inline on desktop, no wrap */}
                    <div className="w-full sm:w-auto flex flex-col md:flex-row flex-nowrap gap-2 sm:gap-3 sm:self-end">
                        <button
                            type="submit"
                            className={`w-full md:w-auto h-12 px-5 rounded-xl font-semibold text-sm sm:text-base shadow-sm
            focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
            active:translate-y-px touch-manipulation transition border shrink-0
            ${isStreaming
                                    ? 'bg-blue-300 text-white cursor-not-allowed border-blue-300'
                                    : 'bg-blue-600 text-white hover:bg-blue-700 border-blue-600'}`}
                        >
                            {isStreaming ? 'Sending…' : 'Submit'}
                        </button>

                        {currentConversation.conversation_type === 'lawsuit' && (
                            <div className="flex flex-col gap-2 w-full md:w-auto shrink-0">
                                <input
                                    type="file"
                                    ref={inputRef}
                                    multiple
                                    accept="image/*,audio/mpeg,audio/wav,application/pdf,.txt,.csv"
                                    onChange={onSelect}
                                    hidden
                                />
                                <button
                                    type="button"
                                    onClick={openFileDialog}
                                    className="w-full md:w-auto h-12 px-5 rounded-xl font-semibold text-sm sm:text-base shadow-sm
                         focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
                         active:translate-y-px touch-manipulation transition border
                         bg-blue-600 text-white border-blue-600 hover:bg-blue-700"
                                >
                                    Upload Files
                                </button>

                                {!!uploadedFiles?.length && (
                                    <ul className="max-h-24 sm:max-h-32 overflow-auto text-xs border rounded-md p-2 space-y-1 w-full md:w-64">
                                        {uploadedFiles.map((f, i) => (
                                            <li key={i} className="flex items-center justify-between gap-2">
                                                <span className="truncate">{f.name}</span>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-gray-500">
                                                        {(f.size / (1024 * 1024)).toFixed(2)} MB
                                                    </span>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            setUploadedFiles((prev) => prev.filter((_, idx) => idx !== i))
                                                        }
                                                        className="px-2 py-1 border text-xs rounded hover:bg-gray-50"
                                                    >
                                                        remove
                                                    </button>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        )}

                        {currentConversation.conversation_type === 'normal' && (
                            <button
                                type="button"
                                onClick={() => setOnlineMode(!isOnline)}
                                aria-pressed={isOnline}
                                className={`w-full md:w-auto h-12 px-5 rounded-xl font-semibold text-sm sm:text-base shadow-sm
                        focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
                        active:translate-y-px touch-manipulation transition border shrink-0
                        ${isOnline
                                        ? 'bg-white text-gray-900 border-gray-300 hover:bg-gray-50'
                                        : 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'}`}
                            >
                                {isOnline ? 'RAG Mode' : 'Online Mode'}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </form>
    )
}

export default Submission;