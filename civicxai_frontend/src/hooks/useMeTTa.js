import { useState } from 'react';
import { mettaAPI } from '@/services/api';
import { toast } from 'sonner';

/**
 * Custom hook for MeTTa AI Engine integration
 * Provides fast, local priority calculations and explanations
 */
export const useMeTTa = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Calculate priority score using MeTTa engine
   * 
   * @param {Object} data - Allocation data
   * @param {number} data.poverty_index - Poverty index (0-1)
   * @param {number} data.project_impact - Project impact score (0-1)
   * @param {number} data.deforestation - Deforestation level (0-1)
   * @param {number} data.corruption_risk - Corruption risk (0-1)
   * @returns {Promise<Object>} Priority calculation result
   */
  const calculatePriority = async (data) => {
    setLoading(true);
    setError(null);

    try {
      const response = await mettaAPI.calculatePriority(data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to calculate priority';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Generate explanation for allocation decision
   * 
   * @param {Object} data - Explanation request data
   * @param {string} data.region_id - Region identifier
   * @param {Object} data.allocation_data - Allocation details
   * @param {string} data.language - Language code (default: 'en')
   * @returns {Promise<Object>} Explanation result
   */
  const generateExplanation = async (data) => {
    setLoading(true);
    setError(null);

    try {
      const response = await mettaAPI.generateExplanation(data);
      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Failed to generate explanation';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check MeTTa engine health status
   * 
   * @returns {Promise<Object>} Health check result
   */
  const checkHealth = async () => {
    try {
      const response = await mettaAPI.healthCheck();
      return response.data;
    } catch (err) {
      const errorMessage = 'MeTTa engine is not available';
      setError(errorMessage);
      return { status: 'error', message: errorMessage };
    }
  };

  return {
    calculatePriority,
    generateExplanation,
    checkHealth,
    loading,
    error,
  };
};

export default useMeTTa;
