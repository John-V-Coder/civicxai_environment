import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle2, 
  Brain,
  Network,
  MessageCircle,
  FileText,
  ArrowRight,
  Sparkles,
  Activity
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useGateway } from '@/hooks/useGateway';

const AIGateway = () => {
  const navigate = useNavigate();
  const { 
    checkHealth,
    getMetrics,
    loading 
  } = useGateway();

  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const handleHealthCheck = async () => {
    const healthStatus = await checkHealth();
    setHealth(healthStatus);
  };

  const handleGetMetrics = async () => {
    const metricsData = await getMetrics();
    setMetrics(metricsData);
  };

  const features = [
    {
      title: 'AI Chat Assistant',
      description: 'Interactive chat for asking questions and getting AI-powered explanations about allocations and priorities',
      icon: MessageCircle,
      color: 'blue',
      route: '/ai-gateway/chat',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Allocation Request',
      description: 'Submit allocation data and PDFs for advanced AI analysis and recommendations with confidence scoring',
      icon: Brain,
      color: 'blue',
      route: '/ai-gateway/allocation',
      gradient: 'from-blue-600 to-indigo-600'
    },
    {
      title: 'Explanation Request',
      description: 'Generate citizen-friendly explanations for allocation decisions with transparency scoring',
      icon: FileText,
      color: 'purple',
      route: '/ai-gateway/explanation',
      gradient: 'from-purple-600 to-pink-600'
    }
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Network className="h-8 w-8 text-blue-500" />
            AI Gateway Hub
          </h1>
          <p className="text-slate-400 mt-1">
            Advanced AI analysis with PDF processing powered by uAgents
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleHealthCheck} disabled={loading}>
            <Activity className="h-4 w-4 mr-2" />
            Check Health
          </Button>
          <Button variant="outline" onClick={handleGetMetrics} disabled={loading}>
            <Sparkles className="h-4 w-4 mr-2" />
            Get Metrics
          </Button>
        </div>
      </div>

      {/* Health & Metrics Status */}
      {health && (
        <Alert className="bg-slate-900 border-slate-700">
          <CheckCircle2 className="h-4 w-4 text-green-500" />
          <AlertDescription className="text-slate-300">
            Gateway Status: <Badge variant="success">{health.gateway_status}</Badge>
            {health.agent_active && <span className="ml-2">• Agent Active</span>}
          </AlertDescription>
        </Alert>
      )}

      {metrics && (
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Gateway Metrics</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-slate-400 text-sm">Total Requests</p>
              <p className="text-2xl font-bold text-white">{metrics.metrics?.total_requests || 0}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Pending</p>
              <p className="text-2xl font-bold text-orange-500">{metrics.metrics?.pending_requests || 0}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-green-500">{metrics.metrics?.completed_requests || 0}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Card
              key={index}
              className="bg-slate-900 border-slate-800 hover:border-slate-600 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10 cursor-pointer group"
              onClick={() => navigate(feature.route)}
            >
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <CardTitle className="text-white flex items-center justify-between">
                  {feature.title}
                  <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-white group-hover:translate-x-1 transition-all duration-300" />
                </CardTitle>
                <CardDescription className="text-slate-400 mt-2">
                  {feature.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className={`w-full bg-gradient-to-r ${feature.gradient} hover:opacity-90 transition-opacity`}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(feature.route);
                  }}
                >
                  Open {feature.title}
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Info Section */}
      <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-400" />
            How It Works
          </CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold">1</div>
              Choose Your Tool
            </h3>
            <p className="text-slate-400 text-sm">
              Select from Chat, Allocation Request, or Explanation Request based on your needs
            </p>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 font-bold">2</div>
              Upload & Submit
            </h3>
            <p className="text-slate-400 text-sm">
              Provide your data, upload PDFs, and submit your request to the AI Gateway
            </p>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-bold">3</div>
              Get AI Insights
            </h3>
            <p className="text-slate-400 text-sm">
              Receive AI-powered recommendations, explanations, and insights in real-time
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIGateway;
