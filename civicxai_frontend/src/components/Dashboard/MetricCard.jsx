import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  RefreshCw, 
  Activity,
  Loader2,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useGateway } from '@/hooks/useGateway';
import { useMeTTa } from '@/hooks/useMeTTa';
import { dashboardAPI } from '@/services/api';
import { toast } from 'sonner';

/**
 * Enhanced MetricCard with API integration and real-time updates
 * Supports data fetching, refresh, and AI-powered insights
 */
const MetricCard = ({ 
  title, 
  value: initialValue, 
  subtitle, 
  change: initialChange, 
  icon, 
  color = 'blue',
  metricType,           // Type of metric: 'gateway', 'metta', 'api'
  endpoint,             // API endpoint to fetch data
  refreshInterval,      // Auto-refresh interval in ms
  showRefresh = true,   // Show refresh button
  showStatus = false,   // Show connection status
  onRefresh,            // Callback after refresh
  className
}) => {
  const [value, setValue] = useState(initialValue);
  const [change, setChange] = useState(initialChange);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  const { getMetrics: getGatewayMetrics, checkHealth: checkGatewayHealth } = useGateway();
  const { checkHealth: checkMeTTaHealth } = useMeTTa();
  const colorClasses = {
    blue: 'bg-blue-500/20 border-blue-500/30',
    green: 'bg-green-500/20 border-green-500/30',
    yellow: 'bg-yellow-500/20 border-yellow-500/30',
    purple: 'bg-purple-500/20 border-purple-500/30',
    violet: 'bg-violet-500/20 border-violet-500/30',
    red: 'bg-red-500/20 border-red-500/30',
  };

  const iconColorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    purple: 'text-purple-400',
    violet: 'text-violet-400',
    red: 'text-red-400',
  };

  /**
   * Fetch data from API based on metric type
   */
  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      let result;

      switch (metricType) {
        case 'gateway':
          result = await getGatewayMetrics();
          break;
        
        case 'gateway_health':
          result = await checkGatewayHealth();
          break;
        
        case 'metta_health':
          result = await checkMeTTaHealth();
          break;
        
        case 'api':
          if (endpoint) {
            const response = await dashboardAPI.getMetrics();
            result = response.data;
          }
          break;
        
        default:
          // No auto-fetch, use provided values
          return;
      }

      // Update values from result
      if (result) {
        // Extract relevant metric from result
        const newValue = extractMetricValue(result, title);
        if (newValue !== undefined) {
          setValue(newValue);
        }
        setLastUpdated(new Date());
        
        if (onRefresh) {
          onRefresh(result);
        }
      }
    } catch (err) {
      console.error('Failed to fetch metric data:', err);
      setError(err.message || 'Failed to fetch data');
      toast.error(`Failed to update ${title}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Extract specific metric value from API response
   */
  const extractMetricValue = (data, metricTitle) => {
    // Add logic to extract specific values based on title
    if (!data) return undefined;
    
    // Example extractions
    if (metricTitle.toLowerCase().includes('request')) {
      return data.total_requests || data.requests || undefined;
    }
    if (metricTitle.toLowerCase().includes('success')) {
      return data.success_rate || data.successful_requests || undefined;
    }
    if (metricTitle.toLowerCase().includes('active')) {
      return data.active_users || data.agent_active || undefined;
    }
    
    return undefined;
  };

  /**
   * Manual refresh handler
   */
  const handleRefresh = async () => {
    await fetchData();
    toast.success(`${title} updated`);
  };

  // Auto-refresh effect
  useEffect(() => {
    if (metricType && metricType !== 'static') {
      fetchData();
    }

    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [metricType, refreshInterval]);

  const getTrendIcon = () => {
    if (change?.includes('+') && !change.includes('+0')) {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else if (change?.includes('-') && !change.includes('-0')) {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      <Card className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-all h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-lg ${colorClasses[color]}`}>
                {loading ? (
                  <Loader2 className={`h-5 w-5 ${iconColorClasses[color]} animate-spin`} />
                ) : error ? (
                  <AlertCircle className="h-5 w-5 text-red-400" />
                ) : (
                  <div className={iconColorClasses[color]}>{icon}</div>
                )}
              </div>
              <div className="flex-1">
                <CardTitle className="text-sm text-slate-400 font-normal">
                  {title}
                </CardTitle>
              </div>
            </div>
            
            {/* Status and Actions */}
            <div className="flex items-center gap-2">
              {showStatus && (
                <Badge 
                  variant="outline" 
                  className={error ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-green-500/20 text-green-400 border-green-500/30'}
                >
                  {error ? (
                    <AlertCircle className="w-3 h-3 mr-1" />
                  ) : (
                    <CheckCircle className="w-3 h-3 mr-1" />
                  )}
                  {error ? 'Error' : 'Online'}
                </Badge>
              )}
              
              {showRefresh && metricType && metricType !== 'static' && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleRefresh}
                  disabled={loading}
                  className="h-8 w-8 text-slate-400 hover:text-white hover:bg-slate-700"
                >
                  <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-2">
          {/* Value Display */}
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-white">
              {loading ? (
                <span className="text-slate-500">--</span>
              ) : error ? (
                <span className="text-red-400 text-lg">Error</span>
              ) : (
                value
              )}
            </p>
            
            {/* Trend Indicator */}
            {change && !loading && !error && (
              <div className="flex items-center gap-1">
                {getTrendIcon()}
                <span className="text-sm text-slate-400">{change}</span>
              </div>
            )}
          </div>
          
          {/* Subtitle */}
          {subtitle && (
            <p className="text-xs text-slate-500">
              {subtitle}
            </p>
          )}
          
          {/* Last Updated */}
          {lastUpdated && !loading && (
            <p className="text-xs text-slate-600 flex items-center gap-1">
              <Activity className="w-3 h-3" />
              Updated {formatLastUpdated(lastUpdated)}
            </p>
          )}
          
          {/* Error Message */}
          {error && (
            <p className="text-xs text-red-400 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              {error}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

/**
 * Format last updated time
 */
const formatLastUpdated = (date) => {
  const now = new Date();
  const diff = Math.floor((now - date) / 1000); // seconds
  
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return date.toLocaleDateString();
};

export default MetricCard;
