import { useState } from 'react';
import UseChatLogic from './funcs';
import { useChat } from '../../context/ChatPageContext';

const FeedbackDoc = () => {

    const {
        handleFeedbackSubmit,
    } = UseChatLogic();

    const {
        setmessageFeedbackDetails,
        openFeedback, setFeedbackFormOpen
    } = useChat();

    const [otherRadio, setOtherRadio] = useState(false);


    return (

        (openFeedback && (
            <form
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm overflow-y-auto p-3 sm:p-4"
                onSubmit={handleFeedbackSubmit}
            >
                <div className="bg-white p-4 sm:p-6 rounded-lg shadow-lg w-full max-w-lg sm:max-w-xl md:max-w-2xl space-y-4 sm:space-y-6 max-h-[90vh] overflow-y-auto">
                    <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Feedback Instructions</h2>

                    <div className="bg-gray-100 p-3 sm:p-4 rounded-lg text-xs sm:text-sm text-gray-700 space-y-2">
                        <p>
                            In this section, you can provide feedback on the chatbot’s responses.
                            If you believe a response was <strong>inaccurate, incomplete, or unreliable</strong>,
                            you may suggest what the correct answer should have been.
                        </p>
                        <p>When submitting your feedback, please include the following:</p>
                        <ul className="list-disc list-inside space-y-1">
                            <li>
                                <strong>Correct Answer Document:</strong> Upload or provide a document that contains the appropriate answer.
                            </li>
                            <li>
                                <strong>Relevant Context:</strong> Specify the part of the document (section, paragraph, or article) that supports your correction.
                            </li>
                            <li>
                                <strong>Theme:</strong> Select the theme of your feedback or propose your own:
                                <ul className="list-disc list-inside ml-4">
                                    <li><strong>cases</strong>: Law Cases</li>
                                    <li><strong>phishing</strong>: Phishing & General Info</li>
                                    <li><strong>cybercrime</strong>: Greek Penal Code & Legislation</li>
                                    <li><strong>gdpr</strong>: GDPR</li>
                                </ul>
                            </li>
                        </ul>
                    </div>

                    {/* Theme Selection */}
                    <div>
                        <label className="block font-medium mb-2">Theme</label>
                        <div className="space-y-2 text-sm">
                            <div>
                                <input
                                    type="radio"
                                    id="cases"
                                    name="theme"
                                    value="cases"
                                    onClick={() => { setmessageFeedbackDetails(prev => ({ ...prev, theme: 'Law Cases' })); setOtherRadio(false); }}
                                />
                                <label htmlFor="cases" className="ml-2">Cases (Law Cases)</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    id="phishing"
                                    name="theme"
                                    value="phishing"
                                    onClick={() => { setmessageFeedbackDetails(prev => ({ ...prev, theme: 'Phishing Scenarios' })); setOtherRadio(false); }}
                                />
                                <label htmlFor="phishing" className="ml-2">Phishing (Scenarios & General Info)</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    id="cybercrime"
                                    name="theme"
                                    value="cybercrime"
                                    onClick={() => { setmessageFeedbackDetails(prev => ({ ...prev, theme: 'Greek Cybercrime Legislation' })); setOtherRadio(false); }}
                                />
                                <label htmlFor="cybercrime" className="ml-2">Cybercrime (Greek Penal Code & Legislation)</label>
                            </div>
                            <div>
                                <input
                                    type="radio"
                                    id="gdpr"
                                    name="theme"
                                    value="gdpr"
                                    onClick={() => { setmessageFeedbackDetails(prev => ({ ...prev, theme: 'General Data Protection Regulation' })); setOtherRadio(false); }}
                                />
                                <label htmlFor="gdpr" className="ml-2">GDPR (Data Protection Regulation)</label>
                            </div>
                            <div className="flex items-center gap-2">
                                <input
                                    type="radio"
                                    id="custom"
                                    name="theme"
                                    value="custom"
                                    onChange={() => setOtherRadio(true)}
                                />
                                <label htmlFor="custom" className="ml-2">Other:</label>
                                <input
                                    type="text"
                                    placeholder="Enter your own theme"
                                    className="flex-1 px-2 py-1 border rounded text-sm"
                                    disabled={otherRadio === false}
                                    onChange={(e) => setmessageFeedbackDetails(prev => ({ ...prev, theme: e.target.value }))}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Document Upload */}
                    <div>
                        <label htmlFor="file_document" className="block font-medium mb-2">
                            Upload Correct Answer Document
                        </label>
                        <input
                            type="file"
                            id="file_document"
                            required
                            name="file_document"
                            accept=".pdf,.doc,.docx,.txt"
                            onChange={(e) => setmessageFeedbackDetails(prev => ({ ...prev, fileDoc: e.target.files?.[0] ?? null }))}
                            className="block w-full text-sm text-gray-600"
                        />
                    </div>

                    <div>
                        <label htmlFor="general_feedback" className="block font-medium mb-2">
                            General Feedback
                        </label>
                        <textarea
                            name="general_feedback"
                            id="general_feedback"
                            autoComplete="off"
                            required
                            onChange={(e) => setmessageFeedbackDetails(prev => ({ ...prev, generalFeedback: e.target.value }))}
                            placeholder="Specify section, paragraph, or article..."
                            className="w-full px-3 py-2 border rounded-lg text-sm h-28 sm:h-32 resize-y"
                        />
                    </div>

                    <div>
                        <label htmlFor="context" className="block font-medium mb-2">
                            Relevant Context
                        </label>
                        <textarea
                            name="context"
                            id="context"
                            autoComplete="off"
                            required
                            onChange={(e) => setmessageFeedbackDetails(prev => ({ ...prev, context: e.target.value }))}
                            placeholder="Specify section, paragraph, or article..."
                            className="w-full px-3 py-2 border rounded-lg text-sm h-28 sm:h-32 resize-y"
                        />
                    </div>

                    {/* Buttons */}
                    <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 sm:gap-3">
                        <button
                            type="button"
                            onClick={() => setFeedbackFormOpen(false)}
                            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        >
                            Close
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Submit Feedback
                        </button>
                    </div>
                </div>
            </form >
        ))
    )
}


export default FeedbackDoc;