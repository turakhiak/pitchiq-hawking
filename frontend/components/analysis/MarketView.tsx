
import { motion } from 'framer-motion';
import { TrendingUp, Users, Quote } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface MarketData {
    tam: string;
    sam: string;
    som: string;
    cagr: string;
    competitors: Array<{ name: string; description: string; strength: string; weakness: string }>;
    market_drivers: string[];
    citations: Array<{ text: string; explanation: string }>;
}

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B'];

export default function MarketView({ data }: { data: MarketData }) {
    if (!data) return <div>No data available</div>;

    // Parse values for chart (remove $ and B/M suffixes roughly)
    const parseValue = (val: string) => {
        if (!val) return 10; // Default if null/undefined
        const num = parseFloat(val.replace(/[^0-9.]/g, ''));
        return isNaN(num) ? 10 : num; // Default to 10 if parsing fails
    };

    const chartData = [
        { name: 'TAM', value: parseValue(data.tam) },
        { name: 'SAM', value: parseValue(data.sam) },
        { name: 'SOM', value: parseValue(data.som) },
    ];

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Market Size Chart */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="glass-card rounded-xl p-6"
                >
                    <div className="flex items-center gap-3 mb-6">
                        <TrendingUp className="w-6 h-6 text-[var(--accent-primary)]" />
                        <h2 className="text-2xl font-bold">Market Size</h2>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
                            <PieChart>
                                <Pie
                                    data={chartData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="grid grid-cols-3 gap-4 mt-6 text-center">
                        <div>
                            <p className="text-sm text-[var(--text-secondary)]">TAM</p>
                            <p className="font-bold text-lg">{data.tam}</p>
                        </div>
                        <div>
                            <p className="text-sm text-[var(--text-secondary)]">SAM</p>
                            <p className="font-bold text-lg">{data.sam}</p>
                        </div>
                        <div>
                            <p className="text-sm text-[var(--text-secondary)]">SOM</p>
                            <p className="font-bold text-lg">{data.som}</p>
                        </div>
                    </div>
                </motion.div>

                {/* Market Drivers */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="glass-card rounded-xl p-6"
                >
                    <h2 className="text-xl font-bold mb-4">Market Drivers</h2>
                    <div className="flex flex-wrap gap-2 mb-6">
                        {data.market_drivers?.map((driver, idx) => (
                            <span key={idx} className="px-3 py-1 bg-[var(--bg-tertiary)] rounded-full text-sm border border-[var(--border-color)]">
                                {driver}
                            </span>
                        ))}
                    </div>
                    <div className="mt-6">
                        <h3 className="font-semibold mb-2">CAGR</h3>
                        <div className="text-4xl font-bold text-green-400">{data.cagr}</div>
                    </div>
                </motion.div>
            </div>

            {/* Competitors */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-card rounded-xl p-6"
            >
                <div className="flex items-center gap-3 mb-4">
                    <Users className="w-6 h-6 text-[var(--accent-secondary)]" />
                    <h2 className="text-2xl font-bold">Competitive Landscape</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-[var(--border-color)]">
                                <th className="pb-3 font-semibold">Competitor</th>
                                <th className="pb-3 font-semibold">Description</th>
                                <th className="pb-3 font-semibold text-green-400">Strength</th>
                                <th className="pb-3 font-semibold text-red-400">Weakness</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-color)]">
                            {data.competitors?.map((comp, idx) => (
                                <tr key={idx} className="group hover:bg-[var(--bg-tertiary)] transition-colors">
                                    <td className="py-4 font-medium">{comp.name}</td>
                                    <td className="py-4 text-sm text-[var(--text-secondary)]">{comp.description}</td>
                                    <td className="py-4 text-sm">{comp.strength}</td>
                                    <td className="py-4 text-sm">{comp.weakness}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
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
