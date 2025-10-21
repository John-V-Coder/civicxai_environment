import React, { useState } from 'react';
import MetricCard from './MetricCard';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  Activity, 
  DollarSign, 
  TrendingUp,
  Zap,
  Brain,
  Network,
  RefreshCw
} from 'lucide-react';

/**
 * Demo component showing all MetricCard features
 * Demonstrates static, API-connected, and real-time metrics
 */
const MetricCardDemo = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefreshAll = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">System Metrics</h2>
          <p className="text-slate-400 mt-1">
            Real-time dashboard with AI-powered insights
          </p>
        </div>
        <Button
          onClick={handleRefreshAll}
          variant="outline"
          className="bg-slate-800 border-slate-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh All
        </Button>
      </div>

      {/* Static Metrics (No API) */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">📊 Static Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Users"
            value="2,543"
            subtitle="Active community members"
            change="+12.5%"
            icon={<Users className="h-5 w-5" />}
            color="blue"
          />
          
          <MetricCard
            title="Total Allocations"
            value="$1.2M"
            subtitle="Funds distributed"
            change="+8.3%"
            icon={<DollarSign className="h-5 w-5" />}
            color="green"
          />
          
          <MetricCard
            title="Active Proposals"
            value="48"
            subtitle="Under review"
            change="-2.1%"
            icon={<Activity className="h-5 w-5" />}
            color="purple"
          />
          
          <MetricCard
            title="Success Rate"
            value="94.2%"
            subtitle="Approved proposals"
            change="+1.8%"
            icon={<TrendingUp className="h-5 w-5" />}
            color="violet"
          />
        </div>
      </div>

      {/* AI Service Status (With API) */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🤖 AI Services Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" key={refreshKey}>
          <MetricCard
            title="Gateway Status"
            value="Online"
            subtitle="uAgents Gateway Service"
            icon={<Network className="h-5 w-5" />}
            color="green"
            metricType="gateway_health"
            showStatus={true}
            showRefresh={true}
            refreshInterval={30000} // Refresh every 30 seconds
          />
          
          <MetricCard
            title="MeTTa Engine"
            value="Online"
            subtitle="Local AI Engine"
            icon={<Brain className="h-5 w-5" />}
            color="violet"
            metricType="metta_health"
            showStatus={true}
            showRefresh={true}
            refreshInterval={30000}
          />
          
          <MetricCard
            title="Gateway Requests"
            value="156"
            subtitle="Total processed"
            change="+23"
            icon={<Zap className="h-5 w-5" />}
            color="blue"
            metricType="gateway"
            showRefresh={true}
            refreshInterval={15000} // Refresh every 15 seconds
          />
        </div>
      </div>

      {/* API Dashboard Metrics */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">📈 Dashboard Metrics (API)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" key={`api-${refreshKey}`}>
          <MetricCard
            title="API Requests"
            value="--"
            subtitle="Loading from API..."
            icon={<Activity className="h-5 w-5" />}
            color="blue"
            metricType="api"
            showRefresh={true}
          />
          
          <MetricCard
            title="Active Users"
            value="--"
            subtitle="Currently online"
            icon={<Users className="h-5 w-5" />}
            color="green"
            metricType="api"
            showRefresh={true}
          />
          
          <MetricCard
            title="Success Rate"
            value="--"
            subtitle="Request success"
            icon={<TrendingUp className="h-5 w-5" />}
            color="violet"
            metricType="api"
            showRefresh={true}
          />
          
          <MetricCard
            title="Response Time"
            value="--"
            subtitle="Average latency"
            icon={<Zap className="h-5 w-5" />}
            color="yellow"
            metricType="api"
            showRefresh={true}
          />
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="mt-8 p-6 bg-slate-800/50 border border-slate-700 rounded-lg space-y-4">
        <h3 className="text-lg font-semibold text-white">🎯 MetricCard Features</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-300">
          <div className="space-y-2">
            <p className="font-semibold text-white">Display Modes:</p>
            <ul className="space-y-1 ml-4">
              <li>✅ <strong>Static:</strong> Display provided values (no API)</li>
              <li>✅ <strong>Gateway:</strong> Fetch from uAgents Gateway</li>
              <li>✅ <strong>MeTTa:</strong> Monitor MeTTa engine health</li>
              <li>✅ <strong>API:</strong> Fetch from Django backend</li>
            </ul>
          </div>
          
          <div className="space-y-2">
            <p className="font-semibold text-white">Features:</p>
            <ul className="space-y-1 ml-4">
              <li>✅ <strong>Auto-refresh:</strong> Configurable intervals</li>
              <li>✅ <strong>Manual refresh:</strong> Click refresh button</li>
              <li>✅ <strong>Loading states:</strong> Spinner while fetching</li>
              <li>✅ <strong>Error handling:</strong> Shows error messages</li>
              <li>✅ <strong>Status badges:</strong> Online/Offline indicators</li>
              <li>✅ <strong>Trend arrows:</strong> Up/Down indicators</li>
              <li>✅ <strong>Last updated:</strong> Time since last fetch</li>
            </ul>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-700">
          <p className="text-sm text-slate-400">
            <strong>Note:</strong> Gateway and MeTTa metrics require the respective services to be running. 
            Static metrics work without any backend connection.
          </p>
        </div>
      </div>
    </div>
  );
};

export default MetricCardDemo;
