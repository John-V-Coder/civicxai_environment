import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  MapPin,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle2,
  Clock,
  Brain,
  FileText,
  ChevronRight,
  Sparkles,
  Target,
  Activity
} from 'lucide-react';

/**
 * Beautiful card for displaying allocation requests from AI Gateway
 * Shows region name prominently with all metrics and AI analysis
 */
const AllocationRequestCard = ({ 
  request,
  onViewDetails,
  compact = false
}) => {
  // Status configurations
  const statusConfig = {
    'pending': {
      color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      icon: Clock,
      label: 'Pending'
    },
    'processing': {
      color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      icon: Activity,
      label: 'Processing'
    },
    'analyzed': {
      color: 'bg-green-500/20 text-green-400 border-green-500/30',
      icon: CheckCircle2,
      label: 'Analyzed'
    },
    'approved': {
      color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      icon: CheckCircle2,
      label: 'Approved'
    },
    'rejected': {
      color: 'bg-red-500/20 text-red-400 border-red-500/30',
      icon: AlertCircle,
      label: 'Rejected'
    }
  };

  const currentStatus = statusConfig[request.status] || statusConfig['pending'];
  const StatusIcon = currentStatus.icon;

  // Priority level colors
  const priorityColors = {
    'CRITICAL': 'text-red-400 bg-red-500/20',
    'HIGH': 'text-orange-400 bg-orange-500/20',
    'MEDIUM': 'text-yellow-400 bg-yellow-500/20',
    'LOW': 'text-blue-400 bg-blue-500/20',
  };

  const getPriorityColor = (level) => {
    if (!level) return 'text-slate-400 bg-slate-500/20';
    const upperLevel = level.toUpperCase();
    return priorityColors[upperLevel] || 'text-slate-400 bg-slate-500/20';
  };

  // Format metrics for display
  const metrics = request.metrics || {};
  const metricsDisplay = [
    { label: 'Poverty', value: metrics.poverty_index, icon: TrendingDown, color: 'text-red-400' },
    { label: 'Impact', value: metrics.project_impact, icon: Target, color: 'text-green-400' },
    { label: 'Environment', value: metrics.environmental_score, icon: Activity, color: 'text-blue-400' },
    { label: 'Risk', value: metrics.corruption_risk, icon: AlertCircle, color: 'text-orange-400' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className="w-full"
    >
      <Card 
        className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-slate-700 hover:border-violet-500/50 transition-all cursor-pointer group backdrop-blur-sm"
        onClick={() => onViewDetails && onViewDetails(request)}
      >
        <CardHeader className="pb-3">
          {/* Header with Region Name and Status */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2.5 rounded-lg bg-violet-500/20 border border-violet-500/30 group-hover:bg-violet-500/30 transition-colors">
                <MapPin className="h-5 w-5 text-violet-400" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-white text-xl font-bold group-hover:text-violet-400 transition-colors flex items-center gap-2">
                  {request.region_name || request.region_id}
                  {request.files_attached > 0 && (
                    <Badge variant="outline" className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">
                      <FileText className="h-3 w-3 mr-1" />
                      {request.files_attached} files
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription className="text-slate-400 text-sm mt-0.5">
                  Region ID: {request.region_id}
                </CardDescription>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-2">
              <Badge variant="outline" className={currentStatus.color}>
                <StatusIcon className="w-3 h-3 mr-1" />
                {currentStatus.label}
              </Badge>
              <ChevronRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 group-hover:text-violet-400 transition-all" />
            </div>
          </div>

          {/* Priority Level Badge (if analyzed) */}
          {request.priority_level && (
            <div className="flex items-center gap-2 mt-2">
              <Badge className={`${getPriorityColor(request.priority_level)} border-0 font-semibold text-sm px-3 py-1`}>
                <Sparkles className="w-3 h-3 mr-1" />
                {request.priority_level} Priority
              </Badge>
              {request.confidence_score && (
                <span className="text-xs text-slate-400">
                  Confidence: {(request.confidence_score * 100).toFixed(0)}%
                </span>
              )}
            </div>
          )}
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-800">
            {metricsDisplay.map((metric, idx) => {
              const MetricIcon = metric.icon;
              const value = metric.value !== undefined ? metric.value : 0;
              const percentage = (value * 100).toFixed(0);
              
              return (
                <div key={idx} className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-md">
                  <div className="flex flex-col flex-1">
                    <div className="flex items-center gap-1.5 mb-1">
                      <MetricIcon className={`w-3.5 h-3.5 ${metric.color}`} />
                      <span className="text-xs text-slate-400 font-medium">{metric.label}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={percentage} 
                        className="h-1.5 flex-1"
                      />
                      <span className="text-sm font-bold text-white min-w-[3ch] text-right">
                        {percentage}%
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* AI Recommendation (if available) */}
          {request.recommended_allocation_percentage !== null && request.recommended_allocation_percentage !== undefined && (
            <div className="p-4 bg-gradient-to-r from-violet-500/10 to-blue-500/10 rounded-lg border border-violet-500/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-violet-400" />
                  <span className="text-sm font-medium text-slate-300">AI Recommendation</span>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-violet-400">
                    {request.recommended_allocation_percentage.toFixed(1)}%
                  </p>
                  <p className="text-xs text-slate-400">allocation</p>
                </div>
              </div>
            </div>
          )}

          {/* Key Findings (if available) */}
          {request.key_findings && request.key_findings.length > 0 && !compact && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Key Findings
              </p>
              <div className="space-y-1">
                {request.key_findings.slice(0, 2).map((finding, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-400 bg-slate-800/30 p-2 rounded">
                    <span className="text-violet-400 font-bold">•</span>
                    <span className="flex-1">{finding}</span>
                  </div>
                ))}
                {request.key_findings.length > 2 && (
                  <p className="text-xs text-slate-500 italic">
                    +{request.key_findings.length - 2} more findings
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Notes (if available) */}
          {request.notes && !compact && (
            <div className="pt-2 border-t border-slate-800">
              <p className="text-xs text-slate-500 line-clamp-2">
                {request.notes}
              </p>
            </div>
          )}

          {/* Timestamp */}
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(request.created_at).toLocaleDateString()} at {new Date(request.created_at).toLocaleTimeString()}
            </span>
            {request.analyzed_at && (
              <span className="flex items-center gap-1 text-green-400">
                <CheckCircle2 className="w-3 h-3" />
                Analyzed
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default AllocationRequestCard;
