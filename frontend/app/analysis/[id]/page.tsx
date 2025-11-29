'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import ChatWidget from '@/components/ChatWidget';
import { motion } from 'framer-motion';
import { Building2, TrendingUp, DollarSign, AlertTriangle, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import clsx from 'clsx';
import { API_BASE_URL } from '@/lib/api';

// Import new structured view components
import CompanyView from '@/components/analysis/CompanyView';
import MarketView from '@/components/analysis/MarketView';
import FinancialView from '@/components/analysis/FinancialView';
import RiskView from '@/components/analysis/RiskView';

const tabs = [
    { id: 'company', name: 'Company', icon: Building2 },
    { id: 'market', name: 'Market', icon: TrendingUp },
    { id: 'financial', name: 'Financial', icon: DollarSign },
    { id: 'risk', name: 'Risks', icon: AlertTriangle },
];

export default function AnalysisPage() {
    const params = useParams();
    const [activeTab, setActiveTab] = useState('company');
    const [analysis, setAnalysis] = useState<any>({});
    const [loading, setLoading] = useState(false);

    const loadAnalysis = async (type: string) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_id: params.id,
                    analysis_type: type,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                // Data is now structured JSON, not a string
                setAnalysis((prev: any) => ({ ...prev, [type]: data.analysis }));
            } else {
                toast.error('Failed to fetch analysis');
            }
        } catch (error) {
            console.error(error);
            toast.error('Failed to load analysis');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab && !analysis[activeTab]) {
            loadAnalysis(activeTab);
        }
    }, [activeTab]);

    const renderContent = () => {
        if (loading) {
            return (
                <div className="glass-card rounded-xl p-8 flex flex-col items-center justify-center min-h-[400px]">
                    <div className="w-12 h-12 border-4 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin mb-4"></div>
                    <p className="text-[var(--text-secondary)] animate-pulse">Analyzing document with AI...</p>
                </div>
            );
        }

        const data = analysis[activeTab];

        if (!data) return null;

        switch (activeTab) {
            case 'company':
                return <CompanyView data={data} />;
            case 'market':
                return <MarketView data={data} />;
            case 'financial':
                return <FinancialView data={data} />;
            case 'risk':
                return <RiskView data={data} />;
            default:
                return <div>Select a tab</div>;
        }
    };

    return (
        <div className="flex min-h-screen">
            <Sidebar />

            <main className="flex-1 ml-64 p-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-4xl font-bold mb-2">Analysis: {params.id}</h1>
                        <p className="text-[var(--text-secondary)]">
                            AI-powered insights from your pitchbook
                        </p>
                    </div>
                    <button className="btn-gradient px-6 py-3 rounded-lg flex items-center gap-2">
                        <Download className="w-5 h-5" />
                        Export Report
                    </button>
                </div>

                <div className="flex gap-2 mb-8 glass-card p-2 rounded-xl">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={clsx(
                                    'flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-all',
                                    activeTab === tab.id
                                        ? 'bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] text-white'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                                )}
                            >
                                <Icon className="w-5 h-5" />
                                {tab.name}
                            </button>
                        );
                    })}
                </div>

                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    {renderContent()}
                </motion.div>
            </main>

            <ChatWidget documentId={params.id as string} />
        </div>
    );
}
