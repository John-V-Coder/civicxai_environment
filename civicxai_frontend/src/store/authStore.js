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
    if (token) {
      try {
        const response = await authAPI.checkAuthStatus();
        set({ 
          user: response.data.user, 
          isAuthenticated: true,
          isLoading: false 
        });
      } catch (error) {
        // Token is invalid, clear it
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      // No token, user is browsing as guest
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
}));

export default useAuthStore;
