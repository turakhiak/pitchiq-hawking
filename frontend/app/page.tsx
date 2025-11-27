'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API call
    try {
      const response = await fetch('http://localhost:8002/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        toast.success('Welcome to PitchIQ!');
        router.push('/dashboard');
      } else {
        toast.error('Invalid credentials');
      }
    } catch (error) {
      toast.error('Connection error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[var(--bg-primary)] via-[var(--bg-secondary)] to-[var(--bg-primary)]" suppressHydrationWarning>
        {/* Floating Particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-[var(--accent-primary)] rounded-full opacity-20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-3/5 items-center justify-center relative z-10 p-12">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="text-left max-w-2xl"
        >
          <div className="flex items-center gap-3 mb-6">
            <Sparkles className="w-12 h-12 text-[var(--accent-primary)]" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] bg-clip-text text-transparent">
              PitchIQ
            </h1>
          </div>
          <h2 className="text-4xl font-bold mb-6 text-[var(--text-primary)]">
            Your AI Investment Analyst
          </h2>
          <p className="text-xl text-[var(--text-secondary)] mb-8">
            Analyze pitchbooks with AI-powered intelligence. Extract insights, validate financials, and generate investment papers in seconds.
          </p>
          <div className="flex flex-col gap-4 text-[var(--text-secondary)]">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full" />
              <span>Multimodal document analysis with Gemini 1.5 Pro</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-[var(--accent-secondary)] rounded-full" />
              <span>Automated financial verification \u0026 risk assessment</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-[var(--accent-primary)] rounded-full" />
              <span>Export to editable presentations \u0026 investment papers</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-2/5 flex items-center justify-center p-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div className="glass-card rounded-2xl p-8 shadow-2xl">
            {/* Mobile Logo */}
            <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
              <Sparkles className="w-10 h-10 text-[var(--accent-primary)]" />
              <h1 className="text-4xl font-bold bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] bg-clip-text text-transparent">
                PitchIQ
              </h1>
            </div>

            <h3 className="text-2xl font-bold mb-2">Welcome back</h3>
            <p className="text-[var(--text-secondary)] mb-8">
              Sign in to your account
            </p>

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Username</label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field w-full"
                  placeholder="analyst"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field w-full"
                  placeholder="••••••••"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-gradient w-full py-3 rounded-lg flex items-center justify-center gap-2"
              >
                {loading ? 'Signing in...' : 'Sign In'}
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>

            <p className="text-center text-sm text-[var(--text-secondary)] mt-6">
              Demo credentials: analyst / password
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
