import React from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';
import useAuthStore from '@/store/authStore';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative">
            <div className="h-20 w-20 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl shadow-violet-600/20 mx-auto">
              <Zap className="h-10 w-10 text-white animate-pulse" />
            </div>
            <div className="absolute inset-0 h-20 w-20 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-2xl animate-ping opacity-20" />
          </div>
          <p className="mt-4 text-slate-400">Loading your workspace...</p>
          <div className="mt-4 flex justify-center gap-1">
            <div className="h-2 w-2 bg-violet-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="h-2 w-2 bg-violet-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="h-2 w-2 bg-violet-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </motion.div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
