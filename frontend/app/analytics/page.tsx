'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import ChatWidget from '@/components/ChatWidget';
import { motion } from 'framer-motion';
import { FileText, TrendingUp, DollarSign, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '@/lib/api';

interface Document {
    id: string;
    name: string;
    date: string;
    industry: string;
    geography: string;
}

export default function AnalyticsPage() {
    const router = useRouter();
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);

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
            } finally {
                setLoading(false);
            }
        };

        fetchDocuments();
    }, []);

    return (
        <div className="flex min-h-screen">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold mb-2">Analytics</h1>
                    <p className="text-[var(--text-secondary)]">
                        View and manage all your pitchbook analyses
                    </p>
                </motion.div>

                {/* Recent Analyses */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-2xl font-bold mb-6">Recent Analyses</h2>

                    {loading ? (
                        <div className="text-center py-12 text-[var(--text-secondary)]">Loading...</div>
                    ) : documents.length > 0 ? (
                        <div className="space-y-4">
                            {documents.map((doc, index) => (
                                <motion.div
                                    key={doc.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    onClick={() => router.push(`/analysis/${doc.id}`)}
                                    className="flex items-center justify-between p-4 bg-[var(--bg-tertiary)] rounded-lg hover:bg-[var(--bg-secondary)] transition-colors cursor-pointer"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-12 h-12 bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] rounded-lg flex items-center justify-center">
                                            <FileText className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold">{doc.name}</h3>
                                            <p className="text-sm text-[var(--text-secondary)]">{doc.industry}</p>
                                        </div>
                                    </div>
                                    <span className="text-sm text-[var(--text-secondary)]">{doc.date}</span>
                                </motion.div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-12 text-[var(--text-secondary)]">
                            <p>No analyses yet. Upload a pitchbook to get started.</p>
                        </div>
                    )}
                </motion.div>

                {/* Quick Stats - Placeholder for now until we have real aggregated stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
                    {[
                        { label: 'Total Analyses', value: documents.length.toString(), icon: FileText },
                        { label: 'Industries Covered', value: new Set(documents.map(d => d.industry)).size.toString(), icon: TrendingUp },
                        { label: 'Avg Deal Size', value: '$--M', icon: DollarSign },
                        { label: 'Risk Flags', value: '0', icon: AlertTriangle },
                    ].map((stat, index) => {
                        const Icon = stat.icon;
                        return (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 + index * 0.1 }}
                                className="glass-card rounded-xl p-6"
                            >
                                <Icon className="w-8 h-8 text-[var(--accent-primary)] mb-3" />
                                <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
                                <p className="text-sm text-[var(--text-secondary)]">{stat.label}</p>
                            </motion.div>
                        );
                    })}
                </div>
            </main>

            <ChatWidget />
        </div>
    );
}
