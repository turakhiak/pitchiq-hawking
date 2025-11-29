'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, FileText, Sparkles, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import clsx from 'clsx';

export default function UploadPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [industry, setIndustry] = useState('');
    const [geography, setGeography] = useState('');
    const [dealType, setDealType] = useState('');
    const [uploading, setUploading] = useState(false);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
            toast.success(`File selected: ${acceptedFiles[0].name}`);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
    });

    const handleUpload = async () => {
        if (!file || !industry || !geography) {
            toast.error('Please fill all required fields');
            return;
            toast.success('Document uploaded successfully!');
            router.push(`/analysis/${data.filename}`);
        } else {
            toast.error('Upload failed');
        }
    } catch (error) {
        toast.error('Connection error');
    } finally {
        setUploading(false);
    }
};

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
                <h1 className="text-4xl font-bold mb-2">Upload Pitchbook</h1>
                <p className="text-[var(--text-secondary)]">
                    Upload a pitchbook PDF for AI-powered analysis
                </p>
            </motion.div>

            {/* Drag and Drop Zone */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mb-8"
            >
                <div
                    {...getRootProps()}
                    className={clsx(
                        'glass-card rounded-xl p-12 border-2 border-dashed cursor-pointer transition-all duration-300',
                        isDragActive
                            ? 'border-[var(--accent-primary)] scale-102 glow'
                            : 'border-white/20 hover:border-[var(--accent-primary)]'
                    )}
                >
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center justify-center text-center">
                        {file ? (
                            <>
                                <FileText className="w-16 h-16 text-[var(--accent-primary)] mb-4" />
                                <h3 className="text-xl font-semibold mb-2">{file.name}</h3>
                                <p className="text-[var(--text-secondary)]">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </>
                        ) : (
                            <>
                                <UploadIcon className="w-16 h-16 text-[var(--accent-primary)] mb-4 animate-float" />
                                <h3 className="text-xl font-semibold mb-2">
                                    {isDragActive ? 'Drop your file here' : 'Drop PDF here or click to browse'}
                                </h3>
                                <p className="text-[var(--text-secondary)]">
                                    Supports: PDF files up to 50MB
                                </p>
                            </>
                        )}
                    </div>
                </div>
            </motion.div>

            {/* Metadata Form */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-card rounded-xl p-8 mb-8"
            >
                <h2 className="text-2xl font-bold mb-6">Deal Information</h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">Industry *</label>
                        <select
                            value={industry}
                            onChange={(e) => setIndustry(e.target.value)}
                            className="input-field w-full"
                            required
                        >
                            <option value="">Select industry</option>
                            <option value="Technology">Technology</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Financial Services">Financial Services</option>
                            <option value="Manufacturing">Manufacturing</option>
                            <option value="Retail">Retail</option>
                            <option value="Energy">Energy</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Geography *</label>
                        <select
                            value={geography}
                            onChange={(e) => setGeography(e.target.value)}
                            className="input-field w-full"
                            required
                        >
                            <option value="">Select geography</option>
                            <option value="North America">North America</option>
                            <option value="Europe">Europe</option>
                            <option value="Asia">Asia</option>
                            <option value="Latin America">Latin America</option>
                            <option value="Middle East">Middle East</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Deal Type</label>
                        <select
                            value={dealType}
                            onChange={(e) => setDealType(e.target.value)}
                            className="input-field w-full"
                        >
                            <option value="">Select deal type (optional)</option>
                            <option value="M&A">M&A</option>
                            <option value="Growth Equity">Growth Equity</option>
                            <option value="Buyout">Buyout</option>
                            <option value="Venture Capital">Venture Capital</option>
                            <option value="Angel Investing">Angel Investing</option>
                            <option value="IPO">IPO</option>
                        </select>
                    </div>
                </div>
            </motion.div>

            {/* Analyze Button */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
            >
                <button
                    onClick={handleUpload}
                    disabled={!file || !industry || !geography || uploading}
                    className="btn-gradient w-full py-4 rounded-xl flex items-center justify-center gap-3 text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Sparkles className="w-6 h-6" />
                    {uploading ? 'Analyzing...' : 'Analyze Document'}
                    <ArrowRight className="w-6 h-6" />
                </button>
            </motion.div>
        </main>
    </div>
);
}
