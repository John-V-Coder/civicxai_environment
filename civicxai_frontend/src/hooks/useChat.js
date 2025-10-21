import { useState, useCallback } from 'react';
import { chatAPI } from '@/services/api';
import { toast } from 'sonner';

/**
 * Custom hook for AI Chat
 * Sends messages to backend and receives AI responses
 */
export const useChat = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Send a message to the AI chat backend
   * 
   * @param {string} message - The user's message
   * @param {File[]} files - Optional file attachments
   * @returns {Promise<Object>} AI response
   */
  const sendMessage = useCallback(async (message, files = null) => {
    if (!message || !message.trim()) {
      const errorMsg = 'Message cannot be empty';
      setError(errorMsg);
      toast.error(errorMsg);
      throw new Error(errorMsg);
    }

    setLoading(true);
    setError(null);

    try {
      const response = await chatAPI.sendMessage(message, files);
      const data = response.data;

      if (!data.success) {
        throw new Error(data.error || 'Failed to get response');
      }

      return {
        content: data.message,
        intent: data.intent,
        filesAttached: data.files_attached || 0
      };
    } catch (err) {
      const errorMessage = err.response?.data?.error 
        || err.response?.data?.details
        || err.message 
        || 'Failed to send message';
      
      setError(errorMessage);
      toast.error('Chat error: ' + errorMessage);
      
      // Return error response for display
      return {
        content: err.response?.data?.message || 'Sorry, I encountered an error processing your request. Please try again.',
        isError: true,
        error: errorMessage
      };
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    sendMessage,
    loading,
    error,
    clearError,
  };
};

export default useChat;
