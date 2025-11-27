
import { motion } from 'framer-motion';
import { Building2, Users, Package, Target, Quote } from 'lucide-react';

interface CompanyData {
    overview: string;
    founding_year: string;
    headquarters: string;
    key_management: Array<{ name: string; role: string; bio: string }>;
    founders_background?: Array<{ name: string; role: string; bio: string }>;
    products: Array<{ name: string; description: string }>;
    business_model: string;
    citations: Array<{ text: string; explanation: string }>;
}

export default function CompanyView({ data }: { data: CompanyData }) {
    if (!data) return <div>No data available</div>;

    return (
        <div className="space-y-6">
            {/* Overview Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-xl p-6"
            >
                <div className="flex items-center gap-3 mb-4">
                    <Building2 className="w-6 h-6 text-[var(--accent-primary)]" />
                    <h2 className="text-2xl font-bold">Company Overview</h2>
                </div>
                <p className="text-[var(--text-secondary)] mb-4">{data.overview}</p>
                <div className="flex gap-6 text-sm">
                    <div className="flex flex-col">
                        <span className="text-[var(--text-tertiary)]">Founded</span>
                        <span className="font-semibold">{data.founding_year || 'N/A'}</span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-[var(--text-tertiary)]">Headquarters</span>
                        <span className="font-semibold">{data.headquarters || 'N/A'}</span>
                    </div>
                </div>
            </motion.div>

            {/* Management Team */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass-card rounded-xl p-6"
            >
                <div className="flex items-center gap-3 mb-4">
                    <Users className="w-6 h-6 text-[var(--accent-secondary)]" />
                    <h2 className="text-2xl font-bold">Key Management</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {data.key_management?.map((person, idx) => (
                        <div key={idx} className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
                            <h3 className="font-bold text-lg">{person.name}</h3>
                            <p className="text-[var(--accent-primary)] text-sm mb-2">{person.role}</p>
                            <p className="text-sm text-[var(--text-secondary)]">{person.bio}</p>
                        </div>
                    ))}
                </div>
            </motion.div>

            {/* Founders Deep Dive (VC Only) */}
            {data.founders_background && data.founders_background.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="glass-card rounded-xl p-6 border border-purple-500/20"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Target className="w-6 h-6 text-purple-400" />
                        <h2 className="text-2xl font-bold">Founders Deep Dive</h2>
                    </div>
                    <div className="space-y-4">
                        {data.founders_background.map((founder, idx) => (
                            <div key={idx} className="p-4 bg-[var(--bg-tertiary)] rounded-lg">
                                <h3 className="font-bold text-lg text-purple-300">{founder.name}</h3>
                                <p className="text-sm text-[var(--text-secondary)] mt-1">{founder.bio}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Products & Business Model */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card rounded-xl p-6"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Package className="w-6 h-6 text-blue-400" />
                        <h2 className="text-xl font-bold">Products</h2>
                    </div>
                    <ul className="space-y-3">
                        {data.products?.map((prod, idx) => (
                            <li key={idx} className="border-b border-[var(--border-color)] pb-2 last:border-0">
                                <span className="font-semibold block">{prod.name}</span>
                                <span className="text-sm text-[var(--text-secondary)]">{prod.description}</span>
                            </li>
                        ))}
                    </ul>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card rounded-xl p-6"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Target className="w-6 h-6 text-green-400" />
                        <h2 className="text-xl font-bold">Business Model</h2>
                    </div>
                    <p className="text-[var(--text-secondary)]">{data.business_model}</p>
                </motion.div>
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
