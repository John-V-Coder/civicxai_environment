import { useState, useCallback } from 'react';
import { gatewayAPI } from '@/services/api';
import { toast } from 'sonner';

/**
 * Custom hook for Gateway (uagents) AI integration
 * Provides advanced AI analysis with PDF support
 */
export const useGateway = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [polling, setPolling] = useState(false);

  /**
   * Submit allocation request with optional PDFs
   * 
   * @param {Object} data - Allocation data
   * @param {File[]} files - Optional PDF files
   * @returns {Promise<Object>} Request submission result with request_id
   */
  const requestAllocation = async (data, files = []) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Add data fields
      Object.keys(data).forEach(key => {
        if (data[key] !== null && data[key] !== undefined) {
          formData.append(key, data[key]);
        }
      });

      // Add files
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await gatewayAPI.requestAllocation(formData);
      toast.success('Allocation request submitted');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to submit allocation request';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Request AI explanation with optional PDFs
   * 
   * @param {Object} data - Explanation request data
   * @param {File[]} files - Optional supporting documents
   * @returns {Promise<Object>} Request submission result with request_id
   */
  const requestExplanation = async (data, files = []) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Add data fields
      Object.keys(data).forEach(key => {
        if (key === 'allocation_data' && typeof data[key] === 'object') {
          formData.append(key, JSON.stringify(data[key]));
        } else if (data[key] !== null && data[key] !== undefined) {
          formData.append(key, data[key]);
        }
      });

      // Add files
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await gatewayAPI.requestExplanation(formData);
      toast.success('Explanation request submitted');
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to submit explanation request';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Poll for request status
   * 
   * @param {string} requestId - Request ID to check
   * @param {Object} options - Polling options
   * @param {number} options.maxAttempts - Maximum polling attempts (default: 30)
   * @param {number} options.interval - Polling interval in ms (default: 2000)
   * @param {Function} options.onUpdate - Callback for status updates
   * @returns {Promise<Object>} Final result when completed
   */
  const pollStatus = useCallback(async (requestId, options = {}) => {
    const {
      maxAttempts = 30,
      interval = 2000,
      onUpdate = null,
    } = options;

    setPolling(true);
    setError(null);

    let attempts = 0;

    const poll = async () => {
      try {
        const response = await gatewayAPI.checkStatus(requestId);
        const { status, data } = response.data;

        // Call update callback if provided
        if (onUpdate) {
          onUpdate(response.data);
        }

        // Check if completed
        if (status === 'completed') {
          setPolling(false);
          toast.success('Request completed');
          return data;
        }

        // Check if error
        if (status === 'error') {
          setPolling(false);
          const errorMsg = data?.error || 'Request failed';
          setError(errorMsg);
          toast.error(errorMsg);
          throw new Error(errorMsg);
        }

        // Continue polling if still processing
        if (status === 'processing' || status === 'pending') {
          attempts++;
          
          if (attempts >= maxAttempts) {
            setPolling(false);
            const timeoutMsg = 'Request timed out';
            setError(timeoutMsg);
            toast.error(timeoutMsg);
            throw new Error(timeoutMsg);
          }

          // Wait and poll again
          await new Promise(resolve => setTimeout(resolve, interval));
          return poll();
        }

        // Unknown status
        throw new Error(`Unknown status: ${status}`);

      } catch (err) {
        setPolling(false);
        const errorMessage = err.message || 'Failed to check request status';
        setError(errorMessage);
        toast.error(errorMessage);
        throw err;
      }
    };

    return poll();
  }, []);

  /**
   * Check gateway health
   * 
   * @returns {Promise<Object>} Health check result
   */
  const checkHealth = async () => {
    try {
      const response = await gatewayAPI.healthCheck();
      return response.data;
    } catch (err) {
      const errorMessage = 'Gateway is not available';
      setError(errorMessage);
      return { status: 'error', message: errorMessage };
    }
  };

  /**
   * Get gateway metrics
   * 
   * @returns {Promise<Object>} Gateway metrics
   */
  const getMetrics = async () => {
    try {
      const response = await gatewayAPI.getMetrics();
      return response.data;
    } catch (err) {
      const errorMessage = 'Failed to fetch gateway metrics';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    }
  };

  return {
    requestAllocation,
    requestExplanation,
    pollStatus,
    checkHealth,
    getMetrics,
    loading,
    polling,
    error,
  };
};

export default useGateway;
