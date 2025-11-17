import { useRef, useState } from "react";
import type { Conversation } from "../../models/Types";
import * as pdfjsLib from "pdfjs-dist";
import workerSrc from "pdfjs-dist/build/pdf.worker.min.mjs?url";
import { useNavigate } from "react-router";
import api from "../../api/axios";
import mammoth from "mammoth";
import { useAuth } from "../../context/AuthContext";
import { useChat } from "../../context/ChatPageContext";

const handlePdfFile = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                if (!e.target) return;
                const typedArray = new Uint8Array(e.target.result as ArrayBuffer);
                const pdf = await pdfjsLib.getDocument(typedArray).promise;
                let text = "";
                for (let i = 1; i <= pdf.numPages; i += 1) {
                    const page = await pdf.getPage(i);
                    const content = await page.getTextContent();
                    const pageText = content.items.map((s) => ('str' in s ? (s as { str: string }).str : '')).join(" ");
                    text += `\n${pageText}`;
                }
                resolve(text);
            } catch (err) {
                reject(err);
            }
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
};

const handleDocxFile = async (file: File): Promise<string> => {
    const arrayBuffer = await file.arrayBuffer();
    const { value: text } = await mammoth.extractRawText({ arrayBuffer });
    return text;
}

const UseChatLogic = () => {
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc;
    const [botResponse, setBotResponse] = useState("");

    const {
        user,
        logoutUser
    } = useAuth();

    const {
        fetchUserMessages,
        createAutomatedMessage,
        createMessage,
        conversations, setConversations,
        createConversation,
        renameConversation,
        userMessages, setMessages,
        userFeedback,
        createDocumentFeedback,
        currentConversation, setCurrentConversation,
        uploadedFiles, setUploadedFiles,
        messageFeedbackDetails,
        isOnline, setOnlineMode,
        isStreaming, setStreaming,
        sidebarOpen, setSidebarOpen,
        userQuery, setUserQuery,
        setFeedbackFormOpen

    } = useChat();


    const navigate = useNavigate();
    const controllerRef = useRef<AbortController | null>(null);

    const createAutomatedBotMessage = async (conversation_id: string, conversation_name: string, conversation_type: string) => {
        const automated_message = await createAutomatedMessage(conversation_id, conversation_name, conversation_type);
        if (typeof automated_message === 'string' && user) {
            await createMessage(user.username, conversation_id, automated_message, 'assistant', undefined);
        }
        else {
            console.error('Invalid conversation_id for createAutomatedBotMessage');
        }

    }

    const createNewConversation = async (conversation_type: string) => {
        if (!user) return;

        const conversation_name = `${conversation_type} Conversation ${conversations?.length || 0}`;
        console.log("NEW CONVERSATION", user?.username, conversation_name, conversation_type)
        const newConv = await createConversation(user?.username, conversation_name, conversation_type);

        if (newConv) {
            setCurrentConversation(newConv);
            setMessages([]); // local clear
            if (conversation_type === 'lawsuit') {
                createAutomatedBotMessage(newConv.conversation_id, newConv.conversation_name, conversation_type);
            }
            await Promise.all([
                fetchUserMessages(user.username, newConv.conversation_id),
                // fetchConversations(user.username),
            ]);
        }
    };

    const getMessagesFromConversations = async (conversation: Conversation) => {
        if (!user) return;
        await fetchUserMessages(user.username, conversation.conversation_id);
        setCurrentConversation(conversation);
    };

    const handleRename = async (conversationId: string, editedTitle: string) => {
        if (!editedTitle.trim() || !user) {
            return;
        }
        console.log("rename Conversation 2", user.username, conversationId, editedTitle.trim())
        await renameConversation(user.username, conversationId, editedTitle.trim());

        if (conversations) {
            for (let i = 0; i < (conversations?.length ?? 0); i++) {
                if (conversations[i] !== null && conversations[i].conversation_id === conversationId) {
                    conversations[i].conversation_name = editedTitle.trim();
                    break;
                }
            }
        }
    }

    const logoutButton = async () => {
        setConversations([]);
        setMessages([]);
        setCurrentConversation({
            conversation_name: '', conversation_id: '', conversation_type: ''
        });
        await logoutUser();
        navigate('/login');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const userMessage = userQuery.trim();
        if (!userMessage) return;
        try {
            if (currentConversation.conversation_name == '' && user) {
                let newConv = await createConversation(user.username, `Conversation ${conversations?.length || 0}`, 'normal');
                if (newConv) {
                    setCurrentConversation(newConv);
                }
                // fetchConversations(user.username);
            }
            const now = new Date().toISOString();
            const newMessages = [
                { message: userMessage, role: 'user', timestamp: now, id: '1', feedback: undefined },
                { message: '', role: 'assistant', timestamp: now, id: '2', feedback: undefined },
            ]
            setMessages(prev => [...(prev ?? []), ...newMessages]);
            setUserQuery('');
            setBotResponse('');

            const controller = new AbortController();
            controllerRef.current = controller;
            setStreaming(true);

            if (userMessages?.length == 0 && user) {
                const restitle = await fetch(`${api.defaults.baseURL}/get_ai_conversation_title`, {
                    method: "POST",
                    signal: controller.signal,
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text: userMessage, role: 'user', conversation_id: currentConversation.conversation_id, message_id: undefined, feedback: undefined, username: user.username }), // no JSON.stringify, no Content-Type header
                });

                if (!restitle.ok || !restitle.body) {
                    setBotResponse("ERROR FROM BOT WHEN CREATING AUTOMATED CONVERSATION TITLE");
                    return;
                }

                const conversation_title_bot = await restitle.json();
                currentConversation.conversation_name = conversation_title_bot.content;
                console.log("rename Conversation 1", currentConversation, user.username, currentConversation.conversation_id, conversation_title_bot.content)
                await renameConversation(user.username, currentConversation.conversation_id, conversation_title_bot.content)
            }

            let conversation_id = currentConversation.conversation_id;
            let type = currentConversation.conversation_type;

            const form = new FormData();
            form.append('message', userMessage);
            form.append("conversation_type", type);
            form.append("web_search_tool", String(isOnline));  // must be string
            form.append("conversation_history", JSON.stringify(userMessages?.slice(-10)));
            form.append('conversation_id', conversation_id ?? "")
            if (uploadedFiles) {
                for (const f of uploadedFiles) {
                    form.append('files', f);
                }
            }

            const res = await fetch(`${api.defaults.baseURL}/request`, {
                method: "POST",
                signal: controller.signal,
                credentials: "include",
                body: form, // no JSON.stringify, no Content-Type header
            });

            if (!res.ok || !res.body) {
                setBotResponse("Error from bot");
                return;
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let fullBotResponse = '';

            while (true && user) {
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
                    if (!conversation_id) {
                        console.error("No conversation_id — cannot persist messages.");
                        return; // or throw new Error("Missing conversation_id")
                    }
                    await createMessage(user.username, conversation_id, newMessages[0].message, 'user', newMessages[0].feedback);
                    await createMessage(user.username, conversation_id, fullBotResponse, 'assistant', newMessages[1].feedback);
                    await fetchUserMessages(user.username, conversation_id);
                    break;
                }
            }
        } catch (err) {
            console.error("Streaming failed:", err);
            setBotResponse(`${err}`);
        } finally {
            setStreaming(false);
            controllerRef.current = null;
        }
    }

    const handleTextareaKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userQuery.trim()) {
                handleSubmit(e);
            }
        }
    };

    function onSelect(e: React.ChangeEvent<HTMLInputElement>) {
        const selected = Array.from(e.target.files ?? []);
        if (selected.length > 0) {
            setUploadedFiles((prev) => [...prev, ...selected]);
        }
        e.target.value = "";
    }

    const handleUserFeedback = async (message_id: string, conversation_id: string, feedback: boolean, e?: React.MouseEvent | React.FormEvent) => {
        e?.preventDefault();
        let message = undefined;
        if (!userMessages || !user) { return; }
        for (let i = 0; i < userMessages.length; i++) {
            if ('id' in userMessages[i] && userMessages[i].id === message_id) {
                message = userMessages[i];
                break;
            }
        }
        if (!message) { return; }
        try {
            await userFeedback(message_id, user?.username, conversation_id, message?.message, message?.role, feedback);
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === message_id ? { ...m, feedback } : m
                )
            );
        } catch (err) {
            console.log("Something went wrong with the feedback");
        }
    }

    const handleFeedback = async () => {
        const document_name = messageFeedbackDetails.fileDoc ? messageFeedbackDetails.fileDoc.name : '';
        const query_id = messageFeedbackDetails.query_id;
        const botAnswer_id = messageFeedbackDetails.generated_answer_id;
        var document_text;
        if (!messageFeedbackDetails.fileDoc) { document_text = '' }
        else if (document_name?.includes('.pdf')) { document_text = await handlePdfFile(messageFeedbackDetails.fileDoc) }
        else if (document_name?.includes('.docx')) { document_text = await handleDocxFile(messageFeedbackDetails.fileDoc) }
        else { document_text = await messageFeedbackDetails.fileDoc?.text() }
        return {
            g_feedback: messageFeedbackDetails.generalFeedback,
            document_text: document_text,
            query_id: query_id,
            negative_answer_id: botAnswer_id,
            doc_name: document_name,
            context: messageFeedbackDetails.context,
            theme: messageFeedbackDetails.theme
        }
    }

    const handleFeedbackSubmit = async (e: React.FormEvent) => {
        if (!user) { return; }
        e.preventDefault();
        const feedback = await handleFeedback();
        await createDocumentFeedback(user.username, feedback.query_id, feedback.negative_answer_id, feedback.doc_name, feedback.document_text, feedback.context, feedback.theme)
        setFeedbackFormOpen(false);
    }

    return {
        createNewConversation,
        handleRename,
        logoutButton,
        handleSubmit,
        handleTextareaKeyDown,
        onSelect,
        handleUserFeedback,
        handleFeedbackSubmit,
        userQuery, setUserQuery,
        isStreaming, setStreaming,
        isOnline, setOnlineMode,
        botResponse,
        sidebarOpen, setSidebarOpen,
        getMessagesFromConversations,
    }
}

export default UseChatLogic;