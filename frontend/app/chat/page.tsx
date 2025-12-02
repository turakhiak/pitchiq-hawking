'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import { motion } from 'framer-motion';
import { MessageSquare, Send, Sparkles, FileText } from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '@/lib/api';
import toast from 'react-hot-toast';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

interface Document {
    id: string;
    name: string;
    date: string;
    industry: string;
}

export default function ChatPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [selectedDoc, setSelectedDoc] = useState<string>('');
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'Hi! Select a document from the dropdown above to start chatting about it.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    // Fetch available documents
    useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/documents`);
                if (response.ok) {
                    const data = await response.json();
                    setDocuments(data);
                }
            } catch (error) {
                console.error('Failed to fetch documents:', error);
                toast.error('Failed to load documents');
            }
        };
        fetchDocuments();
    }, []);

    // Update greeting when document changes
    useEffect(() => {
        if (selectedDoc) {
            const doc = documents.find(d => d.id === selectedDoc);
            setMessages([
                { role: 'assistant', content: `Great! I'm now ready to answer questions about "${doc?.name || selectedDoc}". What would you like to know?` }
            ]);
        }
    }, [selectedDoc, documents]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        if (!selectedDoc) {
            toast.error('Please select a document first');
            return;
        }

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_id: selectedDoc,
                    messages: [...messages, userMessage],
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
            } else {
                toast.error('Failed to get response');
                setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
            }
        } catch (error) {
            toast.error('Connection error');
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered a connection error. Please try again.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar />

            <main className="flex-1 ml-64 p-8 flex flex-col">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6"
                >
                    <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                        <MessageSquare className="w-10 h-10 text-[var(--accent-primary)]" />
                        Chat with Documents
                    </h1>
                    <p className="text-[var(--text-secondary)]">
                        Select a pitch deck and ask questions about it
                    </p>
                </motion.div>

                {/* Document Selector */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card rounded-xl p-4 mb-6"
                >
                    <label className="block text-sm font-medium mb-2">Select Document</label>
                    <select
                        value={selectedDoc}
                        onChange={(e) => setSelectedDoc(e.target.value)}
                        className="input-field w-full max-w-md"
                    >
                        <option value="">Choose a pitch deck...</option>
                        {documents.map((doc) => (
                            <option key={doc.id} value={doc.id}>
                                {doc.name} ({doc.industry})
                            </option>
                        ))}
                    </select>
                    {documents.length === 0 && (
                        <p className="text-sm text-[var(--text-secondary)] mt-2">
                            No documents found. Upload a pitch deck to get started.
                        </p>
                    )}
                </motion.div>

                {/* Chat Area */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="flex-1 glass-card rounded-xl flex flex-col overflow-hidden"
                >
                    {/* Selected Document Indicator */}
                    {selectedDoc && (
                        <div className="p-4 border-b border-white/10 bg-[var(--bg-tertiary)] flex items-center gap-2">
                            <FileText className="w-5 h-5 text-[var(--accent-primary)]" />
                            <span className="text-sm font-medium">
                                Chatting about: {documents.find(d => d.id === selectedDoc)?.name || selectedDoc}
                            </span>
                        </div>
                    )}

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                        {messages.map((message, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={clsx(
                                    'flex',
                                    message.role === 'user' ? 'justify-end' : 'justify-start'
                                )}
                            >
                                <div
                                    className={clsx(
                                        'max-w-[70%] rounded-2xl px-6 py-4',
                                        message.role === 'user'
                                            ? 'bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] text-white'
                                            : 'glass-card text-[var(--text-primary)]'
                                    )}
                                >
                                    {message.role === 'assistant' && (
                                        <div className="flex items-center gap-2 mb-2">
                                            <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                                            <span className="text-xs font-semibold text-[var(--accent-primary)]">PitchIQ AI</span>
                                        </div>
                                    )}
                                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                                </div>
                            </motion.div>
                        ))}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="glass-card rounded-2xl px-6 py-4">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                        <span className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                        <span className="w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="p-6 border-t border-white/10">
                        <div className="flex gap-3">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder={selectedDoc ? "Ask a question about this document..." : "Select a document first..."}
                                className="flex-1 input-field"
                                disabled={loading || !selectedDoc}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={loading || !input.trim() || !selectedDoc}
                                className="btn-gradient px-6 py-3 rounded-lg disabled:opacity-50 flex items-center gap-2"
                            >
                                <Send className="w-5 h-5" />
                                <span className="font-medium">Send</span>
                            </button>
                        </div>
                    </div>
                </motion.div>
            </main>
        </div>
    );
}
