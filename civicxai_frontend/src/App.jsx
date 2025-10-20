import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import useAuthStore from '@/store/authStore';

// Layout
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';

// Auth Pages
import LoginNew from '@/pages/Auth/LoginNew';
import RegisterNew from '@/pages/Auth/RegisterNew';

// Main Pages
import DashboardNew from '@/pages/Dashboard/DashboardNew';
import Proposals from '@/pages/Proposals/Proposals';
import Contributors from '@/pages/Contributors/Contributors';
import Workgroups from '@/pages/Workgroups/Workgroups';
import Analytics from '@/pages/Analytics/Analytics';
import Profile from '@/pages/Profile/Profile';

function App() {
  const { initAuth } = useAuthStore();

  useEffect(() => {
    initAuth();
  }, []);

  return (
    <Router>
      <Toaster />
      
      <Routes>
        {/* Auth Routes - Standalone pages */}
        <Route path="/login" element={<LoginNew />} />
        <Route path="/register" element={<RegisterNew />} />
        
        {/* Main App Routes - Public access with optional auth */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardNew />} />
          <Route path="proposals" element={<Proposals />} />
          <Route path="contributors" element={<Contributors />} />
          <Route path="workgroups" element={<Workgroups />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
        </Route>
        
        {/* 404 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
