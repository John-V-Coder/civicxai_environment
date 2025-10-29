import { create } from 'zustand';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  
  // Initialize auth state from localStorage
  initAuth: async () => {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    console.log('[Auth Init] Starting with token:', token ? 'exists' : 'none');
    
    if (token) {
      // Set loading state
      set({ isLoading: true });
      
      try {
        // Try to get auth status with current token
        console.log('[Auth Init] Checking auth status...');
        const response = await authAPI.checkAuthStatus();
        console.log('[Auth Init] Auth status success:', response.data.user.username);
        
        set({ 
          user: response.data.user, 
          isAuthenticated: true,
          isLoading: false 
        });
      } catch (error) {
        console.log('[Auth Init] Auth status failed:', error.response?.status);
        
        // Token might be expired, try refresh if available
        if (refreshToken && error.response?.status === 401) {
          try {
            console.log('[Auth Init] Attempting token refresh...');
            const refreshResponse = await authAPI.refreshToken(refreshToken);
            localStorage.setItem('access_token', refreshResponse.data.access);
            console.log('[Auth Init] Token refreshed successfully');
            
            // Try auth status again with new token
            const statusResponse = await authAPI.checkAuthStatus();
            console.log('[Auth Init] Auth status after refresh success:', statusResponse.data.user.username);
            
            set({ 
              user: statusResponse.data.user, 
              isAuthenticated: true,
              isLoading: false 
            });
            return;
          } catch (refreshError) {
            // Refresh also failed, clear everything
            console.error('[Auth Init] Token refresh failed:', refreshError.response?.data || refreshError.message);
          }
        }
        
        // Clear invalid tokens
        console.log('[Auth Init] Clearing tokens and logging out');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      // No token, user is browsing as guest
      console.log('[Auth Init] No token found, guest mode');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
  
  // Login
  login: async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      const { access, refresh, user } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      set({ user, isAuthenticated: true });
      toast.success(`Welcome back, ${user.username}!`);
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  },
  
  // Register
  register: async (userData) => {
    try {
      const response = await authAPI.register(userData);
      const { tokens, user } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      set({ user, isAuthenticated: true });
      toast.success('Registration successful!');
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.errors || 'Registration failed';
      toast.error(typeof message === 'object' ? JSON.stringify(message) : message);
      return { success: false, error: message };
    }
  },
  
  // Logout
  logout: async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await authAPI.logout(refreshToken);
      }
    } catch (error) {
      // Ignore logout errors
    } finally {
      // Clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Clear state
      set({ user: null, isAuthenticated: false });
      toast.success('Logged out successfully');
    }
  },
  
  // Update user profile
  updateProfile: async (profileData) => {
    try {
      const response = await authAPI.updateProfile(profileData);
      set({ user: response.data });
      toast.success('Profile updated successfully');
      return { success: true };
    } catch (error) {
      toast.error('Failed to update profile');
      return { success: false, error: error.response?.data };
    }
  },
  
  // Change password
  changePassword: async (passwordData) => {
    try {
      const response = await authAPI.changePassword(passwordData);
      
      // Update tokens if provided
      if (response.data.tokens) {
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);
      }
      
      toast.success('Password changed successfully');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to change password';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  // Request password reset
  requestPasswordReset: async (email) => {
    try {
      const response = await authAPI.requestPasswordReset(email);
      toast.success(response.data.message);
      return { success: true, data: response.data };
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to request password reset';
      toast.error(message);
      return { success: false, error: message };
    }
  },

  // Verify reset token
  verifyResetToken: async (uid, token) => {
    try {
      const response = await authAPI.verifyResetToken(uid, token);
      return { success: true, data: response.data };
    } catch (error) {
      const message = error.response?.data?.error || 'Invalid or expired reset token';
      return { success: false, error: message };
    }
  },

  // Reset password with token
  resetPassword: async (uid, token, newPassword) => {
    try {
      const response = await authAPI.resetPassword(uid, token, newPassword);
      toast.success('Password has been reset successfully');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to reset password';
      toast.error(message);
      return { success: false, error: message };
    }
  },
}));

export default useAuthStore;
