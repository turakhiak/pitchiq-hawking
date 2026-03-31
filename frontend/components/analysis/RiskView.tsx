
import { motion } from 'framer-motion';
import { AlertTriangle, ShieldCheck, Quote, TrendingUp } from 'lucide-react';

interface RiskData {
    reasoning?: string;
    risks: Array<{ category: string; description: string; severity: string; mitigant: string }>;
    overall_risk_score: string;
    citations: Array<{ text: string; explanation: string }>;
}

export default function RiskView({ data }: { data: RiskData }) {
    if (!data) return <div>No data available</div>;

    const getSeverityColor = (severity: string) => {
        const s = severity.toLowerCase();
        if (s.includes('high')) return 'text-red-400 bg-red-400/10 border-red-400/20';
        if (s.includes('medium')) return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
        return 'text-green-400 bg-green-400/10 border-green-400/20';
    };

    return (
        <div className="space-y-6">
            {/* AI Insights Card */}
            {data.reasoning && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl flex items-start gap-3"
                >
                    <div className="mt-1 bg-orange-500 rounded-full p-1">
                        <TrendingUp className="w-3 h-3 text-white" />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-orange-400 uppercase tracking-wider mb-1">Risk Analyst Perspective</p>
                        <p className="text-sm text-[var(--text-secondary)] italic leading-relaxed">
                            "{data.reasoning}"
                        </p>
                    </div>
                </motion.div>
            )}
            
            {/* Overall Score */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-xl p-6 flex items-center justify-between"
            >
                <div>
                    <h2 className="text-2xl font-bold mb-1">Risk Assessment</h2>
                    <p className="text-[var(--text-secondary)]">AI-evaluated risk profile</p>
                </div>
                <div className={`px-6 py-3 rounded-lg border ${getSeverityColor(String(data.overall_risk_score))}`}>
                    <span className="font-bold text-xl">{String(data.overall_risk_score)} Risk</span>
                </div>
            </motion.div>

            {/* Risk Cards */}
            <div className="grid grid-cols-1 gap-4">
                {data.risks?.map((risk, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="glass-card rounded-xl p-6 border-l-4 border-[var(--border-color)] hover:border-[var(--accent-primary)] transition-colors"
                    >
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5 text-[var(--accent-secondary)]" />
                                <h3 className="font-bold text-lg">{risk.category}</h3>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getSeverityColor(risk.severity)}`}>
                                {risk.severity}
                            </span>
                        </div>
                        <p className="text-[var(--text-secondary)] mb-4">
                            {typeof risk.description === 'object' ? JSON.stringify(risk.description) : String(risk.description)}
                        </p>

                        <div className="flex items-start gap-2 p-3 bg-[var(--bg-tertiary)] rounded-lg">
                            <ShieldCheck className="w-5 h-5 text-green-400 mt-0.5" />
                            <div>
                                <span className="text-xs font-bold text-green-400 uppercase tracking-wider">Mitigant</span>
                                <p className="text-sm mt-1">
                                    {typeof risk.mitigant === 'object' ? JSON.stringify(risk.mitigant) : String(risk.mitigant)}
                                </p>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

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
