import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from 'sonner';
import { Toaster as HotToast } from 'react-hot-toast';
import useAuthStore from '@/store/authStore';

// Layout
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';

// Auth Pages
import Login from '@/pages/Auth/Login';
import Register from '@/pages/Auth/Register';
import ForgotPassword from '@/pages/Auth/ForgotPassword';
import ResetPassword from '@/pages/Auth/ResetPassword';

// Main Pages
import Dashboard from '@/pages/Dashboard/Dashboard';
import Proposals from '@/pages/Proposals/Proposals';
import Contributors from '@/pages/Contributors/Contributors';
import Workgroups from '@/pages/Workgroups/Workgroups';
import Analytics from '@/pages/Analytics/Analytics';
import Profile from '@/pages/Profile/Profile';

// AI Pages
import AIGateway from '@/pages/AIgateway/AIGateway';
import AIGatewayChat from '@/components/AIgateway/AIGatewayChat';
import AllocationRequest from '@/components/AIgateway/AllocationRequest';
import ExplanationRequest from '@/components/AIgateway/ExplanationRequest';
import PriorityCalculator from '@/components/MeTTa/PriorityCalculator';
import DataSources from '@/pages/DataSources/DataSources';

function App() {
  const { initAuth } = useAuthStore();

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      {/* Toasters for different notification systems */}
      <Toaster />
      <Sonner position="top-right" expand={true} richColors closeButton theme="dark" />
      <HotToast position="top-center" />
      
      <Routes>
        {/* Auth Routes - Standalone pages */}
        <Route path="/login" element={<Login/>} />
        <Route path="/register" element={<Register/>} />
        <Route path="/forgot-password" element={<ForgotPassword/>} />
        <Route path="/reset-password/:uid/:token" element={<ResetPassword/>} />
        
        {/* Main App Routes - Public access with optional auth */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="proposals" element={<Proposals />} />
          <Route path="contributors" element={<Contributors />} />
          <Route path="workgroups" element={<Workgroups />} />
          <Route path="analytics" element={<Analytics />} />
          
          {/* AI Features */}
          <Route path="ai-gateway" element={<AIGateway />} />
          <Route path="ai-gateway/chat" element={<AIGatewayChat />} />
          <Route path="ai-gateway/chat/:id" element={<AIGatewayChat />} />
          <Route path="ai-gateway/allocation" element={<AllocationRequest />} />
          <Route path="ai-gateway/explanation" element={<ExplanationRequest />} />
          <Route path="calculator" element={<PriorityCalculator />} />
          {/* Legacy route - redirects to new unified chat */}
          <Route path="proposal-chat/:id" element={<AIGatewayChat />} />
          
          {/* Admin Only - Data Sources */}
          <Route path="data-sources" element={
            <ProtectedRoute requireAdmin={true}>
              <DataSources />
            </ProtectedRoute>
          } />
          
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
