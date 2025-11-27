'use client';

import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatWidget from '@/components/ChatWidget';
import { motion } from 'framer-motion';
import { FileText, TrendingUp, Shield, Clock } from 'lucide-react';
import Link from 'next/link';

interface Document {
    id: string;
    name: string;
    date: string;
    industry: string;
    geography: string;
}

interface Stats {
    total_documents: number;
    industries_covered: number;
    avg_deal_size: string;
    risk_flags: number;
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats>({
        total_documents: 0,
        industries_covered: 0,
        avg_deal_size: '-',
        risk_flags: 0
    });
    const [recentDocs, setRecentDocs] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, docsRes] = await Promise.all([
                    fetch('http://localhost:8002/api/documents/stats'),
                    fetch('http://localhost:8002/api/documents')
                ]);

                if (statsRes.ok) {
                    const statsData = await statsRes.json();
                    setStats(statsData);
                }

                if (docsRes.ok) {
                    const docsData = await docsRes.json();
                    setRecentDocs(docsData);
                }
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const statCards = [
        { name: 'Documents Analyzed', value: stats.total_documents.toString(), icon: FileText, color: 'from-blue-500 to-cyan-500' },
        { name: 'Industries Covered', value: stats.industries_covered.toString(), icon: TrendingUp, color: 'from-purple-500 to-pink-500' },
        { name: 'Risk Alerts', value: stats.risk_flags.toString(), icon: Shield, color: 'from-orange-500 to-red-500' },
        { name: 'Avg Deal Size', value: stats.avg_deal_size, icon: Clock, color: 'from-green-500 to-teal-500' },
    ];

    return (
        <div className="flex min-h-screen">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
                    <p className="text-[var(--text-secondary)]">
                        Welcome back! Here's your investment analysis overview.
                    </p>
                </motion.div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {statCards.map((stat, index) => {
                        const Icon = stat.icon;
                        return (
                            <motion.div
                                key={stat.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="glass-card rounded-xl p-6 hover:scale-105 transition-transform cursor-pointer"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className={`p-3 rounded-lg bg-gradient-to-r ${stat.color}`}>
                                        <Icon className="w-6 h-6 text-white" />
                                    </div>
                                </div>
                                <h3 className="text-3xl font-bold mb-1">{stat.value}</h3>
                                <p className="text-sm text-[var(--text-secondary)]">{stat.name}</p>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Recent Documents */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-2xl font-bold mb-6">Recent Documents</h2>
                    <div className="space-y-4">
                        {loading ? (
                            <div className="text-center py-8 text-[var(--text-secondary)]">Loading...</div>
                        ) : recentDocs.length > 0 ? (
                            recentDocs.map((doc) => (
                                <Link href={`/analysis/${doc.id}`} key={doc.id}>
                                    <div className="flex items-center justify-between p-4 bg-[var(--bg-tertiary)] rounded-lg hover:bg-[var(--bg-secondary)] transition-colors cursor-pointer mb-3">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] rounded-lg flex items-center justify-center">
                                                <FileText className="w-6 h-6 text-white" />
                                            </div>
                                            <div>
                                                <h3 className="font-semibold">{doc.name}</h3>
                                                <p className="text-sm text-[var(--text-secondary)]">{doc.industry} • {doc.geography}</p>
                                            </div>
                                        </div>
                                        <span className="text-sm text-[var(--text-secondary)]">{doc.date}</span>
                                    </div>
                                </Link>
                            ))
                        ) : (
                            <div className="text-center py-8 text-[var(--text-secondary)]">
                                <p>No documents yet. Upload a pitchbook to get started.</p>
                            </div>
                        )}
                    </div>
                </motion.div>
            </main>

            <ChatWidget />
        </div>
    );
}
