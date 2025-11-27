
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, AlertCircle, Quote } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface FinancialData {
    revenue_data: Array<{ year: string; value: number; is_projected: boolean }>;
    ebitda_margins?: string;
    valuation: string;
    monthly_burn_rate?: string;
    runway_months?: string;
    unit_economics?: Array<{ metric: string; value: string }>;
    key_metrics: Array<{ metric: string; value: string }>;
    verification_notes: string;
    citations: Array<{ text: string; explanation: string }>;
}

export default function FinancialView({ data }: { data: FinancialData }) {
    if (!data) return <div>No data available</div>;

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Key Metrics Cards */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card rounded-xl p-6 lg:col-span-1"
                >
                    <h2 className="text-xl font-bold mb-4">Key Metrics</h2>
                    <div className="space-y-4">
                        <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
                            <p className="text-sm text-[var(--text-secondary)]">Valuation</p>
                            <p className="text-2xl font-bold text-green-400">{data.valuation}</p>
                        </div>
                        {data.ebitda_margins && (
                            <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
                                <p className="text-sm text-[var(--text-secondary)]">EBITDA Margins</p>
                                <p className="text-2xl font-bold text-blue-400">{data.ebitda_margins}</p>
                            </div>
                        )}
                        {/* VC Specific Metrics */}
                        {data.monthly_burn_rate && (
                            <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg border border-red-500/20">
                                <p className="text-sm text-[var(--text-secondary)]">Monthly Burn</p>
                                <p className="text-2xl font-bold text-red-400">{data.monthly_burn_rate}</p>
                            </div>
                        )}
                        {data.runway_months && (
                            <div className="p-4 bg-[var(--bg-tertiary)] rounded-lg border border-yellow-500/20">
                                <p className="text-sm text-[var(--text-secondary)]">Runway</p>
                                <p className="text-2xl font-bold text-yellow-400">{data.runway_months}</p>
                            </div>
                        )}

                        {data.key_metrics?.map((metric, idx) => (
                            <div key={idx} className="flex justify-between items-center border-b border-[var(--border-color)] pb-2">
                                <span className="text-sm text-[var(--text-secondary)]">{metric.metric}</span>
                                <span className="font-semibold">{metric.value}</span>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Revenue Chart */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card rounded-xl p-6 lg:col-span-2"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <TrendingUp className="w-6 h-6 text-[var(--accent-primary)]" />
                        <h2 className="text-2xl font-bold">Revenue Growth</h2>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.revenue_data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="year" stroke="var(--text-secondary)" />
                                <YAxis stroke="var(--text-secondary)" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                />
                                <Bar dataKey="value" fill="var(--accent-primary)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </div>

            {/* Unit Economics (VC Only) */}
            {data.unit_economics && data.unit_economics.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="glass-card rounded-xl p-6"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <DollarSign className="w-6 h-6 text-purple-400" />
                        <h2 className="text-xl font-bold">Unit Economics</h2>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {data.unit_economics.map((item, idx) => (
                            <div key={idx} className="p-4 bg-[var(--bg-tertiary)] rounded-lg text-center">
                                <p className="text-sm text-[var(--text-secondary)] mb-1">{item.metric}</p>
                                <p className="text-xl font-bold text-white">{item.value}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Verification Notes */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-card rounded-xl p-6 border border-yellow-500/30 bg-yellow-500/5"
            >
                <div className="flex items-center gap-3 mb-2">
                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                    <h3 className="font-bold text-yellow-500">AI Verification Notes</h3>
                </div>
                <p className="text-sm text-[var(--text-secondary)]">{data.verification_notes}</p>
            </motion.div>

            {/* Citations */}
            {data.citations?.length > 0 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card rounded-xl p-6 border-l-4 border-[var(--accent-primary)]"
                >
                    <div className="flex items-center gap-2 mb-3">
                        <Quote className="w-5 h-5 text-[var(--text-tertiary)]" />
                        <h3 className="font-semibold text-[var(--text-secondary)]">Source Citations</h3>
                    </div>
                    <div className="space-y-3">
                        {data.citations.map((cite, idx) => (
                            <div key={idx} className="text-sm">
                                <p className="italic text-[var(--text-secondary)]">"{cite.text}"</p>
                                <p className="text-xs text-[var(--text-tertiary)] mt-1">— {cite.explanation}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}
        </div>
    );
}
