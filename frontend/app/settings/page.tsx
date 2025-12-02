'use client';

import Sidebar from '@/components/Sidebar';
import { motion } from 'framer-motion';
import { Settings, Construction } from 'lucide-react';
import ChatWidget from '@/components/ChatWidget';

export default function SettingsPage() {
    return (
        <div className="flex min-h-screen">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="flex items-center gap-3 mb-8">
                        <Settings className="w-8 h-8 text-[var(--accent-primary)]" />
                        <h1 className="text-3xl font-bold">Settings</h1>
                    </div>

                    <div className="glass-card rounded-xl p-12 text-center">
                        <div className="w-20 h-20 bg-[var(--bg-tertiary)] rounded-full flex items-center justify-center mx-auto mb-6">
                            <Construction className="w-10 h-10 text-[var(--accent-secondary)]" />
                        </div>
                        <h2 className="text-2xl font-bold mb-2">Under Construction</h2>
                        <p className="text-[var(--text-secondary)] max-w-md mx-auto">
                            We're working on advanced configuration options for PitchIQ.
                            Check back soon for profile management, API keys, and notification settings.
                        </p>
                    </div>
                </motion.div>
            </main>

            <ChatWidget />
        </div>
    );
}
