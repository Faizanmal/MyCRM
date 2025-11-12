import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, Loader2, Mail, Lock, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: 'beforeChildren',
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      stiffness: 100,
      damping: 15,
    },
  },
};

const errorVariants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      stiffness: 300,
      damping: 20,
    },
  },
  exit: { opacity: 0, x: 10 },
};

export default function EnhancedLoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData);
      router.push('/');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please check your credentials.';
      setError(errorMessage);
      // Shake animation on error
      const form = document.getElementById('login-form');
      form?.classList.add('animate-shake');
      setTimeout(() => form?.classList.remove('animate-shake'), 500);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gray-900">
      {/* Animated Gradient Background */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-40 animate-pulse-slow" />
      
      {/* Floating particles/shapes (optional) */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute top-20 left-20 w-72 h-72 bg-primary-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute top-40 right-20 w-72 h-72 bg-secondary-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute -bottom-20 left-1/2 w-72 h-72 bg-accent-500 rounded-full mix-blend-multiply filter blur-xl opacity-20"
          animate={{
            x: [0, 50, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      {/* Main Content */}
      <div className="relative min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          className="max-w-md w-full"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Logo and Title */}
          <motion.div variants={itemVariants} className="text-center mb-8">
            <motion.div
              className="mx-auto h-16 w-16 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-glow-lg mb-6"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: 'spring', stiffness: 400, damping: 10 }}
            >
              <span className="text-white font-bold text-2xl">CRM</span>
            </motion.div>
            
            <h2 className="text-4xl font-extrabold text-white mb-2">
              Welcome Back
            </h2>
            <p className="text-gray-300 text-sm">
              Sign in to access your CRM dashboard
            </p>
          </motion.div>

          {/* Login Card with Glassmorphism */}
          <motion.div
            variants={itemVariants}
            className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-glass-lg p-8"
          >
            <form id="login-form" onSubmit={handleSubmit} className="space-y-6">
              {/* Error Alert */}
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    variants={errorVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="bg-danger-500/20 border border-danger-500/50 rounded-lg p-4 flex items-start gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-danger-400 shrink-0 mt-0.5" />
                    <p className="text-sm text-danger-200">{error}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Username/Email Field */}
              <div className="space-y-2">
                <label
                  htmlFor="username"
                  className={`block text-sm font-medium transition-colors duration-200 ${
                    focusedField === 'username' ? 'text-primary-300' : 'text-gray-300'
                  }`}
                >
                  Username or Email
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                    <Mail
                      className={`w-5 h-5 transition-colors duration-200 ${
                        focusedField === 'username' ? 'text-primary-400' : 'text-gray-400'
                      }`}
                    />
                  </div>
                  <motion.input
                    id="username"
                    name="username"
                    type="text"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('username')}
                    onBlur={() => setFocusedField(null)}
                    whileFocus={{ scale: 1.02 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                    placeholder="Enter your username or email"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label
                  htmlFor="password"
                  className={`block text-sm font-medium transition-colors duration-200 ${
                    focusedField === 'password' ? 'text-primary-300' : 'text-gray-300'
                  }`}
                >
                  Password
                </label>
                <div className="relative">
                  <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                    <Lock
                      className={`w-5 h-5 transition-colors duration-200 ${
                        focusedField === 'password' ? 'text-primary-400' : 'text-gray-400'
                      }`}
                    />
                  </div>
                  <motion.input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.password}
                    onChange={handleChange}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    whileFocus={{ scale: 1.02 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    className="w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                    placeholder="Enter your password"
                  />
                  <motion.button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </motion.button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center cursor-pointer group">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-white/20 bg-white/10 text-primary-500 focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 transition-all"
                  />
                  <span className="ml-2 text-sm text-gray-300 group-hover:text-white transition-colors">
                    Remember me
                  </span>
                </label>
                <motion.a
                  href="#"
                  whileHover={{ scale: 1.05 }}
                  className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
                >
                  Forgot password?
                </motion.a>
              </div>

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={isLoading}
                whileHover={{ scale: isLoading ? 1 : 1.02 }}
                whileTap={{ scale: isLoading ? 1 : 0.98 }}
                className="w-full py-3 px-4 bg-gradient-primary text-white font-medium rounded-lg shadow-glow-md hover:shadow-glow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  'Sign In'
                )}
              </motion.button>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/20"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-transparent text-gray-400">Demo Credentials</span>
                </div>
              </div>

              {/* Demo Credentials */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="bg-white/5 border border-white/10 rounded-lg p-4 text-center"
              >
                <p className="text-xs text-gray-300 mb-1">
                  <span className="font-medium">Username:</span> admin
                </p>
                <p className="text-xs text-gray-300">
                  <span className="font-medium">Password:</span> admin123
                </p>
              </motion.div>
            </form>
          </motion.div>

          {/* Footer */}
          <motion.p
            variants={itemVariants}
            className="mt-8 text-center text-sm text-gray-400"
          >
            Don&apos;t have an account?{' '}
            <motion.a
              href="#"
              whileHover={{ scale: 1.05 }}
              className="text-primary-400 hover:text-primary-300 font-medium transition-colors"
            >
              Sign up for free
            </motion.a>
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
