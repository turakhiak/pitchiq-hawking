'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Sparkles } from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '@/lib/api';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function ChatWidget({ documentId }: { documentId?: string }) {
    const [isOpen, setIsOpen] = useState(false);
    const [documentName, setDocumentName] = useState<string>('');

    // Set initial message based on document context
    const getInitialMessage = () => {
        if (documentId && documentId !== 'demo') {
            return `Hi! I'm your PitchIQ AI assistant. Ask me anything about ${documentName || documentId}.`;
        }
        return 'Hi! I\'m your PitchIQ AI assistant. Upload and analyze a pitch deck to chat about it.';
    };

    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: getInitialMessage() }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    // Update document name when documentId changes
    useEffect(() => {
        if (documentId && documentId !== 'demo') {
            setDocumentName(documentId.replace(/_/g, ' '));
        }
    }, [documentId]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_id: documentId || 'demo',
                    messages: [...messages, userMessage],
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
            } else {
                setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, the backend is having trouble. Please try again.' }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* Floating Button */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.button
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        onClick={() => setIsOpen(true)}
                        className="fixed bottom-8 right-8 w-16 h-16 bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform z-50"
                    >
                        <MessageSquare className="w-7 h-7 text-white" />
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--success)] rounded-full animate-pulse" />
                    </motion.button>
                )}
            </AnimatePresence>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, x: 400 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 400 }}
                        transition={{ type: 'spring', damping: 25 }}
                        className="fixed bottom-8 right-8 w-96 h-[600px] glass-card rounded-2xl shadow-2xl flex flex-col z-50"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-white/10">
                            <div className="flex flex-col gap-1">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-[var(--accent-primary)]" />
                                    <h3 className="font-semibold">PitchIQ Assistant</h3>
                                </div>
                                {documentId && documentId !== 'demo' && documentName && (
                                    <span className="text-xs text-[var(--text-secondary)] ml-7">
                                        📄 {documentName}
                                    </span>
                                )}
                            </div>
                            <button onClick={() => setIsOpen(false)} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
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
                                            'max-w-[80%] rounded-2xl px-4 py-3',
                                            message.role === 'user'
                                                ? 'bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] text-white'
                                                : 'glass-card text-[var(--text-primary)]'
                                        )}
                                    >
                                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                    </div>
                                </motion.div>
                            ))}

                            {loading && (
                                <div className="flex justify-start">
                                    <div className="glass-card rounded-2xl px-4 py-3">
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
                        <div className="p-4 border-t border-white/10">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                    placeholder="Ask about the pitchbook..."
                                    className="flex-1 input-field"
                                    disabled={loading}
                                />
                                <button
                                    onClick={sendMessage}
                                    disabled={loading || !input.trim()}
                                    className="btn-gradient px-4 rounded-lg disabled:opacity-50"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
